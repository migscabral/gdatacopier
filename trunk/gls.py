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
	import time
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
	print "gls %s requires gdata-python-client v2.0+, fetch from Google at" % _GCP_VERSION
	print "<http://code.google.com/p/gdata-python-client/>"
	exit(1)


def signal_handler(signal, frame):
    print "\n[Interrupted] Bye Bye!"
    sys.exit(0)

"""
	Validate email address function courtsey using regular expressions
	http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/65215
"""
def is_email(email):
    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
            return True
    return False

"""
	Handles downloading of the document feed from Google and then
	asking the display function to spit it out
"""
def list_documents(server_string, options):
	
	username, separator, document_path = server_string.partition(':')
	
	if not is_email(username):
		print "Usernames most be provided as your full Gmail address, hosted domains included."
		sys.exit(2)

	doc_type = None
	folder_name = None
	
	doc_param_parts = document_path.split('/')
	
	if doc_param_parts.count > 1 and not doc_param_parts[1] == '':
		doc_type = doc_param_parts[1]
		
	if doc_param_parts.count > 2 and not doc_param_parts[2] == '':
		folder_name = doc_param_parts[2]

	# Get a handle to the document list service
	sys.stdout.write("Logging into Google server as %s ... " % (username))
	gd_client = gdata.docs.service.DocsService(source="etk-gdatacopier-v2")
	
	try:
		# Authenticate to the document service'
		gd_client.ClientLogin(username, options.password)
		print "done."
		
		sys.stdout.write("Fetching document list feeds from Google servers for %s ... " % (username))
		feed = gd_client.GetDocumentListFeed()
		print "done.\n"
		
		for entry in feed.entry:
			#updated_time = time.asctime(entry.updated.text)
			print '%-15s%-17s%-50s' % (entry.GetDocumentType(), entry.author[0].name.text.encode('UTF-8'), entry.title.text.encode('UTF-8'))

	except gdata.service.BadAuthentication:
		print "Failed, Bad Password!"
	except gdata.service.Error:
		print "Failed!"


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
		arg1 must be a remote server string to fetch document lists
	"""
	
	if not len(args) == 1 or (not is_remote_server_string(args[0])):
		print "you most provide a remote server address as username@gmail.com:/[doctype]/[folder]"
		exit(1)

	"""
		If password not provided as part of the command line arguments, prompt the user
		to enter the password on the command line
	"""

	if options.password == None: 
		options.password = getpass.getpass()

	list_documents(args[0], options)

"""
	Prints Greeting
"""
def greet():
	print "gls %s, document list utility. Copyright 2009 Eternity Technologies" % _GLS_VERSION
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