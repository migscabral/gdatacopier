#!/usr/bin/env python2.5

"""

	gls
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
	
	Lists documents on the Google document servers, user must provide a username
	password combination, document type and or folder names
	
	Options:
	
	--password=		Option to provide password on the command line
	
"""

_GLS_VERSION = 2.0
_GLS_SOURCE_STRING = "GDataCopier Listing Utility"

"""
	Imports the required modules 
"""

try:
	from optparse import OptionParser
	import sys
	import os
	import re
	import signal
	import getpass
except:
	print "gls failed to find some basic python modules, please validate the environment"
	exit(1)

try:
	import gdata.docs
	import gdata.docs.service
except:
	print "gls %s required gdata-python-client v2.0+, downloadable from Google at" % _GCP_VERSION
	print "<http://code.google.com/p/gdata-python-client/>"
	exit(1)

"""
	Prints out a document list to standard output in a pretty format
"""
def write_list(list_feed):
	return

"""
	Handles downloading of the document feed from Google and then
	asking the display function to spit it out
"""
def list_documents(server_string, options):

	print server_string
	# Get a handle to the document list service
	gd_client = gdata.docs.service.DocsService(source="etk-gdatacopier-v2")
	gd_client.ClientLogin('devraj@gmail.com', options.password)
	
	# Authenticate to the document service'

	# If the user provided password as a command line argument
	
	# Get the proper feed based on what options were provided
	
	
	# Write the list to the the standard output
	feed = gd_client.GetDocumentListFeed()
	for entry in feed.entry:
		print '%s %s %s' % (entry.title.text.encode('UTF-8'), entry.GetDocumentType(), entry.resourceId.text)

"""
	Is able to match a remote server directive
"""
def is_remote_server_string(remote_address):
	re_remote_address = re.compile(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}:/')
	matched_strings = re_remote_address.findall(remote_address)
	return len(matched_strings) > 0

	
def parse_user_input():
	
	usage = "usage: %prog [options] username@domain.com:/[doctype]/[foldername]"
	parser = OptionParser(usage)
	
	parser.add_option('-p', '--password', dest = 'password',
						help = 'password for the user account, use with extreme caution. Could be stored in logs/history')
						
	(options, args) = parser.parse_args()
	
	"""
		If password not provided as part of the command line arguments, prompt the user
		to enter the password on the command line
	"""

	if options.password == None: 
		options.password = getpass.getpass()
	
	"""
		arg1 must be a remote server string to fetch document lists
	"""
	
	if not len(args) == 1 or (not is_remote_server_string(args[0])):
		print "you must provide a remote server address to fetch a list of documents"
		exit(1)

	list_documents(args[0], options)

"""
	Prints Greeting
"""
def greet():
	print "gls %s, import/export utility for the Google document system" % _GLS_VERSION
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