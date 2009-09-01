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

_GCP_VERSION = 2.0
_SYSLOG = False

"""
	Imports the required modules 
"""

try:
	from optparse import OptionParser
	import sys
	import os
	import re
	import signal
except:
	print "gcp failed to find some basic python modules, please validate the environment"
	exit(1)

try:
	import gdata.docs
	import gdata.docs.service
except:
	print "gcp %s required gdata-python-client v2.0+, downloadable from Google at" % _GCP_VERSION
	print "<http://code.google.com/p/gdata-python-client/>"
	exit(1)


def export_documents(source_path, target_path, options):
	return
	
	
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

	parser.add_option('-v', '--verbose', action = 'store_true', dest = 'verbose', default = False, 
						help = 'sends output to standard output, can be used in conjunction with log option')
	parser.add_option('-m', '--metadata', action = 'store_true', dest = 'metadata', default = False, 
						help = 'exports metadata for exported documents')
	parser.add_option('-p', '--password', dest = 'password', 
						help = 'password to login to Google document servers, use with extreme caution, may be logged')
	parser.add_option('-l', '--log', action = 'store_true', dest = 'log', default = True, 
						help = 'writes actions to system logger, adjust log levels to increase/decrease verbosity')
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
	print "gcp %s, import/export utility for the Google document system" % _GCP_VERSION
	print "Copyright Devraj Mukherjee, et al. Released under the GNU/GPL v3\n"

"""
	main() is where things come together, this joins all the messages defined above
	these messages must be executed in the defined order
"""
def main():
	greet()						# Greet the user with a standard welcome message
	parse_user_input()			# Check to see we have the right options or exit

# Begin execution of the main method since we are at the bottom of the script	
if __name__ == "__main__":
	main()
	
"""
	End of Python file
"""