#!/usr/bin/env python

__version__ = "2.2.0"
__author__  = "Devraj Mukherjee"

LOGGER_NAME = 'GDataCopier'

try:
        import os
        import os.path
        from gdatacopier.exceptions import *
except:
	print "failed to find some basic python modules"
	exit(1)
try:
        import re
        import gdata.docs.service
        import gdata.gauth
        import gdata.docs.data
        import gdata.docs.client
except:
	print "GDataCopier %s requires gdata-python-client v2.0+, fetch from Google at" % __version__
	print "<http://code.google.com/p/gdata-python-client/>"
	exit(1)

'''
    Return a string expanded for both leading "~/" or "~username/" and
    environment variables in the form "$varname" or "${varname}".
'''
def expand_user_vars(s):
    return os.path.expanduser(os.path.expandvars(s))

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
	Adds a category of documents to the filter
"""
def add_category_filter(document_query, docs_type):
	# If the user provided a doctype then add a filter
        # Docs
	if docs_type == "docs" or docs_type == "documents":
		document_query.categories.append('document')
        # Sheets
	elif docs_type == "sheets" or docs_type == "spreadsheets":
		document_query.categories.append('spreadsheet')
        # Slides
	elif docs_type == "slides" or docs_type == "presentation":
		document_query.categories.append('presentation')
        # Draws
	elif docs_type == "draw" or docs_type == "drawing":
		document_query.categories.append('drawing')
        # Folders
	elif docs_type == "folders":
		document_query.categories.append('folder')
        # PDFs
	elif docs_type == "pdf":
		document_query.categories.append('pdf')

"""
	If there's a filter for a title then this adds it on
"""
def add_title_match_filter(document_query, name_filter):
	# Add title match
	if not name_filter == None:
		if name_filter[len(name_filter) - 1: len(name_filter)] == "*":
			document_query['title-exact'] = 'false'
			document_query['title'] = name_filter[:len(name_filter) - 1]
		else:
			document_query['title-exact'] = 'true'
			document_query['title'] = name_filter

"""
	Is able to match a remote server directive
"""
def is_remote_server_string(remote_address):
	re_remote_address = re.compile(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}:/')
	matched_strings = re_remote_address.findall(remote_address)
	return len(matched_strings) > 0

"""
	Login method which distinguish the login type (ClientLogin or Oauth)
        from the options read by the parser
"""
def login(username, oauth_values, options, gd_client):
        # Exception are caught in list_documents() method

        # Call the rigth method for authentication
        if (options.standard_login):
            gd_client.ClientLogin(username, options.password, gd_client.source)
        elif (options.two_legged_oauth):
            gd_client.auth_token = gdata.gauth.TwoLeggedOAuthHmacToken( 
                        oauth_values['consumer_key'],
                        oauth_values['consumer_secret'],
                        username
            )

# TODO the following methods may needs some improvments...
def get_folder_id_from_name(folder_name, gd_client):
    # API v3 needs to retry the entire list of folders
    feed = gd_client.GetDocList(uri='/feeds/default/private/full/-/folder')
    found = False
    for folder in feed.entry:
        if folder.title.text == folder_name:
            (found, id) = (True, folder.resource_id.text)
    # If found return the right URI, else raise exception
    if found:
        return "/%s/contents" % id
    else:
        raise GDataCopierFolderNotExists('folder \"%s\" not exists!' % folder_name)