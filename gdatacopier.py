#!/usr/bin/env python2.5

"""
    GoogleDocCopier, Copyright (c) 2007 De Bortoli Wines Pty Ltd
    Released under the terms and conditions of the GNU/GPL

    Developed by Eternity Technologies Pty Ltd.
           
    Tested to work under GNU/Linux operating systems. This software comes with
    NO WARRANTY and its use is completely at YOUR OWN RISK.
   
    Relies on:
     - Python version 2.5 or greater
     - Google Data Python libraries
       http://code.google.com/apis/gdata/clientlibs.html

    Summary:
    Uses the Google Data API to obtain lists of documents and spreadsheets and acts
    as a web browser, to perform a login, handle redirects, manage cookies and then
    finally fires an appropriate URL to download the doc or spreadhseet
   
    Intended to be used as a library for backing up Google documents and spreadsheets
    to Open Document formats for offline use and storage.
   
    Any change to Google's Data API or the way they implement their export functions
    may cease this API to work. If you are writing a UI please see the list of exceptions
    and handle it at the UI level
   
    Note the user agent is set to Firefox running on Ubuntu, this has to be set to
    something well accepted like Firefox, otherwise Google will reject the requests
   
    Resouces:   
      - How cookielib works in Python
        http://www.voidspace.org.uk/python/articles/cookielib.shtml
      - How to ask Google docs to send different versions of the document
        http://googlesystem.blogspot.com/2007/07/download-published-documents-and.html

"""
   
"""
    Imports Google and python libs
"""

import sys
import tempfile
import urllib
import exceptions
import urllib2
import time

import cookielib
from urllib2  import *
from urlparse import *

import gdata.docs
import gdata.docs.service

"""
    Exceptions
"""

class NotLoggedInSimulatedBrowser(exceptions.Exception):
    pass
class SimluatedBrowserLoginFailed(exceptions.Exception):
    pass
class NotEnoughCookiesFromGoogle(exceptions.Exception):
    pass
class DocumentDownloadURLError(exceptions.Exception):
    pass
class FailedToDownloadFile(exceptions.Exception):
    pass
class FailedToUploadFile(exceptions.Exception):
    pass
class InvalidExportFormat(exceptions.Exception):
    pass
class FailedToWriteDocumentToFile(exceptions.Exception):
    pass
class FileNotFound(exceptions.Exception):
    pass
class InvalidContentType(exceptions.Exception):
    pass
    
"""
    DocumentFormats, for use with the API
"""

class GoogleDocFormat:

    OOWriter  = "oo"
    MSWord    = "doc"
    RichText  = "rtf"
    Text      = "txt"
    PDF       = "pdf"
    
    
class GoogleSpreadsheetFormat:

    MSExcel   = "xls"
    CSV       = "csv"
    txt       = "txt"
    OOCalc    = "ods"

"""
    Main document downloader class
"""

class GoogleDocCopier:

    __gd_client            = None     # GData object
    __cokie_jar            = None     # Cookie jar object to handle cookies
    __is_logged_in         = False    # State of login for this session
    __is_hosted_account    = False    # True or False
    __hosted_domain        = None     # We need the hosted domain to construct urls
    
    __cached_doc_list      = []       # Cached document list
    __cached_sheet_list    = []       # Cached spreadsheet list
    
    __proxy_strings        = {}       # Proxy strings, if blank ignored
    
    # Some pre-set strings and urls that are required to perform the magic
    # http://googlesystem.blogspot.com/2007/07/download-published-documents-and.html
       
    __url_google_auth      = "https://www.google.com/accounts/ServiceLoginAuth"
    __url_google_followup  = "http://docs.google.com"
    __url_google_get_doc   = "http://docs.google.com/MiscCommands?command=saveasdoc&exportformat=%s&docID=%s"
    __url_google_get_sheet = "http://spreadsheets.google.com/ccc?output=%s&key=%s"
    
    # If you are using Google hosted applications the URLs are somewhat different
    # these variables hold the pattern, and the API switches accordingly
    
    __url_hosted_auth      = "https://www.google.com/a/%s/LoginAction"
    __url_hosted_followup  = "http://docs.google.com/a/%s/"
    __url_hosted_get_doc   = "http://docs.google.com/a/%s/MiscCommands?command=saveasdoc&exportformat=%s&docID=%s"
    __url_hosted_get_sheet = "http://spreadsheets.google.com/a/%s/pub?output=%s&key=%s"
    
    # Set the user agent to whatever you please, but make sure its accepted by Google
    # also, please leave the authors name in there, I put in a lot of hard work
    
    __valid_doc_formats    = ['doc', 'oo', 'txt', 'pdf', 'rtf']
    __valid_sheet_formats  = ['xls', 'ods', 'csv', 'pdf', 'txt']
    __sheet_content_types  = { 'ods': 'application/vnd.oasis.opendocument.spreadsheet', 'csv': 'text/comma-separated-values',
                               'xls': 'application/vnd.ms-excel' }
    __doc_content_types    = { 'doc': 'application/msword', 'odt': 'application/vnd.oasis.opendocument.text',
                               'rtf': 'application/rtf', 'sxw': 'application/vnd.sun.xml.writer',
                               'txt': 'text/plain' }
                               
    # Default formats the files are exported in
    __default_sheet_format = "ods"
    __default_doc_format   = "oo"

    # User agent sent to Google's servers
    __user_agent           = "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20061201 Firefox/2.0.0.6 (Ubuntu-feisty)"
    
    __author__             = "Devraj Mukherjee <devraj@gmail.com>"
    
    # Default constructors, basically sets up a few a things, much like logout
    def __init__(self):
        self.logout()
        return
        
        
    # Login authenticates a user account using the gdata and urllib2 methods
    def login(self, username, password):
    
        # Lets establish if this is a hoted or a Google account by the email 
        self.__set_account_type(username)
    
        # Establish a connection for the Google document feeds
        self.__gd_client          = gdata.docs.service.DocsService()
        
        self.__gd_client.email    = username
        self.__gd_client.password = password
        self.__gd_client.service  = "writely"
        
        self.__gd_client.ProgrammaticLogin()
        
        # Establish a connection via urllib2 for downloading, implement this request
        # wget --save-cookies cookies.txt --post-data "continue=http://docs.google.com&followup=
        # http://docs.google.com&Email=devraj&Passwd=password&PersistentCookie=true" 
        # https://www.google.com/accounts/ServiceLoginAuth?service=writely -O file.txt -c
        
        prepared_auth_url = None
        login_data = None
        
        if self.__is_hosted_account:
            app_username, domain = username.split('@')
            followup_url      = self.__url_hosted_followup % self.__hosted_domain
            login_data        = {'persistent': 'true', 'userName': app_username, 'password': password, 
                                 'continue': followup_url, 'followup': followup_url}
            prepared_auth_url = self.__url_hosted_auth % (self.__hosted_domain)
        else:
            login_data        = {'PersistentCookies': 'true', 'Email': username, 'Passwd': password, 
                                 'continue': self.__url_google_followup, 'followup': self.__url_google_followup}
            prepared_auth_url = self.__url_google_auth

                
        if (not login_data == None) and (not prepared_auth_url == None):
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie_jar))
            opener.addheaders = [('User-agent', self.__user_agent)]
            response = opener.open(prepared_auth_url, urllib.urlencode(login_data))
            self.__is_logged_in = True
            
            if len(self.__cookie_jar) < 2:
                raise NotEnoughCookiesFromGoogle
        else:
            raise SimluatedBrowserLoginFailed

    # Logout clears out all cookies, caches etc
    def logout(self):
        self.__cookie_jar        = None
        self.__cookie_jar        = cookielib.CookieJar()
        self.__is_logged_in      = False
        self.__cached_doc_list   = []
        self.__cached_sheet_list = []

    # Imports a local file to a Google document
    def import_document(self, document_path, document_title = None):
        if not os.path.isfile(document_path):
            raise FileNotFound

        # We will require the content type of this document
        base_path, full_file_name = os.path.split(document_path)
        file_name, file_extension = os.path.splitext(full_file_name)
        
        # Remove any dots in the file_extension
        file_extension = file_extension.replace(".", "")
        
        # If the file doesn't have an extension then we have a problem
        if len(file_extension) < 1:
            raise InvalidContentType

		# If no document title has been provided we will assign one
        if document_title == None:
            document_title = file_name

        entry = None
        
        if self.__sheet_content_types.has_key(file_extension):
            content_type = self.__sheet_content_types[file_extension]
            media_source = gdata.MediaSource(file_path = document_path, content_type = content_type)
            entry = self.__gd_client.UploadSpreadsheet(media_source, document_title)
        elif self.__doc_content_types.has_key(file_extension):
            content_type = self.__doc_content_types[file_extension]
            media_source = gdata.MediaSource(file_path = document_path, content_type = content_type)
            entry = self.__gd_client.UploadDocument(media_source, document_title)
        else:
            raise InvalidContentType
            
        # At this point if entry is None then the file upload failed for some reason
        if entry == None:
            raise FailedToUploadFile

        return entry.GetAlternateLink().href
        
    # Exports a Google document to a local file
    def export_document(self, document_id, file_format ="default", output_path = None):
        # Set file format to oo if user has chosen default
        if file_format == "default":
            file_format = self.__default_doc_format
        # We must have a valid file format
        if not file_format in self.__valid_doc_formats:
            raise InvalidExportFormat
        
        prepared_download_url = None
        
        if self.__is_hosted_account:
            prepared_download_url = self.__url_hosted_get_doc % (self.__hosted_domain, file_format, document_id)
        else:
            prepared_download_url = self.__url_google_get_doc % (file_format, document_id)
            
        if not prepared_download_url == None:
            self.__export(prepared_download_url, output_path)
        else:
            raise DocumentDownloadURLError              
               
    # Exports a Google spreadsheet to a local file
    def export_spreadsheet(self, document_id, file_format = "default", output_path = None):
        # Set file format to ods if user has chosen default
        if file_format == "default":
            file_format = self.__default_sheet_format
        # We must have a valid file format
        if not file_format in self.__valid_sheet_formats:
            raise InvalidExportFormat
            
        prepared_download_url = None
        
        if self.__is_hosted_account:
            prepared_download_url = self.__url_hosted_get_sheet % (self.__hosted_domain, file_format, document_id)
        else:
            prepared_download_url = self.__url_google_get_sheet % (file_format, document_id)

        if not prepared_download_url == None:
            self.__export(prepared_download_url, output_path)
        else:
            raise DocumentDownloadURLError
        
    # Imports a local file to a Google spreadsheet
    def import_spreadsheet(self, spreadsheet_path):        
        print "not implemented"
        
    # Caches the documents lists
    def cache_document_lists(self):
        self.__cached_doc_list   = self.get_document_list()
        self.__cached_sheet_list = self.get_spreadsheet_list()
        
    # Returns the currently cached list of documents
    def get_cached_document_list(self):
        return self.__cached_doc_list
       
    # Returns the currently cached list of spreadhseets
    def get_cached_spreadsheet_list(self):
        return self.__cached_sheet_list
        
    # Gets a live list of documents from Google
    def get_document_list(self):
        return self.__get_item_list('document')
    
    # Gets a live list of spreadsheets from Google
    def get_spreadsheet_list(self):
        return self.__get_item_list('spreadsheet')
        
    # Checks to see if a document or spreadsheet exists
    def has_item(self, document_id):
        return self.is_spreadsheet(document_id) or self.is_document(document_id)
        
    # Given a document id checks to see if its a spreadsheet
    def is_spreadsheet(self, document_id):
        # If the spreadsheet cache is empty the fill it up
        if len(self.__cached_sheet_list) == 0:
            self.__cached_sheet_list = self.get_spreadsheet_list()
            
        for document in self.__cached_sheet_list:
            if document['google_id'] == document_id:
                return True
        return False
        
    # Given a document id checks to see if its a spreadsheet
    def is_document(self, document_id):
        # If the cache is empty then try and cache again
        if len(self.__cached_doc_list) == 0:
            self.__cached_doc_list = self.get_document_list()
            
        for document in self.__cached_doc_list:
            if document['google_id'] == document_id:
                return True
        return False
    
    """
        Private functions to support various hacky Google POST requests, also 
        helps handle hosted or Google account variations
    """
    
    # Function to check if this is a hosted or Google account
    def __set_account_type(self, username):
        # By default lets assume this is not a hosted account
        self.__is_hosted_account = False
        
        user, domain = username.split('@')
        if not domain == "gmail.com":
            self.__is_hosted_account = True
            self.__hosted_domain = domain
   
    # Helper export function  
    def __export(self, download_url, file_name):
        if (not self.__is_logged_in):
            raise NotLoggedInSimulatedBrowser
                   
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie_jar))
        opener.addheaders = [('User-agent', self.__user_agent)]
        
        try:
            response = opener.open(download_url)
        except HTTPError:
            raise FailedToDownloadFile
            
        try:
            file_handle = open(file_name, 'wb')
            file_handle.write(response.read())
            file_handle.close()
        except:
            raise FailedToWriteDocumentToFile
            
        response.close()
    
    # Gets a list of items from Google docs and filters its based on type        
    def __get_item_list(self, item_type = None):
        if (not self.__is_logged_in):
            raise NotLoggedInSimulatedBrowser

        item_list = []
        feed = self.__gd_client.GetDocumentListFeed()
        feed_entries = feed.entry
        
        # Return to caller if there are no feed items
        if(len(feed_entries) == 0):
        	return item_list

        for entry in feed_entries:
            if self.__is_item_of_type(entry.category, item_type):
                item_list.append({'title': entry.title.text.encode('UTF-8'), 
                                  'google_id': self.__get_document_id(entry.GetAlternateLink().href), 
                                  'updated': self.__get_document_date(entry.updated.text)})

        return item_list

    # Parses the document id out of the alternate link url, the atom feed
    # doesn't actually provide the document id      
    def __get_document_id(self, alternate_link):
    	parsed_url = urlparse(alternate_link)
    	url_params = parsed_url[4]
    	document_id = url_params.split('=')[1]
        return document_id
        
    # Parses the date out of the string    
    def __get_document_date(self, updated_date):
    	return updated_date[0:10]
        
    # Checks to see if the item is of a particular type, document or spreadhseet
    # the Google atom library sends a tuple of categories    
    def __is_item_of_type(self, categories, item_type):
        for category in categories:
            if category.label == item_type:
                return True
        return False
        
"""
    End of Python API
"""
