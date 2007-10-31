#!/usr/bin/env python2.5

"""
    gdoc-cp.py, Copyright (c) 2007 De Bortoli Wines Pty Ltd
    http://code.google.com/p/gdatacopier/
    Released under the terms and conditions of the GNU/GPL

    Developed by Eternity Technologies Pty Ltd.

    Tested to work under GNU/Linux operating systems. This software comes with
    NO WARRANTY and its use is completely at YOUR OWN RISK.
    
    Summary:    
    Default text based user interface for gdatacopier, intended to ease 
    bulk downloading and uploading of document to and from Google docs.
    
"""

import sys
import getopt
import getpass
import re
import os
    
from gdatacopier import *

# Global variables
__author__  = "Devraj Mukherjee <devraj@etk.com.au>"

__version__ = "1.0.1"  # Version of the user interface program
_copier     = None     # Globally available object of GoogleDocCopier


# Humbly prints the proper usage of this user interface
def usage():
    print """
    Usage: gdoc-cp.py -u user@gmail.com -p password action
    
    -h   --help          print this message
    
    -u=  --username=     Google username, Gmail or hosted
    -p=  --password=     password for the account (in plain text)

         If username and password is not provided user will be prompted
         to enter it, use this if using gdoc-cp interactively

    -g=  --google-id=    A valid Google document id, or one the following
                         spreadsheets - for all spreadsheets
                         documents    - for all documents
                         all          - for spreadsheets and documents
                         
    -f=  --local=        Local file name, or directory if exporting
                         multiple documents
                         
    -t=  --title         Title for a document, used only while importing
    
    Valid actions:
   
    -l   --list-all      lists all documents and spreadsheets
    -s   --list-sheets   lists only spreadsheets
    -d   --list-docs     lists only documents
    
    -m   --metadata      Writes an additional text file with document metadata
   
    -e=  --export=       exports the Google document is the format
                         valid params default, ods, xls, rtf, txt, pdf, oo, csv
                         default exports files in OASIS formats

    -i   --import        imports a local document to Google servers

    """

# Validate email address function courtsey
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
    print "%-25s%-12s%s" % ("Google id", "yyyy-mm-dd", "Document title")
    for document in document_list:
        print "%-25s%-12s%s" % (document['google_id'], document['updated'], document['title'])
    print "\n%s item(s) found" % (len(document_list))
    return
    
# Lists documents and spreadsheets
def list_all():
    list_documents()
    list_spreadsheets()
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
    
# Checks to see if its  sane directory or stops the program
def is_sane_dir(local_path):
    if not os.path.isdir(local_path):
        print"ERROR: The path provided to -f or --local parameter must be a directory"
        sys.exit(2)

# Ellaborately handles the login includes exceptions
def handle_login(username, password):
    global _copier
    try:
        sys.stdout.write("Logging into Google server as %s ..." % (username))
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
    except NotEnoughCookiesFromGoogle:
        print "\nERROR: Google returned a shorter response than expected, there's something wrong"
        sys.exit(2)
"""
    except:
        print "\nUnknown error while attempting to login to Google servers"
        sys.exit(2)
"""
# Make a file name sane so the OS doesn't bomb it out
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
def download_document(document_id, file_format, local_path):
    global _copier
    try:
        if _copier.is_document(document_id):
            print "%-25s -d-> %s" % (document_id, local_path)
            _copier.export_document(document_id, file_format, local_path)
        elif _copier.is_spreadsheet(document_id):
            print "%-25s -s-> %s" % (document_id, local_path)
            _copier.export_spreadsheet(document_id, file_format, local_path)
        else:
            print "	WARNING: Failed to find Google doc with id", document_id
    except FailedToDownloadFile:
        print "Error: The last download was not successful"
    except FailedToWriteDocumentToFile:
        print "Error: Failed to write to", local_path
    except InvalidExportFormat:
        print "Warning: Document id %s cannot be exported to %s" % (document_id, file_format)
    except:
        print "Unknown error while trying to dowload the last document"
        
# Downloads all a set of documents or spreadsheets
def download_set(doc_list, file_format, local_path):
    global _copier
    for document in doc_list:
        file_name = local_path + "/" + sanatize_filename(document['title'] + " - " + document['google_id'], file_format)
        download_document(document['google_id'], file_format, file_name)
    return
    

# Download a set of documents, handles default formats etc    
def download_docs(file_format, local_path):
    if file_format == "default":
        file_format = "ods"
    doc_list = _copier.get_cached_spreadsheet_list()
    download_set(doc_list, file_format, local_path)

# DOwnloads a set of sheets, handles default formats etc
def download_sheets(file_format, local_path):
    if file_format == "default":
        file_format = "oo"
    doc_list = _copier.get_cached_document_list()
    download_set(doc_list, file_format, local_path)

    
# Copies a Google document to a local file, handles multiple downloads as well
def copy_google_to_local(document_id, file_format, local_path):
    global _copier

    # If no local path specified then its the current directory
    if local_path == None:
        local_path == ""

    """ Judge what the the user wants """
    if document_id == "spreadsheets":
        is_sane_dir(local_path)
        download_docs(file_format, local_path)
        sys.exit(0)
    elif document_id == "documents":
        is_sane_dir(local_path)
        download_sheets(file_format, local_path)
        sys.exit(0)
    elif document_id == "all":
        is_sane_dir(local_path)
        download_docs(file_format, local_path)
        download_sheets(file_format, local_path)
        sys.exit(0)
    elif _copier.has_item(document_id):
        download_document(document_id, file_format, local_path)
        sys.exit(0)
    else:
        print "ERROR: Couldn't find %s in your set of documents\n" % (document_id)
        sys.exit(2)

# Parses various user input parameters and makes the script do hopefully
# what the user intended to do    
def parse_user_options():

    short_opts = "u:p:g:f:e:lsdiht:"
    long_opts  = ["username=", "password=", "google-id=", 
                  "local=", "export=", "list-all", "list-sheets",
                  "list-docs", "import", "help", "title="]
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
        
    # List only documents
    if has_required_parameters(options, ['-d', '--list-docs']):
        list_documents()
        sys.exit(0)

    # Import a local file to a Google document
    if has_required_parameters(options, ['-i', '--import']) and has_required_parameters(options, ['-f', '--local']):
        document_title = value_for_parameter(options, ['-t', '--title'])
        local_file  = value_for_parameter(options, ['-f', '--local'])
            
        copy_local_to_google(local_file, document_title)
        sys.exit(0)
        
    # Export a Google document as a local file
    if has_required_parameters(options, ['-e', '--export']) and (has_required_parameters(options, ['-g', '--google-id'])):
        export_format = (value_for_parameter(options, ['-e', '--export'])).lower()
        document_id   = value_for_parameter(options, ['-g', '--google-id'])
        local_file    = value_for_parameter(options, ['-f', '--local'])
        
        if not export_format in ['default', 'oo', 'rtf', 'doc', 'pdf', 'txt', 'csv', 'xls', 'ods']:
            print "ERROR: The specified export format is invalid, please check usage (-h)"
            sys.exit(2)
            
        # If local file name is None then the script will assign a name
        copy_google_to_local(document_id, export_format, local_file)
        sys.exit(0)
    
    # No valid options found so lets tell the user how to use this
    usage()
    sys.exit(2)

# The humble main function, useful because things stay in place        
def main():
    global _copier
    print "gdoc-cp.py version %s, content copy & backup utility for Google documents & spreadsheets" % __version__
    print "Distributed under the GNU/GPL v2, Copyright (c) De Bortoli Wines <http://debortoli.com.au>"
    _copier = GDataCopier()
    parse_user_options()

# If this is the end of the script and we have done nothing then lets
# start the main function
if __name__ == "__main__":
    main()

"""
	End of Python script
"""
