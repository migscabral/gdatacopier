#!/usr/bin/env python2.5

"""

	gcp
	GDataCopier, http://gdatacopier.googlecode.com/
	
	Copyright 2009 Eternity Technologies.
	Distributed under the terms and conditions of the GNU/GPL v3
	
	GDataCopier is free software and comes with absolutely NO WARRANTY. Use 
	of this software is completely at YOUR OWN RISK.
	
	Version 2.0
	
	Requires:
		
		- Python 2.5
		- Python GData API 2.0+
		
	Summary:
		
	GDataCopier originally started as a backup utility for Google Documents.
	When first published GData API didn't allow downloading documents, GDataCopier
	pretended to Firefox and perform the interactions required to download the
	documents.
	
	Since GData 2.0 Google has incorporated downloading documents into the API.
	As of Version 2.0 GDataCopier provides a cp like command line utility to ease
	backup of Google Documents simpler for System Administrators.

	Usage:
	
	gcp [options] username@domain.com:/[doctype]/* /home/devraj
	
	doctype:
	
	docs			for documents
	sheets			for spreadsheets
	slides			for presentations
	
	Options:
	
	--verbose		Sends output to standard out
	--metadata		Exports meta information for each download
	--password=		Option to provide password on the command line
	--log=			Asks gcp to write to syslog	
	--format=		pdf, doc, oo (default), txt, xls
	
"""

__version__ = 2.0
__author__  = "Devraj Mukherjee"

"""
	Imports the required modules 
"""

try:
	from optparse import OptionParser
	import sys
	import os
	import re
	import signal
	import time
	import getpass
except:
	print "gcp failed to find some basic python modules, please validate the environment"
	exit(1)

try:
	import gdata.docs
	import gdata.docs.service
	import gdata.spreadsheet.service
except:
	print "gcp %s requires gdata-python-client v2.0+, downloadable from Google at" % __version__
	print "<http://code.google.com/p/gdata-python-client/>"
	exit(1)

# Accepted formats for exporting files, these have to be used as file extensions
__accepted_doc_formats__ = ['doc', 'html', 'zip', 'odt', 'pdf', 'png', 'rtf', 'txt']
__accepted_slides_formats__ = ['pdf', 'png', 'ppt', 'swf', 'txt', 'zip', 'html', 'odt']
__accepted_sheets_formats__ = ['xls', 'ods', 'txt', 'html', 'pdf', 'tsv', 'csv']
__bad_chars__ = ['\\', '/', '&']

# Raised if the document format is invalid
class GDataCopierInvalidRequestedFormat(Exception):
	pass

def signal_handler(signal, frame):
	    print "\n[Interrupted] Bye Bye!"
	    sys.exit(0)


"""
	Helpers
"""

def add_category_filter(document_query, docs_type):

	# If the user provided a doctype then add a filter
	if docs_type == "docs" or docs_type == "documents":
		document_query.categories.append('document')
	elif docs_type == "sheets" or docs_type == "spreadsheets":
		document_query.categories.append('spreadsheet')
	elif docs_type == "slides" or docs_type == "presentation":
		document_query.categories.append('presentation')
	elif docs_type == "folders":
		document_query.categories.append('folder')
	elif docs_type == "pdf":
		document_query.categories.append('pdf')

def add_title_match_filter(document_query, name_filter):

	# Add title match
	if not name_filter == None:
		if name_filter[len(name_filter) - 1: len(name_filter)] == "*":
			document_query['title-exact'] = 'false'
			document_query['title'] = name_filter[:len(name_filter) - 1]
		else:
			document_query['title-exact'] = 'true'
			document_query['title'] = name_filter
			
def get_appropriate_extension(entry, docs_type, desired_format):
	
	entry_document_type = entry.GetDocumentType()
	
	# If no docs_type it means there are a mixture of things being exported
	if desired_format == "oo" or docs_type == None:
		if entry_document_type == "document" or entry_document_type == "presentation":
			return "odt"
		elif entry_document_type == "spreadsheet":
			return "xls"
	
	# If docs_type is of specific type check for output format
	if docs_type == "docs" or docs_type == "documents":
		if __accepted_doc_formats__.count(desired_format) > 0: return desired_format
	elif docs_type == "sheets" or docs_type == "spreadsheets":
		if __accepted_sheets_formats__.count(desired_format) > 0: return desired_format
	elif docs_type == "slides" or docs_type == "presentation":
		if __accepted_slides_formats__.count(desired_format) > 0: return desired_format
	
	return None


def sanatize_filename(filename):
	
	for bad_char in __bad_chars__:
		filename = filename.replace(bad_char, '-')	
		
	return filename

def export_documents(source_path, target_path, options):
	
	if not os.path.isdir(target_path):
		print "%s does not exists or you don't have write privelleges" % target_path
		sys.exit(2)

	username, separator, document_path = source_path.partition(':')
	
	docs_type = None
	folder_name = None
	name_filter = None
	
	doc_param_parts = document_path.split('/')
	
	if len(doc_param_parts) > 1 and not doc_param_parts[1] == '':
		docs_type = doc_param_parts[1]
		
	if len(doc_param_parts) > 2 and not doc_param_parts[2] == '':
		folder_name = doc_param_parts[2]

	if len(doc_param_parts) > 3 and not doc_param_parts[3] == '':
			name_filter = doc_param_parts[3]
			
	# Get a handle to the document list service
	sys.stdout.write("Logging into Google server as %s ... " % (username))
	gd_client = gdata.docs.service.DocsService(source="etk-gdatacopier-v2")
	
	document_query = gdata.docs.service.DocumentQuery()
	
	add_category_filter(document_query, docs_type)

	# If the user provided a folder type then add this here
	if not folder_name == None and not folder_name == "all":
		document_query.AddNamedFolder(username, folder_name)

	add_title_match_filter(document_query, name_filter)
	
	try:
		
		# Authenticate to the document service'
		gd_client.ClientLogin(username, options.password)
		print "done."
		
		sys.stdout.write("Fetching document list feeds from Google servers for %s ... " % (username))
		feed = gd_client.Query(document_query.ToUri())
		print "done.\n"
		
		for entry in feed.entry:

			export_extension = get_appropriate_extension(entry, docs_type, options.format)

			if export_extension == None:
				continue
			
			# Construct a file name for the export
			export_filename = target_path + "/" + entry.author[0].name.text.encode('UTF-8') + "-" + \
			 sanatize_filename(entry.title.text.encode('UTF-8')) + "." + export_extension

			# Might use a timestamp if we implement a sync function
			updated_time = time.strftime(entry.updated.text)

			# Tell the user something about what we are doing
			sys.stdout.write("%-30s -d-> %-40s" % (entry.resourceId.text, export_filename))
			try:
				gd_client.Export(entry, export_filename)
				print " - OK"
			except gdata.service.Error:
				print " - FAILED"
				
	except gdata.service.BadAuthentication:
		print "Failed, Bad Password!"
	
	
def import_documents(source_path, target_path, options):
	return
	

"""
	Is able to match a remote server directive
"""
def is_remote_server_string(remote_address):
	re_remote_address = re.compile(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}:/')
	matched_strings = re_remote_address.findall(remote_address)
	return len(matched_strings) > 0
	
def parse_user_input():
	
	usage = "usage: %prog [options] username@domain.com:/docs/* /home/username/directory"
	parser = OptionParser(usage)

	parser.add_option('-m', '--metadata', action = 'store_true', dest = 'metadata', default = False, 
						help = 'exports metadata for exported documents')
	parser.add_option('-p', '--password', dest = 'password', 
						help = 'password to login to Google document servers, use with extreme caution, may be logged')
	parser.add_option('-f', '--format', default = 'oo',
						help = 'file format to export documents to, ensure to use default if exporting mixed types')
						
	(options, args) = parser.parse_args()
	
	"""
		If arg1 is remote server then we are exporting documents, otherwise we are
		importing documents into the Google document system
	"""
	
	if not len(args) == 2:
		print "invalid or missing source or destination for copying documents"
		exit(1)
	
	document_source = args[0]
	document_target = args[1]
	
	"""
		If password not provided as part of the command line arguments, prompt the user
		to enter the password on the command line
	"""
	
	if options.password == None: 
		options.password = getpass.getpass()
	
	"""
		If the first parameter is a remote address we are backing up documents
		otherwise we are exporting documents to the Google servers. At this stage
		gcp does not support server to server or local to local copy of documents
	"""
	if is_remote_server_string(document_source) and is_remote_server_string(document_target):
		print "gcp does not support server-to-server transfer of documents, one of the locations must be local"
		exit(1)
	elif (not is_remote_server_string(document_source)) and (not is_remote_server_string(document_target)):
		print "gcp does not support local-to-local copying of files, please use cp"
		exit(1)
	elif is_remote_server_string(document_source) and (not is_remote_server_string(document_target)):
		export_documents(document_source, document_target, options)
	elif (not is_remote_server_string(document_source)) and is_remote_server_string(document_target):
		import_documents(document_source, document_target, options)
	else:
		print "gcp requires either the source or destination to be a remote address"
		exit(1)


"""
	Prints Greeting
"""

def greet():
	print "gcp %s, document list utility. Copyright 2009 Eternity Technologies" % __version__
	print "Released under the GNU/GPL v3 at <http://gdatacopier.googlecode.com>\n"

"""
	main() is where things come together, this joins all the messages defined above
	these messages must be executed in the defined order
"""

def main():
	signal.signal(signal.SIGINT, signal_handler)
	greet()						# Greet the user with a standard welcome message
	parse_user_input()			# Check to see we have the right options or exit

# Begin execution of the main method since we are at the bottom of the script	
if __name__ == "__main__":
	main()
	
"""
	End of Python file
"""