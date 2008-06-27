#!/usr/bin/env python

"""
	gdoc-cp.py, Copyright (c) 2007 De Bortoli Wines Pty Ltd
	http://code.google.com/p/gdatacopier/
	Distributed under the terms and conditions of the GNU/GPL v3
	
	Version 1.0.3

	Developed by Eternity Technologies Pty Ltd.
	
	This is free software, and comes with ABSOLUTELY NO WARRANTY use of 
	this software is completely at your OWN RISK.

	Summary:	
	Default text based user interface for gdatacopier, intended to ease 
	bulk downloading and uploading of document to and from Google docs.
	
"""

import sys
import getopt
import getpass
import re
import os
import signal
	
from gdatacopier import *

# Global variables
__author__	= "Devraj Mukherjee <devraj@etk.com.au>"

__version__ = "1.0.3"  # Version of the user interface program
_copier		= None	   # Globally available object of GoogleDocCopier


# Humbly prints the proper usage of this user interface
def usage():
	print """
    Usage: gdoc-cp.py -u user@gmail.com -p password action
    
    -h   --help          print this message
    
    -u=  --username=     Google username, Gmail or hosted
    -p=  --password=     password for the account (in plain text)

         If username and password is not provided user will be prompted
         to enter it, use this if using gdoc-cp interactively

    -g=  --google-id=    A valid Google document id, or document type
                         spreadsheets, documents, presentations, all
                         
    -f=  --local=        Local file name, or directory if exporting many
    -b=  --label=        Only get documents that match the list of labels
    -t=  --title         Title for a document, used only while importing
    -m   --metadata      Write the metadata for the document to a text file
    
    Valid actions:
   
    -l   --list-all      lists all documents and spreadsheets
    -s   --list-sheets   lists only spreadsheets
    -d   --list-docs     lists only documents
    -j   --list-slides   lists only presentations
    
    -e=  --export=       exports the Google document is the format
                         valid params default, ods, xls, rtf, txt, pdf, oo, csv

    -i   --import        imports a local document to Google servers

	"""

# Signal handler for Ctrl+C etc
def signal_handler(signal, frame):
	print "\n[Interrupted] You seem to have changed your mind, aborting last action"
	sys.exit(0)

# Validate email address function courtsey using regular expressions
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/65215
def validate_email(email):
	if len(email) > 7:
		if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
			return True
	return False

# Checks to see if the options dictionary has a required param	  
def has_required_parameters(options, required_list):
	found = False
	for option in required_list:
		if options.has_key(option):
			found = True
	return found

# Extension of the above to return the value associated to a param
def value_for_parameter(options, required_list):
	for option in required_list:
		if options.has_key(option):
			return options[option]
	return None
	
# Displays a list of three in a beautiful way
def display_list(document_list):
	print "%-25s%-12s%-20s%s" % ("Google id", "yyyy-mm-dd", "Owner", "Document title")
	for document in document_list:
		# Only want the first 30 chars of the document title
		document_title = document['title']
		if len(document_title) > 30:
			document_title = document['title'][0:30] + ".."
		print "%-25s%-12s%-20s%s" % (document['google_id'], document['updated'][0:10], document['author_name'][0:18] + "..", document_title)
	print "\n%s item(s) found" % (len(document_list))
	return
	
# Lists documents and spreadsheets
def list_all():
	list_documents()
	list_spreadsheets()
	list_presentations()
	return

# Lists documents only
def list_documents():
	global _copier
	document_list = _copier.get_cached_document_list()
	print "Documents:\n=========="
	display_list(document_list)
	print ""
	return
	
# Lists spreadsheets only
def list_spreadsheets():
	global _copier
	document_list = _copier.get_cached_spreadsheet_list()
	print "Spreadsheets:\n============="
	display_list(document_list)
	print ""
	return	 

# List presentations only
def list_presentations():
	global _copier
	document_list = _copier.get_cached_presentation_list()
	print "Presentations:\n=============="
	display_list(document_list)
	return

# Checks to see if its	sane directory or stops the program
def is_sane_dir(local_path):
	if not os.path.isdir(local_path):
		print"ERROR: The path provided to -f or --local parameter must be a directory"
		sys.exit(2)

# Ellaborately handles the login includes exceptions
def handle_login(username, password):
	global _copier
	try:
		sys.stdout.write("Logging into Google authentication server as %s ..." % (username))
		_copier.login(username, password)
		print " done"
		sys.stdout.write("Caching a list of documents and spreadsheets ... ")
		_copier.cache_document_lists()
		print "done\n"
	except gdata.service.BadAuthentication:
		print "\nERROR: Authentication via the Google data API failed, check username and password"
		sys.exit(2)
	except SimluatedBrowserLoginFailed:
		print "\nERROR: Authentication via the simulated browser failed, check username and password"
		sys.exit(2)

# Make a file name sane so the OS doesn't bomb it out
# TODO: Replace this function with a clever regulation expression
def sanatize_filename(document_title, file_format):
	bad_char_list = ['\\', '/', ':', '~', '!', '@', '#', '$', '%', '^', '&', '*', '?', ',', '.', '|', ]
	for char in bad_char_list:
		document_title = document_title.replace(char, '')
	if file_format == "oo":
		file_format = "odt"
	return document_title + "." + file_format

"""
	All methods below this line handle UI stuff
"""

# Copies a local file to Google	   
def copy_local_to_google(source_file, document_title):
	global _copier
		
	base_path, full_file_name = os.path.split(source_file)
	file_name, file_extension = os.path.splitext(full_file_name)
	   
	try:
		google_url = _copier.import_document(source_file, document_title)
		print "%s -g-> %s" % (full_file_name, google_url)
	except FileNotFound:
		print "Error: Failed to locate the source file, check path names"
	except InvalidContentType:
		print "Error: Unable to import content of type %s to Google" % (file_extension)
	except FailedToUploadFile:
		print "Error: File upload failed, check content type and ensure the file can be read"


# Downloads a single Google document to disk
def download_document(document_id, file_format, local_path, write_metadata = False):
	global _copier
	try:
		if _copier.is_document(document_id):
			print "%-25s -d-> %s" % (document_id, local_path)
			_copier.export_document(document_id, file_format, local_path)
			if write_metadata:
				_copier.export_metadata(document_id, local_path)
		elif _copier.is_spreadsheet(document_id):
			print "%-25s -s-> %s" % (document_id, local_path)
			_copier.export_spreadsheet(document_id, file_format, local_path)
			if write_metadata:
				_copier.export_metadata(document_id, local_path)
		else:
			print "WARNING: Failed to find Google doc with id", document_id
	except FailedToDownloadFile:
		print "Error: The last download was not successful"
	except FailedToWriteDocumentToFile:
		print "Error: Failed to write to", local_path
	except InvalidExportFormat:
		print "Warning: Document id %s cannot be exported to %s" % (document_id, file_format)
	except:
		print "Unknown error while trying to dowload the last document"

# Downloads all a set of documents or spreadsheets
def download_set(doc_list, file_format, local_path, write_metadata = False):
	global _copier
	for document in doc_list:
		file_name = local_path + "/" + sanatize_filename(document['title'] + " - " + document['google_id'], file_format)
		download_document(document['google_id'], file_format, file_name, write_metadata)
	return
	

# Download a set of documents, handles default formats etc	  
def download_docs(file_format, local_path, write_metadata = False):
	if file_format == "default":
		file_format = "ods"
	doc_list = _copier.get_cached_spreadsheet_list()
	download_set(doc_list, file_format, local_path, write_metadata)

# Downloads a set of sheets, handles default formats etc
def download_sheets(file_format, local_path, write_metadata = False):
	if file_format == "default":
		file_format = "oo"
	doc_list = _copier.get_cached_document_list()
	download_set(doc_list, file_format, local_path, write_metadata)

	
# Copies a Google document to a local file, handles multiple downloads as well
def copy_google_to_local(document_id, file_format, local_path, write_metadata = False):
	global _copier
	# If no local path specified then its the current directory
	if local_path == None:
		local_path == ""

	""" Judge what the the user wants """
	if document_id == "spreadsheets":
		is_sane_dir(local_path)
		download_docs(file_format, local_path, write_metadata)
		sys.exit(0)
	elif document_id == "documents":
		is_sane_dir(local_path)
		download_sheets(file_format, local_path, write_metadata)
		sys.exit(0)
	elif document_id == "all":
		is_sane_dir(local_path)
		download_docs(file_format, local_path, write_metadata)
		download_sheets(file_format, local_path, write_metadata)
		sys.exit(0)
	elif _copier.has_item(document_id):
		download_document(document_id, file_format, local_path, write_metadata)
		sys.exit(0)
	else:
		print "ERROR: Couldn't find %s in your set of documents\n" % (document_id)
		sys.exit(2)
		
# Check for sane environment variables
def check_sane_env_vars():
	# Name value pairs for the environment var and the string expected
	validation_list = {'https_proxy': 'https://', 'http_proxy': 'http://'}
	# Check each var
	for env_var in validation_list:
		env_var_value = os.environ.get(env_var)
		# If the var is set and we can't find the string we want then display warning
		if env_var_value and not env_var_value.startswith(validation_list[env_var]):
			print "[Warning] %s doesn't start with %s, this may cause problems" % (env_var, validation_list[env_var])

# Parses various user input parameters and makes the script do hopefully
# what the user intended to do	  
def parse_user_options():

	short_opts = "u:p:g:f:e:lmsdiht:j"
	long_opts  = ["username=", "password=", "google-id=", 
				  "local=", "export=", "list-all", "list-sheets", "list-slides", 
				  "list-docs", "import", "help", "title=", "metadata"]
	try:
		opts, args = getopt.getopt(sys.argv[1:], short_opts, long_opts)
	except getopt.GetoptError:
		print "ERROR: One or more options were incorrect"
		usage()
		sys.exit(2)
		
	options = {}
	for key, value in opts:
		options[key] = value
	
	# See if the user is just after some help or if there are no options
	if has_required_parameters(options, ['-h', '--help']) or len(options) == 0:
		usage()
		sys.exit(0)
		
	# Local variables to handle username and password
	_username = ""
	_password = None
				
	# Extract the username and password into vars so we can use it all around
	if has_required_parameters(options, ['-u', '--username']):
		_username = value_for_parameter(options, ['-u', '--username'])
	# We must have a proper email address for this to work
	while(not validate_email(_username)):
		_username = raw_input("Google email: ")
	
	# Get password from getopt or ask user to enter it in	 
	if has_required_parameters(options, ['-p', '--password']):
		_password = value_for_parameter(options, ['-p', '--password'])
	else:
		 _password = getpass.getpass("Password: ")
	
	
	# Have to login for all the above functions
	handle_login(_username, _password)
		
	# List all documents and spreadsheets
	if has_required_parameters(options, ['-l', '--list-all']):
		list_all()		  
		sys.exit(0)
	
	# List all spreadsheets
	if has_required_parameters(options, ['-s', '--list-sheets']):
		list_spreadsheets()
		sys.exit(0)

	# List all presentations
	if has_required_parameters(options, ['-j', '--list-slides']):
		list_presentations()
		sys.exit(0)
		
	# List only documents
	if has_required_parameters(options, ['-d', '--list-docs']):
		list_documents()
		sys.exit(0)

	# Import a local file to a Google document
	if has_required_parameters(options, ['-i', '--import']) and has_required_parameters(options, ['-f', '--local']):
		document_title = value_for_parameter(options, ['-t', '--title'])
		local_file	= value_for_parameter(options, ['-f', '--local'])
			
		copy_local_to_google(local_file, document_title)
		sys.exit(0)
		
	# Export a Google document as a local file
	if has_required_parameters(options, ['-e', '--export']) and (has_required_parameters(options, ['-g', '--google-id'])):
		export_format = (value_for_parameter(options, ['-e', '--export'])).lower()
		# Export format is set to default if not provided
		if not export_format:
			export_format = "default"
			   
		document_id		  = value_for_parameter(options, ['-g', '--google-id'])
		local_file		  = value_for_parameter(options, ['-f', '--local'])
		write_metadata	  = has_required_parameters(options, ['-m', '--metadata'])
		
		if write_metadata:
			print "[Info] Metadata export enabled for this export\n"
		
		if not export_format in ['default', 'oo', 'rtf', 'doc', 'pdf', 'txt', 'csv', 'xls', 'ods']:
			print "ERROR: The specified export format is invalid, please check usage (-h)"
			sys.exit(2)
			
		# If local file name is None then the script will assign a name
		copy_google_to_local(document_id, export_format, local_file, write_metadata)
		sys.exit(0)
	
	# No valid options found so lets tell the user how to use this
	usage()
	sys.exit(2)

# The humble main function, useful because things stay in place		   
def main():
	# Add some signal handlers to make it easier for users
	signal.signal(signal.SIGINT, signal_handler)
	# Get a reference to the global var
	global _copier
	# Print a welcome message
	print "gdoc-cp.py version %s, bi-directional copy utility for Google docs, sheets & slides" % __version__
	print "Distributed under the GNU/GPL v3, at <http://code.google.com/p/gdatacopier/>"
	print "This is free software and comes with ABSOLUTELY NO WARRANTY, use it at your OWN RISK.\n"
	# Validate sanity of the environment
	check_sane_env_vars() 
	# Make a new GDataCopier object and start parsing options to see what the user wants
	_copier = GDataCopier()
	parse_user_options()

# If this is the end of the script and we have done nothing then lets
# start the main function
if __name__ == "__main__":
	main()

"""
	End of Python script
"""
