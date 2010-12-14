#!/usr/bin/env python

__version__ = "2.2.0"
__author__  = "Devraj Mukherjee, Matteo Canato"

# Accepted formats for exporting files, these have to be used as file extensions
__accepted_doc_formats__ = ['doc', 'html', 'zip', 'odt', 'pdf', 'png', 'rtf', 'txt']
__accepted_slides_formats__ = ['pdf', 'png', 'ppt', 'swf', 'txt', 'zip', 'html', 'odt']
__accepted_sheets_formats__ = ['xls', 'ods', 'txt', 'html', 'pdf', 'tsv', 'csv']
__accepted_draw_formats__ = ['png', 'jpeg', 'svg', 'pdf']
__bad_chars__ = ['\\', '/', '&', ':']

LOGGER_NAME = 'GDataCopier'
# With Docs API v3.0 the URI are changed
BASE_FEED = "/feeds/default"

try:
        import os
        import os.path
        import sys
        import mimetypes
        mimetypes.init()
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

'''
    Return a string with the filename (without extension and 
'''
def filename_from_path(filepath):
    return os.path.splitext(os.path.basename(filepath))[0]

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

"""
    Strips characters that are not acceptable as file names
"""
def sanatize_filename(filename):
	#filename = filename.decode('UTF-8')
	filename = filename.decode(sys.getfilesystemencoding())
	for bad_char in __bad_chars__:
		filename = filename.replace(bad_char, '')

	filename = filename.lstrip().rstrip()
	return filename.encode(sys.getfilesystemencoding())

"""
    Gets an extension that works with a file format
"""
def get_appropriate_extension(entry, docs_type, desired_format):
        entry_document_type = entry.GetDocumentType()

        # If no docs_type it means there are a mixture of things being exported.
        # and the default format is OpenDocument (for OpenOffice)
	if desired_format == "oo" or docs_type == None:
		if entry_document_type == "document":
			return "odt"
		elif entry_document_type == "presentation":
			return "ppt"
		elif entry_document_type == "spreadsheet":
			return "ods"
		elif entry_document_type == "drawing":
			return "png"
		elif entry_document_type == "pdf":
			return "pdf"
                elif mimetypes.guess_extension(entry_document_type) != None:
                        # If other file guess the string from mimetype.
                        # The function returns the "dotted" file extension so
                        # we remove the first char.
                        return mimetypes.guess_extension(entry_document_type)[1:]
                else:
                        return None
        # If docs_type is of specific type check for output format                    
        else:
            # Docs
            if docs_type == "docs" or docs_type == "documents" or entry.GetDocumentType() == "document":
                    if __accepted_doc_formats__.count(desired_format) > 0: return desired_format
            # Sheets
            elif docs_type == "sheets" or docs_type == "spreadsheets" or entry.GetDocumentType() == "spreadsheet":
                    if __accepted_sheets_formats__.count(desired_format) > 0: return desired_format
            # Slides
            elif docs_type == "slides" or docs_type == "presentation" or entry.GetDocumentType() == "presentation":
                    if __accepted_slides_formats__.count(desired_format) > 0: return desired_format
            # Draws
            elif docs_type == "draw" or docs_type == "drawing" or entry.GetDocumentType() == "drawing":
                    if __accepted_draw_formats__.count(desired_format) > 0: return desired_format
            # PDFs
            elif docs_type == "pdf" or desired_format == "pdf":
                    return "pdf"
            # Others file
            elif mimetypes.guess_extension(entry_document_type) != None:
                    # If other file guess the string from mimetype.
                    # The function returns the "dotted" file extension so
                    # we remove the first char.
                    return mimetypes.guess_extension(entry_document_type)[1:]
            else:
                    return None
	return None

def is_a_known_extension(ext):
    if (ext in __accepted_doc_formats__) or (ext in __accepted_slides_formats__) \
        or (ext in __accepted_sheets_formats__) or (ext in __accepted_draw_formats__):
            return True
    else:
            return False

"""
    The following method should be used in gcp when arbitrary files upload will be
    available not only for Google Apps for Business accounts.
"""
def get_mime_type(filename):
    return mimetypes.guess_type(os.path.basename(filename))[0]

"""
    If the folder exists, returns the folder entry.
    Otherwise returns None.
"""
def get_folder_entry(gd_client, folder_name):
    document_query = gdata.docs.service.DocumentQuery(feed=BASE_FEED)

    if not (folder_name == None or folder_name == "all"):
        document_query.categories.append('folder')

    feed = gd_client.GetEverything(document_query.ToUri())

    for entry in feed:
        if entry.title.text == folder_name:
            return entry
    return None

"""
    If the document exists, returns the entry of the doc.
    Otherwise returns None.
"""
def get_document_resource(gd_client, folder, doc_name):
    filename = filename_from_path(doc_name)

    if folder == None or folder == "all":
        in_root = True
        feed = gd_client.GetEverything(uri='/feeds/default/private/full/folder%3Aroot/contents/')
    else:
        in_root = False
        feed = gd_client.GetEverything(uri=folder.content.src)

    for doc in feed:
        if doc.title.text == filename:
            if in_root==False or (len(doc.InFolders())==0 and in_root==True):
                return doc
    return None