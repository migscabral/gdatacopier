#!/usr/bin/env python

"""

	gcp
	GDataCopier, http://gdatacopier.googlecode.com/
	
	Copyright 2010 Eternity Technologies.
	Distributed under the terms and conditions of the GNU/GPL v3
	
	GDataCopier is free software and comes with absolutely NO WARRANTY. Use 
	of this software is completely at YOUR OWN RISK.
	
	Version 2.2.0
	
"""

__version__ = "2.2.0"
__author__  = "Devraj Mukherjee, Matteo Canato"

"""
	Imports the required modules 
"""
try:
	from optparse import OptionParser
        import ConfigParser
	import datetime
	import sys
	import os
	import re
	import string
	import signal
	import time
	import stat
	import getpass
	import base64
        from gdatacopier import helpers
        from gdatacopier.exceptions import *
except:
	print "gcp failed to find some basic python modules, please validate the environment"
	exit(1)

try:
        import gdata
        import gdata.data
	import gdata.spreadsheet.service
        import gdata.docs.service
        import gdata.gauth
        import gdata.docs.data
        import gdata.docs.client
except:
	print "gcp %s requires gdata-python-client v2.0+, downloadable from Google at" % __version__
	print "<http://code.google.com/p/gdata-python-client/>"
	exit(1)

try:
        # Add logs functionality
        import logging
        LOG = logging.getLogger(helpers.LOGGER_NAME)
except:
	print "gcp failed to find logging python modules, please validate the environment"
	exit(1)

"""
    Default values read from configuration file
"""
defaults = {
    'configdir' : '~/.gdatacopier/',
    'config' : 'gdatacopierrc',
}

"""
    The following fields are update when oauth 2 legged is used and values are
    read from a configuration file
"""
oauth_values = {
    'consumer_key'    : None,
    'consumer_secret' : None,
}

"""
	Methods
"""
def signal_handler(signal, frame):
    LOG.debug("\n[Interrupted] Bye Bye!")
    sys.exit(2)

"""
    Setup the global (root, basic) configuration for logging.
"""
def setup_logger(options):
    msg_format = '%(message)s'
    if options.debug:
        level = logging.DEBUG
        msg_format = '%(levelname)s:%(name)s:%(message)s'
    elif options.verbose:
        level = logging.DEBUG
    elif options.silent:
        level = logging.ERROR
    else:
        level = logging.INFO
    # basicConfig does nothing if it's been called before
    # (e.g. in run_interactive loop)
    # TODO insert LOG file path
    logging.basicConfig(level=level, format=msg_format)
    # Redundant for single-runs, but necessary for run_interactive.
    LOG.setLevel(level)
    # XXX: Inappropriate location (style-wise).
    if options.debug:
        LOG.debug('Gdata will be imported from ' + gdata.__file__)

def export_documents(source_path, target_path, options):
        username, document_path = source_path.split(':')

        if not os.path.isdir(target_path):
            LOG.error("%s does not exists or you don't have write privelleges" % target_path)
            sys.exit(2)

	if not helpers.is_email(username):
            LOG.error("Usernames must be provided as your full Gmail address, hosted domains included.")
            sys.exit(2)

	docs_type = None
	folder_name = None
	name_filter = None
	
	doc_param_parts = document_path.split('/')
	
	if len(doc_param_parts) > 1 and not (doc_param_parts[1] == '' or doc_param_parts[1] == '*'):
		docs_type = doc_param_parts[1]
		
	if len(doc_param_parts) > 2 and not (doc_param_parts[2] == '' or doc_param_parts[2] == '*'):
		folder_name = doc_param_parts[2]

	if len(doc_param_parts) > 3 and not (doc_param_parts[3] == '' or doc_param_parts[3] == '*'):
			name_filter = doc_param_parts[3]
			
	# Get a handle to the document list service
        LOG.info("Logging into Google server as %s" % (username))
        gd_client = gdata.docs.client.DocsClient(source='etk-gdatacopier-v2')
        """
            NOTE: starting Jan 2011 Google Document List API will support only
            SSL connection (spreedsheets aren't under SSL yet)
            http://code.google.com/intl/it/apis/documents/forum.html?place=topic%2Fgoogle-documents-list-api%2FaEDGbZMul9s%2Fdiscussion
        """
        gd_client.ssl = True                # Force all API requests through HTTPS
        gd_client.api_version = '3.0'       # Force API version 3.0

        if (options.debug):
            gd_client.http_client.debug = True  # Set to True for debugging HTTP requests
        else:
            gd_client.http_client.debug = False

	try:
            # Authenticate to the document service'
            helpers.login(username, oauth_values, options, gd_client)
            
            # Spreadsheet export requires separate authentication token is the
            # logged in with standard login
            if options.standard_login:
                spreadsheets_client = gdata.spreadsheet.service.SpreadsheetsService()
                spreadsheets_client.ClientLogin(username, options.password)

            # If the user provided a folder type then add this here
            if folder_name == None or folder_name == "all":
                document_query = gdata.docs.service.DocumentQuery(feed=helpers.BASE_FEED)
            else:
                projection_folder = "full" + helpers.get_folder_id_from_name(folder_name, gd_client)
                document_query = gdata.docs.service.DocumentQuery(feed=helpers.BASE_FEED, projection=projection_folder)

            helpers.add_category_filter(document_query, docs_type)
            helpers.add_title_match_filter(document_query, name_filter)

            # We must keep track of the docs token
            if options.standard_login:
                docs_auth_token     = gd_client.auth_token
                sheets_auth_token   = spreadsheets_client.GetClientLoginToken()

            LOG.info("Fetching document list feeds from Google servers for %s" % (username))
            LOG.debug("Sending a request for the URI: %s" % document_query.ToUri())

            docs = gd_client.GetEverything(document_query.ToUri())  # makes multiple HTTP requests.
		
            # Counters
            success_counter     = 0
            failed_counter      = 0
            unchanged_counter   = 0
            service_error_counter = 0

            for entry in docs:
                    export_extension = helpers.get_appropriate_extension(entry, docs_type, options.format)

                    # Construct a file name for the export
                    export_filename = None
                    if not options.create_user_dir:
                            export_filename = target_path + "/" + helpers.sanatize_filename(entry.title.text)
                    else:
                            if not os.path.isdir(target_path + "/" + entry.author[0].name.text):
                                    os.mkdir(target_path + "/" + entry.author[0].name.text)
                            export_filename = target_path + "/" + entry.author[0].name.text + "/" + helpers.sanatize_filename(entry.title.text)

                    # Add a Base64 hash of the resource id if the user requires it
                    if options.add_document_id:
                            export_filename = export_filename + "-" + base64.b64encode(entry.resourceId.text)
                    
                    # For arbitrary files (extension == None) check if they
                    # already have an extension and preserve it
                    if export_extension != None:
                            export_filename = export_filename + "." + export_extension

                    # Tell the user something about what we are doing
                    print "%-30s -d-> %-50s" % (entry.resource_id.text[0:30], export_filename[-50:])

                    # Change authentication token if we are exporting spreadheets with standard login
                    if options.standard_login and entry.GetDocumentType() == "spreadsheet":
                            gd_client.auth_token = gdata.gauth.ClientLoginToken(sheets_auth_token)

                    # Thanks to http://stackoverflow.com/questions/127803/how-to-parse-iso-formatted-date-in-python
                    # we are use regular expression to parse RFC3389
                    updated_time = datetime.datetime(*map(int, re.split('[^\d]', entry.updated.text)[:-1]))
                    remote_access_time = time.mktime(updated_time.timetuple())

                    # If not force overwrite check if file exists and ask if we should overwrite
                    if not options.overwrite and os.path.isfile(export_filename):
                            user_answer = ""
                            while not user_answer == "NO" and not user_answer.upper() == "YES":
                                    user_answer = raw_input("overwrite (yes/NO): ")
                                    if user_answer == "": user_answer = "NO"
                            if user_answer == "NO": continue

                    # If update then check to see if the datestamp has changed or ignore
                    if options.update and os.path.isfile(export_filename):
                            file_modified_time = os.stat(export_filename).st_mtime
                            # If local file is older than remote file then download
                            if file_modified_time >= remote_access_time:
                                    LOG.info("UNCHANGED")
                                    unchanged_counter = unchanged_counter + 1
                                    continue
                    try:
                            # Use Export() method when downloading sheets, docs and draws in a known format
                            if helpers.is_a_known_extension(export_extension) \
                                and (entry.GetDocumentType() == 'draw' or entry.GetDocumentType() == 'spreadsheet' \
                                or entry.GetDocumentType() == 'document' or entry.GetDocumentType() == 'presentation'):
                                    gd_client.Export(entry, export_filename)
                            else:
                                    # We use the Download() function for PDFs and
                                    # arbitrary files (zip, mov, tar, etc.)
                                    gd_client.Download(entry, export_filename)
                            os.utime(export_filename, (remote_access_time, remote_access_time))
                            success_counter = success_counter + 1
                            LOG.info("OK")
                    except gdata.service.Error:
                            LOG.error("SERVICE ERROR")
                            service_error_counter = service_error_counter + 1
                    except:
                            LOG.error("FAILED")
                            failed_counter = failed_counter + 1

                    # Restore original Google Docs client login token
                    if options.standard_login:
                        gd_client.auth_token = docs_auth_token

            print "\n%i successful, %i unchanged, %i service error, %i failed" % (success_counter, unchanged_counter, service_error_counter, failed_counter)

	except gdata.client.BadAuthentication:
		LOG.error("Standard login failed. Bad Password!")
		sys.exit(2)
	except gdata.client.CaptchaChallenge:
		LOG.error("Captcha required, please login using the web interface and try again.")
		sys.exit(2)
	except gdata.service.BadAuthentication:
		LOG.error("Standard login for spreadsheets service failed. Bad Password!")
		sys.exit(2)
	except gdata.client.Unauthorized:
		LOG.error("Unauthorized!\nCheck the OAuth key/secret stored into gdatacopierrc file.")
		sys.exit(2)
	except gdata.client.Error, e:
		LOG.error("OAuth login failed. Reason: %s \n" % e[0]['reason'])
		sys.exit(2)
        except GDataCopierFolderNotExists, e:
                LOG.error('Error: %s\n' % e)
                sys.exit(2)
	except Exception, e:
		LOG.error("Failed. %s" % e)
		sys.exit(2)
	
def import_documents(source_path, target_path, options):
	upload_filenames = []
	username, document_path = target_path.split(':')

	if not helpers.is_email(username):
            LOG.error("Usernames must be provided as your full Gmail address, hosted domains included.")
            sys.exit(2)

        folder_name = None
        doc_param_parts = document_path.split('/')

        if len(doc_param_parts) > 1 and not doc_param_parts[1] == '':
                folder_name = doc_param_parts[1]
	
	# File or Directory add the names of the uploads to a list 
	if os.path.isdir(source_path):
		dir_list = os.listdir(source_path)
		for file_name in dir_list:
			if not file_name[:1] == ".": upload_filenames.append(source_path + "/" + file_name)
	elif os.path.isfile(source_path):
		upload_filenames.append(source_path)
        else:
                LOG.error("The folder/file %s not exists!" % source_path)
                sys.exit(2)

	# Get a handle to the document list service
        LOG.info("Logging into Google server as %s" % (username))
        gd_client = gdata.docs.client.DocsClient(source='etk-gdatacopier-v2')
        """
            NOTE: starting Jan 2011 Google Document List API will support only
            SSL connection (spreedsheets aren't under SSL yet)
            http://code.google.com/intl/it/apis/documents/forum.html?place=topic%2Fgoogle-documents-list-api%2FaEDGbZMul9s%2Fdiscussion
        """
        gd_client.ssl = True                # Force all API requests through HTTPS
        gd_client.api_version = '3.0'       # Force API version 3.0

        if (options.debug):
            gd_client.http_client.debug = True  # Set to True for debugging HTTP requests
        else:
            gd_client.http_client.debug = False

	try:
            # Authenticate to the document service'
            helpers.login(username, oauth_values, options, gd_client)

            LOG.info("Fetching document list feeds from Google servers for %s" % (username))

            # The folder where to upload must be a gdata.docs.data.DocsEntry object
            # see http://code.google.com/intl/it/apis/documents/docs/3.0/developers_guide_python.html#UploadDocToAFolder
            remote_folder = helpers.get_folder_entry(gd_client, folder_name)

            # Counters
            notallowed_counter = 0
            failed_counter = 0
            dup_name_counter = 0
            updated_counter = 0
            success_counter = 0

            # Upload allowed documents to the Google system
            for file_name in upload_filenames:

                    extension = (file_name[len(file_name) - 4:]).upper().replace(".", "")

                    LOG.info("%-50s -u-> " % os.path.basename(file_name)[-50:])

                    """
                        Check to see that we are allowed to upload this document
                        NOTE: Arbitrary files upload is only available to \
                        Google Apps for Business accounts.
                        http://code.google.com/intl/it/apis/documents/docs/3.0/developers_guide_python.html#UploadingArbitraryFileTypes
                    """
                    if not extension in gdata.docs.data.MIMETYPES:
                            LOG.error("FILETYPE NOT ALLOWED (%s)" % extension)
                            notallowed_counter = notallowed_counter + 1
                            continue

                    mime_type = gdata.docs.data.MIMETYPES[extension]
                    media_source = gdata.data.MediaSource(file_path=file_name, content_type=mime_type)

                    entry = None
                    existing_resource = helpers.get_document_resource(gd_client, remote_folder, file_name)

                    try:
                            if existing_resource == None:
                                    if remote_folder == None:
                                            entry = gd_client.Upload(media_source, helpers.filename_from_path(file_name))
                                    else:
                                            entry = gd_client.Upload(media_source, helpers.filename_from_path(file_name), folder_or_uri=remote_folder)
                            else:
                                    if not options.overwrite:
                                            user_answer = ""
                                            while not user_answer == "NO" and not user_answer.upper() == "YES":
                                                    user_answer = raw_input("overwrite (yes/NO): ")
                                                    if user_answer == "": user_answer = "NO"
                                            if user_answer == "NO":
                                                    raise GDataCopierDuplicateDocumentNameFound
                                                    continue

                                    entry = gd_client.Update(existing_resource, media_source=media_source)
                                    updated_counter = updated_counter + 1

                            success_counter = success_counter + 1

                            """
                                    Print new resource id or indicate that the document has been updated
                            """
                            if existing_resource == None and not entry == None:
                                LOG.info(entry.resource_id.text)
                            else:
                                LOG.info("UPDATED %s" % helpers.filename_from_path(file_name))

                    except GDataCopierDuplicateDocumentNameFound:
                            LOG.error("DUPLICATE NAME %s" % helpers.filename_from_path(file_name))
                            dup_name_counter = dup_name_counter + 1
                    except Exception, e:
                            LOG.error("FAILED reason %s" % e)
                            failed_counter = failed_counter + 1

            print "\n%i successful, %i not allowed, %i failed, %i updated, %i duplicate names" % (success_counter, notallowed_counter, failed_counter, updated_counter, dup_name_counter)
	except gdata.client.BadAuthentication:
		LOG.error("Standard login failed. Bad Password!")
		sys.exit(2)
	except gdata.client.CaptchaChallenge:
		LOG.error("Captcha required, please login using the web interface and try again.")
		sys.exit(2)
	except gdata.service.BadAuthentication:
		LOG.error("Standard login for spreadsheets service failed. Bad Password!")
		sys.exit(2)
	except gdata.client.Unauthorized:
		LOG.error("Unauthorized!\nCheck the OAuth key/secret stored into gdatacopierrc file.")
		sys.exit(2)
	except gdata.client.Error, e:
		LOG.error("OAuth login failed. Reason: %s \n" % e[0]['reason'])
		sys.exit(2)
        except GDataCopierFolderNotExists, e:
                LOG.error('Error: %s\n' % e)
                sys.exit(2)
	except Exception, e:
		LOG.error("Failed. %s" % e)
		sys.exit(2)
	
def parse_user_input():
	usage = "usage: %prog [options] username@domain.com:/[doctype]/[folder]/Title* /home/directory"
	parser = OptionParser(usage)

	parser.add_option('-s', '--silent',
                            action = 'store_true',
                            dest = 'silent',
                            default = False,
                            help = 'decreases verbosity, supresses all messages \
                                    but summaries and critical errors')
	parser.add_option('-u', '--update',
                            action = 'store_true',
                            dest = 'update',
                            default = False,
                            help = 'only downloads files that have changed on \
                                    the Google document servers, remote time stamps \
                                    are replicated')
	parser.add_option('-o', '--overwrite',
                            action = 'store_true',
                            dest = 'overwrite',
                            default = False,
                            help = 'overwrite files if they already exists on the \
                                    local disk (download only option)')
	parser.add_option('-i', '--doc-id',
                            action = 'store_true',
                            dest = 'add_document_id',
                            default = False,
                            help = 'appends document id at the end of the file name, \
                                    use this if you have multiple documents with \
                                    the same name')
	parser.add_option('-c', '--create-user-dir',
                            action = 'store_true',
                            dest = 'create_user_dir',
                            default = False,
                            help = 'copies documents to a sub-directory by owner \
                                    name, if the directory doesn\'t exist it will \
                                    be created')
	parser.add_option('-p', '--password',
                            dest = 'password',
                            help = 'password to login to Google document servers, \
                                    use with extreme caution, may be logged')
	parser.add_option('', '--password-file',
                            dest = 'password_file',
                            help = 'password may alternatviely be read from a file, \
                                    provide full path of file')
	parser.add_option('-f', '--format',
                            default = 'oo',
                            help = 'file format to export documents to, ensure \
                                    to use default if exporting mixed types (download \
                                    only option)')
        parser.add_option('--configdir',
                            dest='configdir',
                            action='store',
                            default=defaults['configdir'],
                            help='look in DIR for config/data files', metavar='DIR')
        parser.add_option('--config',
                            dest='config',
                            action='append',
                            default=defaults['config'],
                            help='load configuration from FILE',
                            metavar='FILE')
        parser.add_option('--debug',
                            dest='debug',
                            action='store_true',
                            default = False,
                            help=('Enable all debugging output, including HTTP data'))
        parser.add_option('--verbose',
                            dest='verbose',
                            action='store_true',
                            default = False,
                            help='Print all messages.')
	parser.add_option('--standard_login',
                            action = 'store_true',
                            dest = 'standard_login',
                            default = False,
                            help = 'use authentication with standard login')
	parser.add_option('--two_legged_oauth',
                            action = 'store_true',
                            dest = 'two_legged_oauth',
                            default = False,
                            help = 'use OAuth 2-legged authentication, \
                                    use in combination with a configuration file. \
                                    Use with extreme caution')
						
	(options, args) = parser.parse_args()
	
	"""
		If arg1 is remote server then we are exporting documents, otherwise we are
		importing documents into the Google document system
	"""
	greet(options)

        # Set up the logger
        setup_logger(options)

	if not sys.getfilesystemencoding():
		LOG.error("no encoding detected in your environment settings, try something like export LANG=en_US.UTF-8; ")
		sys.exit(1)
	
	if not len(args) == 2:
		LOG.error("invalid or missing source or destination for copying documents")
		exit(1)
	
        # Exit if user provide both standard login and oauth options
        if (options.two_legged_oauth and options.standard_login):
            LOG.error("You have to select only one authentication method")
            exit(2)

        # Exit if user don't provide the login type
        if not (options.two_legged_oauth or options.standard_login):
            LOG.error("You have to select an authentication method: --standard_login OR --two_legged_oauth")
            exit(3)

        if (options.two_legged_oauth):
            # Check if configdir exists
            configdir_type = 'Default'
            if options.configdir != defaults['configdir']:
                configdir_type = 'Specified'
            configdir = helpers.expand_user_vars(options.configdir)
            if not os.path.exists(configdir):
                raise GDataCopierOperationError('%s config/data dir "%s" does not '
                        'exist - create or specify alternate directory with '
                        '--configdir option' % (configdir_type, configdir))
            if not os.path.isdir(configdir):
                raise GDataCopierOperationError('%s config/data dir "%s" is not a '
                        'directory - fix or specify alternate directory with '
                        '--configdir option' % (configdir_type, configdir))
            if not os.access(configdir, os.W_OK):
                raise GDataCopierOperationError('%s config/data dir "%s" is not writable '
                        '- fix permissions or specify alternate directory with '
                        '--configdir option'% (configdir_type, configdir))

            # Check if configuration file exists
            path = os.path.join(os.path.expanduser(options.configdir), options.config)
            LOG.debug('processing config %s\n' % path)
            if not os.path.exists(path):
                raise GDataCopierOperationError('configuration file %s does not exist' % path)
            elif not os.path.isfile(path):
                raise GDataCopierOperationError('%s is not a file' % path)

            """
                Read from configuration file.
                An example of configuration file is this:
                    [oauth]
                    consumer_key: yourdomain.com
                    consumer_secret: rt3Fweg/AGrG0t3FwegB
            """
            try:
                config = ConfigParser.ConfigParser()
                config.read(path)
                oauth_values['consumer_key'] = config.get("oauth", "consumer_key")
                oauth_values['consumer_secret'] = config.get("oauth", "consumer_secret")
            except ConfigParser.NoSectionError, o:
                raise GDataCopierConfigurationError('configuration file %s missing section (%s)' % (path, o))
            except ConfigParser.NoOptionError, o:
                raise GDataCopierConfigurationError('configuration file %s missing option (%s)' % (path, o))
            except (ConfigParser.DuplicateSectionError,ConfigParser.InterpolationError,
                        ConfigParser.MissingSectionHeaderError,ConfigParser.ParsingError), o:
                raise GDataCopierConfigurationError('configuration file %s incorrect (%s)' % (path, o))
            except GDataCopierConfigurationError, o:
                raise GDataCopierConfigurationError('configuration file %s incorrect (%s)' % (path, o))

	if options.silent and not options.overwrite:
		print "overwrite option must be used when running in silent mode, include -o in your command"
		exit(1)
	
	"""
		Password may be provided from file, if a parameter is provided we will attempt to
		read this from the file
	"""
	if not options.password_file == None:
		try:
			options.password = open(options.password_file).read().strip()
		except:
			LOG.error("Failed to read password from file, ensure file exists with sufficient privelleges")
			sys.exit(2)
	
	"""
		If password not provided as part of the command line arguments, prompt the user
		to enter the password on the command line
	"""
	if (options.standard_login and options.password == None):
		options.password = getpass.getpass()
        
        return options, args

# Prints Greeting
def greet(options):
	if not options.silent:
		print "gcp %s, document copy utility. Copyright 2010 Eternity Technologies" % __version__
		print "Released under the GNU/GPL v3 at <http://gdatacopier.googlecode.com>\n"

# main() is where things come together, this joins all the messages defined above
# these messages must be executed in the defined order
def main():
    try:
	signal.signal(signal.SIGINT, signal_handler)
        # Check to see we have the right options or exit
	options, args = parse_user_input()
        
        document_source = args[0]
	document_target = args[1]

        # Call the method
	"""
		If the first parameter is a remote address we are backing up documents
		otherwise we are exporting documents to the Google servers. At this stage
		gcp does not support server to server or local to local copy of documents
	"""
	if helpers.is_remote_server_string(document_source) and helpers.is_remote_server_string(document_target):
		LOG.error("gcp does not support server-to-server transfer of documents, one of the locations must be local")
		exit(1)
	elif (not helpers.is_remote_server_string(document_source)) and (not helpers.is_remote_server_string(document_target)):
		LOG.error("gcp does not support local-to-local copying of files, please use cp")
		exit(1)
	elif helpers.is_remote_server_string(document_source) and (not helpers.is_remote_server_string(document_target)):
		export_documents(document_source, document_target, options)
	elif (not helpers.is_remote_server_string(document_source)) and helpers.is_remote_server_string(document_target):
		import_documents(document_source, document_target, options)
	else:
		LOG.error("gcp requires either the source or destination to be a remote address")
		exit(1)
    # Catch exceptions
    except KeyboardInterrupt:
        LOG.warning('Operation aborted by user (keyboard interrupt)\n')
        sys.exit(0)
    except GDataCopierConfigurationError, o:
        LOG.error('Configuration error: %s\n' % o)
        sys.exit(2)
    except GDataCopierOperationError, o:
        LOG.error('Error: %s\n' % o)
        sys.exit(3)
    except StandardError, o:
        LOG.critical(
            '\nException: please read docs/BUGS and include the '
            'following information in any bug report:\n\n'
        )
        LOG.critical('  GDataCopier version %s\n' % __version__)
        LOG.critical('  Python version %s\n\n' % sys.version)
        LOG.critical('Unhandled exception follows:\n')
        (exc_type, value, tb) = sys.exc_info()
        import traceback
        tblist = (traceback.format_tb(tb, None)
                  + traceback.format_exception_only(exc_type, value))
        if type(tblist) != list:
            tblist = [tblist]
        for line in tblist:
            LOG.critical('  %s\n' % line.rstrip())
        LOG.critical('\nPlease also include configuration information from running gcp\n')
        sys.exit(4)

# Begin execution of the main method since we are at the bottom of the script	
if __name__ == "__main__":
	main()
	
"""
	End of Python file
"""
