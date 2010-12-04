#!/usr/bin/env python

"""

	gls
	GDataCopier, http://gdatacopier.googlecode.com/

	Copyright 2010 Eternity Technologies.
	Distributed under the terms and conditions of the GNU/GPL v3

	GDataCopier is free software and comes with absolutely NO WARRANTY. Use
	of this software is completely at YOUR OWN RISK.

	Version 2.2.0

"""

__version__ = "2.2.0"
__author__  = "Devraj Mukherjee"

"""
	Imports the required modules
"""
try:
	from optparse import OptionParser
        import ConfigParser
	import datetime        
	import sys
	import os
        import os.path
	import re
	import signal
	import getpass
        from gdatacopier import helpers
        from gdatacopier.exceptions import *
except:
	print "gls failed to find some basic python modules, please validate the environment"
	exit(1)

try:
        import gdata
        import gdata.docs.service
        import gdata.gauth
        import gdata.docs.data
        import gdata.docs.client
except:
	print "gls %s requires gdata-python-client v2.0+, fetch from Google at" % __version__
	print "<http://code.google.com/p/gdata-python-client/>"
	exit(1)

try:
        # Add logs functionality
        import logging
        LOG = logging.getLogger(helpers.LOGGER_NAME)
except:
	print "gls failed to find logging python modules, please validate the environment"
	exit(1)


"""
    Default values read from configuration file
"""
defaults = {
    'gdatacopierdir' : '~/.gdatacopier/',
    'rcfile' : 'gdatacopierrc',
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
    sys.exit(0)

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

"""
	Handles downloading of the document feed from Google and then
	asking the display function to spit it out
"""
def list_documents(server_string, options):
	username, document_path = server_string.split(':', 1)
	# Counters for the uploads
	docs_counter    = 0
	sheets_counter  = 0
	slides_counter  = 0
        draws_counter   = 0
	pdf_counter     = 0

	if not helpers.is_email(username):
            LOG.info("Usernames must be provided as your full Gmail address, hosted domains included.")
            sys.exit(2)

	docs_type   = None
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
        gd_client.ssl = True                # Force all API requests through HTTPS
        gd_client.api_version = '3.0'       # Force API version 3.0
        
        if (options.debug):
            gd_client.http_client.debug = True  # Set to True for debugging HTTP requests
        else:
            gd_client.http_client.debug = False

	try:
            # Authenticate to the document service'
            helpers.login(username, oauth_values, options, gd_client)

            # With Docs API v3.0 the URI are changed
            base_feed = "/feeds/default"

            # If the user provided a folder type then add this here
            if not folder_name == None and not folder_name == "all":
                projection_folder = "full" + helpers.get_folder_id_from_name(folder_name, gd_client)
                document_query = gdata.docs.service.DocumentQuery(feed=base_feed, projection=projection_folder)
            else:
                document_query = gdata.docs.service.DocumentQuery(feed=base_feed)

            helpers.add_category_filter(document_query, docs_type)
            helpers.add_title_match_filter(document_query, name_filter)

            LOG.info("Fetching document list feeds from Google servers for %s" % (username))
            LOG.debug("Sending a request for the URI: %s" % document_query.ToUri())
            docs = gd_client.GetEverything(document_query.ToUri())  # makes multiple HTTP requests.

            print 'User %s has a total of %s documents.' % (username, len(docs))
            if len(docs) != 0:
                print '%-17s %-18s %-46s %-15s' % ('AUTHOR', 'DATE', 'TITLE', 'TYPE')

                for entry in docs:
                        document_type = entry.GetDocumentType()

                        # Thanks to http://stackoverflow.com/questions/127803/how-to-parse-iso-formatted-date-in-python
                        # regular expression to parse RFC3389
                        updated_time = datetime.datetime(*map(int, re.split('[^\d]', entry.updated.text)[:-1]))
                        date_string = updated_time.strftime('%b %d %Y %H:%M')

                        print '%-17s %-18s %-46s %-15s' % (entry.author[0].name.text[0:16], date_string, entry.title.text[0:45], document_type)

                        # Increase counters
                        if document_type == "document":
                                docs_counter = docs_counter + 1
                        elif document_type == "spreadsheet":
                                sheets_counter = sheets_counter + 1
                        elif document_type == "presentation":
                                slides_counter = slides_counter + 1
                        elif document_type == "drawing":
                                draws_counter = draws_counter + 1
                        elif document_type == "pdf":
                                pdf_counter = pdf_counter + 1

                print "\n%i document(s), %i spreadsheet(s), %i presentation(s), %i pdf(s), %i drawing(s)" \
                        % (docs_counter, sheets_counter, slides_counter, pdf_counter, draws_counter)
                                
	except gdata.client.BadAuthentication:
		LOG.error("Standard login failed. Bad Password!")
		sys.exit(2)
	except gdata.client.CaptchaRequired:
		LOG.error("Captcha required, please login using the web interface and try again.")
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
	usage  = "usage: %prog [options] username@domain.com:/[doctype]/[foldername]/Title*\n"
	usage += "              where [doctype] is docs, sheets, slides, pdf, folders"
	parser = OptionParser(usage)

	parser.add_option('-s', '--silent',
                            action = 'store_true',
                            dest = 'silent',
                            default = False,
                            help = 'decreases verbosity, supresses all messages \
                                    but summaries and critical errors')
	parser.add_option('-p', '--password',
                            dest = 'password',
                            help = 'password for the user account, use with extreme caution. \
                                    Could be stored in logs/history')
        parser.add_option('--gdatacopierdir',
                            dest='gdatacopierdir',
                            action='store', 
                            default=defaults['gdatacopierdir'],
                            help='look in DIR for config/data files', metavar='DIR')
        parser.add_option('--rcfile',
                            dest='rcfile',
                            action='append',
                            default=defaults['rcfile'],
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

	greet(options)
        
        # Set up the logger
        setup_logger(options)

	# arg1 must be a remote server string to fetch document lists
	if not len(args) == 1 or (not helpers.is_remote_server_string(args[0])):
            print "You most provide a remote server address as username@gmail.com:/[doctype]/[folder]"
            exit(1)

        # Exit if user provide both standard login and oauth options
        if (options.two_legged_oauth and options.standard_login):
            print "You have to select only one authentication method"
            exit(2)

        if (options.two_legged_oauth):
            # Check if gdatacopierdir exists
            gdatacopierdir_type = 'Default'
            if options.gdatacopierdir != defaults['gdatacopierdir']:
                gdatacopierdir_type = 'Specified'
            gdatacopierdir = helpers.expand_user_vars(options.gdatacopierdir)
            if not os.path.exists(gdatacopierdir):
                raise GDataCopierOperationError('%s config/data dir "%s" does not '
                        'exist - create or specify alternate directory with '
                        '--gdatacopierdir option' % (gdatacopierdir_type, gdatacopierdir))
            if not os.path.isdir(gdatacopierdir):
                raise GDataCopierOperationError('%s config/data dir "%s" is not a '
                        'directory - fix or specify alternate directory with '
                        '--gdatacopierdir option' % (gdatacopierdir_type, gdatacopierdir))
            if not os.access(gdatacopierdir, os.W_OK):
                raise GDataCopierOperationError('%s config/data dir "%s" is not writable '
                        '- fix permissions or specify alternate directory with '
                        '--gdatacopierdir option'% (gdatacopierdir_type, gdatacopierdir))

            # Check if configuration file exists
            path = os.path.join(os.path.expanduser(options.gdatacopierdir), options.rcfile)
            LOG.debug('processing rcfile %s\n' % path)
            if not os.path.exists(path):
                raise GDataCopierOperationError('configuration file %s does not exist' % path)
            elif not os.path.isfile(path):
                raise GDataCopierOperationError('%s is not a file' % path)

            """
                Read from configuration file.
                An example of configuration file is this:
                    [oauth]
                    consumer_key: yourdomain.com
                    consumer_secret: yourconsumerkey
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

	# If password not provided as part of the command line arguments, prompt the user
	# to enter the password on the command line
	if (options.standard_login and options.password == None):
		options.password = getpass.getpass()

        return options, args

# Prints Greeting
def greet(options):
    if not options.silent:
        print "gls %s, document list utility. Copyright 2010 Eternity Technologies" % __version__
        print "Released under the GNU/GPL v3 at <http://gdatacopier.googlecode.com>\n"

# main() is where things come together, this joins all the messages defined above
# these messages must be executed in the defined order
def main():
    try:
	signal.signal(signal.SIGINT, signal_handler)
        # Check to see we have the right options or exit
	options, args = parse_user_input()
        # Call the method
        list_documents(args[0], options)
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
            log.critical('  %s\n' % line.rstrip())
        LOG.critical('\nPlease also include configuration information from running gls\n')
        sys.exit(4)

# Begin execution of the main method since we are at the bottom of the script
if __name__ == "__main__":
	main()

"""
	End of Python file
"""
