#!/usr/bin/env python

"""
    gdatacopier.py, Copyright (c) 2007 De Bortoli Wines Pty Ltd
    http://code.google.com/p/gdatacopier/
    Released under the terms and conditions of the GNU/GPL

    Developed by Eternity Technologies Pty Ltd.
           
    Tested to work under GNU/Linux operating systems. This software comes with
    NO WARRANTY and its use is completely at YOUR OWN RISK.
   
    Relies on:
     - Python version 2.4 or greater
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
import base64
import os

import cookielib
from urllib2  import *
from urlparse import *

import gdata.docs
import gdata.docs.service

"""
    Exceptions, quite self explainatory
"""

class NotLoggedInSimulatedBrowser(exceptions.Exception):
    pass
class SimluatedBrowserLoginFailed(exceptions.Exception):
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
class NoSuchGoogleDocument(exceptions.Exception):
    pass

        
"""
    DocumentFormats, for use with the API, to used as constants while
    programming with GDataCopier
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
    Text      = "txt"
    OOCalc    = "ods"

"""
    HTTPS proxy handling classes, adaption of original source availabe at
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/456195
"""

class ProxyHTTPConnection(httplib.HTTPConnection):

    _ports = {'http' : 80, 'https' : 443}

    def request(self, method, url, body=None, headers={}):
        #request is called before connect, so can interpret url and get
        #real host/port to be used to make CONNECT request to proxy
        proto, rest = urllib.splittype(url)
    
        if proto is None:
            raise ValueError, "unknown URL type: %s" % url
        #get host
        host, rest = urllib.splithost(rest)
        #try to get port
        host, port = urllib.splitport(host)
        #if port is not defined try to get from proto
        if port is None:
            try:
                port = self._ports[proto]
            except KeyError:
                raise ValueError, "unknown protocol for: %s" % url
        self._real_host = host
        self._real_port = port
        httplib.HTTPConnection.request(self, method, url, body, headers)

    def connect(self):
        httplib.HTTPConnection.connect(self)
    
        # Modified by Devraj Mukherjee to add authentication support basic auth
        #send proxy CONNECT request
        extra_string = "CONNECT %s:%s HTTP/1.0\r\n" % (self._real_host, self._real_port)
        extra_string += self._get_authentication_string() + "\r\n"
        self.send(extra_string)

        #expect a HTTP/1.0 200 Connection established
        response = self.response_class(self.sock, strict=self.strict, method=self._method)
        (version, code, message) = response._read_status()
        #probably here we can handle auth requests...
        if code != 200:
            #proxy returned and error, abort connection, and raise exception
            self.close()
            raise socket.error, "Proxy connection failed: %d %s" % (code, message.strip())
        #eat up header block from proxy....
        while True:
            #should not use directly fp probablu
            line = response.fp.readline()
            if line == '\r\n': break
        
    def _get_authentication_string(self):
        auth_string = ""
        proxy_username = os.environ.get("proxy-username")
        proxy_password = os.environ.get("proxy-password")
        if proxy_username and proxy_password:
            encoded_user_pass = base64.encodestring("%s:%s" % (proxy_username, proxy_password))
            auth_string = "Proxy-authorization: Basic %s\r\n" % encoded_user_pass
        
        return auth_string


class ProxyHTTPSConnection(ProxyHTTPConnection):
    
    default_port = 443

    def __init__(self, host, port = None, key_file = None, cert_file = None, strict = None):
        ProxyHTTPConnection.__init__(self, host, port)
        self.key_file = key_file
        self.cert_file = cert_file
    def connect(self):
        ProxyHTTPConnection.connect(self)
        #make the sock ssl-aware
        ssl = socket.ssl(self.sock, self.key_file, self.cert_file)
        self.sock = httplib.FakeSocket(self.sock, ssl)

class ConnectHTTPHandler(urllib2.HTTPHandler):

    def __init__(self, proxy=None, debuglevel=0):
        self.proxy = self._parse_proxy_details(proxy)
        urllib2.HTTPHandler.__init__(self, debuglevel)

    def do_open(self, http_class, req):
        if self.proxy is not None:
            req.set_proxy(self.proxy, 'http')
        return urllib2.HTTPHandler.do_open(self, ProxyHTTPConnection, req)

    def _parse_proxy_details(self, proxy_string):
        proto, rest = urllib.splittype(proxy_string)
        host,  rest = urllib.splithost(rest)
        host,  port = urllib.splitport(host)
        return "%s:%s" % (host, port)

class ConnectHTTPSHandler(urllib2.HTTPSHandler):

    def __init__(self, proxy=None, debuglevel=0):
        self.proxy = self._parse_proxy_details(proxy)
        urllib2.HTTPSHandler.__init__(self, debuglevel)

    def do_open(self, http_class, req):
        if self.proxy is not None:
            req.set_proxy(self.proxy, 'https')
        return urllib2.HTTPSHandler.do_open(self, ProxyHTTPSConnection, req)
    
    def _parse_proxy_details(self, proxy_string):
        proto, rest = urllib.splittype(proxy_string)
        host,  rest = urllib.splithost(rest)
        host,  port = urllib.splitport(host)
        return "%s:%s" % (host, port)	

"""
    Main document downloader class
"""

class GDataCopier:

    _gd_client            = None     # GData object
    _cookie_jar           = None     # Cookie jar object to handle cookies
    _is_logged_in         = False    # State of login for this session
    _is_hosted_account    = False    # True or False
    _hosted_domain        = None     # We need the hosted domain to construct urls
    
    _cached_doc_list      = []       # Cached document list
    _cached_sheet_list    = []       # Cached spreadsheet list
    
    _proxy_strings        = {}       # Proxy strings, if blank ignored
    
    # Some pre-set strings and urls that are required to perform the magic
    # http://googlesystem.blogspot.com/2007/07/download-published-documents-and.html
       
    _url_google_auth      = "https://www.google.com/accounts/ServiceLoginAuth"
    _url_google_followup  = "https://docs.google.com"
    _url_google_get_doc   = "https://docs.google.com/MiscCommands?command=saveasdoc&exportformat=%s&docID=%s"
    _url_google_get_sheet = "https://spreadsheets.google.com/ccc?output=%s&key=%s"
    
    # If you are using Google hosted applications the URLs are somewhat different
    # these variables hold the pattern, and the API switches accordingly
    
    _url_hosted_auth      = "https://www.google.com/a/%s/LoginAction"
    _url_hosted_followup  = "https://docs.google.com/a/%s/"
    _url_hosted_get_doc   = "https://docs.google.com/a/%s/MiscCommands?command=saveasdoc&exportformat=%s&docID=%s"
    _url_hosted_get_sheet = "https://spreadsheets.google.com/a/%s/pub?output=%s&key=%s"
    
    # Set the user agent to whatever you please, but make sure its accepted by Google
    # also, please leave the authors name in there, I put in a lot of hard work
    
    _valid_doc_formats    = ['doc', 'oo', 'txt', 'pdf', 'rtf']
    _valid_sheet_formats  = ['xls', 'ods', 'csv', 'pdf', 'txt']
    _sheet_content_types  = { 'ods': 'application/vnd.oasis.opendocument.spreadsheet', 'csv': 'text/comma-separated-values',
                              'xls': 'application/vnd.ms-excel' }
    _doc_content_types    = { 'doc': 'application/msword', 'odt': 'application/vnd.oasis.opendocument.text',
                              'rtf': 'application/rtf', 'sxw': 'application/vnd.sun.xml.writer',
                              'txt': 'text/plain' }
                               
    # Default formats the files are exported in
    _default_sheet_format = "ods"
    _default_doc_format   = "oo"

    # User agent sent to Google's servers
    _user_agent           = "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20061201 Firefox/2.0.0.6 (Ubuntu-feisty)"
    
    __author__            = "Devraj Mukherjee <devraj@gmail.com>"
    __version__           = "1.0.2"
    
    # Default constructors, basically sets up a few a things, much like logout
    def __init__(self):
        # Basically init does exactly what logout does, this reads a little
        # odd, but the functionality is much the same    
        self.logout()
        
    # Login authenticates a user account using the gdata and urllib2 methods
    # Addresses Issue 11, reported 2nd Nov 2007
    
    def login(self, username, password):
    
        # Establish a connection for the Google document feeds
        self._gd_client          = gdata.docs.service.DocsService()
        
        self._gd_client.email    = username
        self._gd_client.password = password
        self._gd_client.service  = "writely"
        
        self._gd_client.ProgrammaticLogin()
        
        # Lets set is Logged in to false before we start this process
        self._is_logged_in = False
        
        # We will try both login mechanims and see which one works        
        if self._perform_google_login(username, password):
            self._is_logged_in = True
            self._is_hosted_account = False
            return
        elif self._perform_hosted_login(username, password):
            self._is_logged_in = True
            self_is_hosted_account = True
            return
        else:
            raise SimluatedBrowserLoginFailed

    # Logout clears out all cookies, caches etc
    def logout(self):
        self._cookie_jar        = cookielib.CookieJar()
        self._is_logged_in      = False
        self._cached_doc_list   = []
        self._cached_sheet_list = []

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
        
        if self._sheet_content_types.has_key(file_extension):
            content_type = self._sheet_content_types[file_extension]
            media_source = gdata.MediaSource(file_path = document_path, content_type = content_type)
            entry = self._gd_client.UploadSpreadsheet(media_source, document_title)
        elif self._doc_content_types.has_key(file_extension):
            content_type = self._doc_content_types[file_extension]
            media_source = gdata.MediaSource(file_path = document_path, content_type = content_type)
            entry = self._gd_client.UploadDocument(media_source, document_title)
        else:
            raise InvalidContentType
            
        # At this point if entry is None then the file upload failed for some reason
        if entry == None:
            raise FailedToUploadFile

        return entry.GetAlternateLink().href
        
    # Export the metadata for a given document id
    def export_metadata(self, document_id, file_name):
        # If caches aren't availabe, make them now
        if len(self._cached_sheet_list) == 0:
            self._cached_sheet_list = self.get_spreadsheet_list()
        if len(self._cached_doc_list) == 0:
            self._cached_doc_list = self.get_document_list()

        # Find the document details
        doc_details = self.get_entry_details(document_id)
        
        if doc_details:
            md_file = open(file_name + ".txt", "w")
            md_file.write("Title: " + doc_details['title'] + "\n")
            md_file.write("Google id: " + doc_details['google_id'] + "\n")
            md_file.write("Author: " + doc_details['author_name'] + "\n")
            md_file.write("Email: " + doc_details['author_email'] + "\n")
            md_file.write("Last updated: " + doc_details['updated'] + "\n")
            md_file.close()
            return

        raise NoSuchGoogleDocument
        
    # Exports a Google document to a local file
    def export_document(self, document_id, file_format ="default", output_path = None):
        # Set file format to oo if user has chosen default
        if file_format == "default":
            file_format = self._default_doc_format
        # We must have a valid file format
        if not file_format in self._valid_doc_formats:
            raise InvalidExportFormat
        
        prepared_download_url = None
        
        if self._is_hosted_account:
            prepared_download_url = self._url_hosted_get_doc % (self._hosted_domain, file_format, document_id)
        else:
            prepared_download_url = self._url_google_get_doc % (file_format, document_id)
            
        if not prepared_download_url == None:
            self._export(prepared_download_url, output_path)
        else:
            raise DocumentDownloadURLError              
               
    # Exports a Google spreadsheet to a local file
    def export_spreadsheet(self, document_id, file_format = "default", output_path = None):
        # Set file format to ods if user has chosen default
        if file_format == "default":
            file_format = self._default_sheet_format
        # We must have a valid file format
        if not file_format in self._valid_sheet_formats:
            raise InvalidExportFormat
            
        prepared_download_url = None
        
        if self._is_hosted_account:
            prepared_download_url = self._url_hosted_get_sheet % (self._hosted_domain, file_format, document_id)
        else:
            prepared_download_url = self._url_google_get_sheet % (file_format, document_id)

        if not prepared_download_url == None:
            self._export(prepared_download_url, output_path)
        else:
            raise DocumentDownloadURLError
        
    # Caches the documents lists
    def cache_document_lists(self):
        self._cached_doc_list   = self.get_document_list()
        self._cached_sheet_list = self.get_spreadsheet_list()
        
    # Returns the currently cached list of documents
    def get_cached_document_list(self):
        return self._cached_doc_list
       
    # Returns the currently cached list of spreadhseets
    def get_cached_spreadsheet_list(self):
        return self._cached_sheet_list
        
    # Gets a live list of documents from Google
    def get_document_list(self):
        return self._get_item_list('document')
    
    # Gets a live list of spreadsheets from Google
    def get_spreadsheet_list(self):
        return self._get_item_list('spreadsheet')
        
    # Checks to see if a document or spreadsheet exists
    def has_item(self, document_id):
        return self.is_spreadsheet(document_id) or self.is_document(document_id)
        
    # Given a document id checks to see if its a spreadsheet
    def is_spreadsheet(self, document_id):
        # If the spreadsheet cache is empty the fill it up
        if len(self._cached_sheet_list) == 0:
            self._cached_sheet_list = self.get_spreadsheet_list()
            
        for document in self._cached_sheet_list:
            if document['google_id'] == document_id:
                return True
        return False
        
    # Given a document id checks to see if its a spreadsheet
    def is_document(self, document_id):
        # If the cache is empty then try and cache again
        if len(self._cached_doc_list) == 0:
            self._cached_doc_list = self.get_document_list()
            
        for document in self._cached_doc_list:
            if document['google_id'] == document_id:
                return True
        return False
        
    # Gets metadata information for an entry spreadsheet or document
    def get_entry_details(self, document_id):
        # Make an empty list so we dont have ifs and thens before
        # the for loop
        list_to_look = ()
        # Check to see if this is a valid doc or sheet
        if self.is_spreadsheet(document_id):
            list_to_look = self._cached_sheet_list
        if self.is_document(document_id):
            list_to_look = self._cached_doc_list
        
        # If its a document or a sheet then send back the details
        for entry in list_to_look:
            if entry['google_id'] == document_id:
                return entry

        # Document wasn't found so return a None            
        return None
    
    """
        Private functions to support various hacky Google POST requests, also 
        helps handle hosted or Google account variations
    """
 
    # Performs a Login Google style, also caters for private emails that
    # are able to use Google docs, refer to Issue 11 on code.google.com 
    # to see why these changes were made
       
    def _perform_google_login(self, username, password):
    
        login_data        = {'PersistentCookies': 'true', 'Email': username, 'Passwd': password, 
                             'continue': self._url_google_followup, 'followup': self._url_google_followup}
        prepared_auth_url = self._url_google_auth
        
        response = self._open_https_url(prepared_auth_url, login_data)
        return (len(self._cookie_jar) > 1)

    # Performs a login hosted account style        
    def _perform_hosted_login(self, username, password):

        app_username, self._hosted_domain = username.split('@')
        followup_url      = self._url_hosted_followup % self._hosted_domain
        login_data        = {'persistent': 'true', 'userName': app_username, 'password': password, 
                             'continue': followup_url, 'followup': followup_url}
        prepared_auth_url = self._url_hosted_auth % (self._hosted_domain)
        
        response = self._open_https_url(prepared_auth_url, login_data)
        return (len(self._cookie_jar) > 1)
    
    # Helper export function  
    def _export(self, download_url, file_name):
        if (not self._is_logged_in):
            raise NotLoggedInSimulatedBrowser
            
        try:
            response = self._open_https_url(download_url, post_data = None)
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
    def _get_item_list(self, item_type = None):
        if (not self._is_logged_in):
            raise NotLoggedInSimulatedBrowser

        item_list = []
        feed = self._gd_client.GetDocumentListFeed()
        feed_entries = feed.entry
        
        # Return to caller if there are no feed items
        if(len(feed_entries) == 0):
        	return item_list

        for entry in feed_entries:
            if self._is_item_of_type(entry.category, item_type):
                item_list.append({'title': entry.title.text.encode('UTF-8'), 
                                  'google_id': self._get_document_id(entry.GetAlternateLink().href), 
                                  'updated': entry.updated.text,
                                  'author_name': entry.author[0].name.text,
                                  'author_email': entry.author[0].email.text},)
        return item_list

    # Parses the document id out of the alternate link url, the atom feed
    # doesn't actually provide the document id      
    def _get_document_id(self, alternate_link):
    	parsed_url = urlparse(alternate_link)
    	url_params = parsed_url[4]
    	document_id = url_params.split('=')[1]
        return document_id
        
    # Checks to see if the item is of a particular type, document or spreadhseet
    # the Google atom library sends a tuple of categories    
    def _is_item_of_type(self, categories, item_type):
        for category in categories:
            if category.label == item_type:
                return True
        return False
    
    """
    
      Get a url opener, with proxy options
      urllib2 doesn't support the CONNECT command for pass through of proxies
      read this article for an excellent description of the issue
      http://www.voidspace.org.uk/python/articles/urllib2.shtml
    
    """
    
    def _open_https_url(self, target_url, post_data = None):
        # Opener will be assigned to either a proxy enabled or disabled opener
        opener    = None
        proxy_url = os.environ.get('http_proxy')
        
        if proxy_url:
            opener = urllib2.build_opener(ConnectHTTPHandler(proxy = proxy_url), ConnectHTTPSHandler(proxy = proxy_url), urllib2.HTTPCookieProcessor(self._cookie_jar))
        else:
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self._cookie_jar))

        # Proxy or not, add the headers and place the POST reuqest
        opener.addheaders = [('User-agent', self._user_agent)]
        
        response = None
        if post_data:
            response = opener.open(target_url, urllib.urlencode(post_data))
        else:
            response = opener.open(target_url)
            
        return response
        
"""
    End of Python API
"""
