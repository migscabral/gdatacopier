#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  gdatacopier, Command line utilties to manage your Google docs
#  http://gdatacopier.googlecode.com
#
#  Copyright (c) 2012, Eternity Technologies Pty Ltd.
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

__all__     = ['Handler']
__author__  = 'devraj (Devraj Mukherjee)'
__version__ = '3.0'

import webbrowser
import socket
import datetime
import keyring
import re

import gdata.service
import gdata.client

import gdatacopier.auth

## @brief Represents a single Docs Entry, abstracts properties required by GDataCopier
#
class GDocEntry(object):
    
    def __init__(self, title, owner, last_modified_date, document_type):
        self._title = title
        self._owner = owner
        self._last_modified_date = last_modified_date
        self._document_type = document_type
        
    @property
    def title(self):
        return self._title
        
    @property
    def document_type(self):
        return self._document_type
        
    @property
    def date_string(self):
        updated_time = datetime.datetime(*map(int, re.split('[^\d]', self._last_modified_date.text)[:-1]))
        date_string = updated_time.strftime('%b %d %Y %H:%M')
        return date_string
        
    
## @brief Proxy client that encapsulates the use of GData Client
#
class GDocClientProxy(object):
    
    def __init__(self, docs_client):
        self._gd_client = docs_client
        self._gd_client.xoauth_requestor_id = "brad@etk.com.au"
        
    @property 
    def auth_token(self):
        return self._gd_client.auth_token
        
    @auth_token.setter
    def auth_token(self, value):
        self._gd_client.auth_token = value
        
    def get_docs_list(self, owner_filter=None, title_filter=None):
        
        documents = self._gd_client.GetAllResources()
        filtered_docs_list = []

        for resource in documents:
            filtered_docs_list.append(GDocEntry(resource.title.text, None, last_modified_date=resource.updated, document_type=resource.GetResourceType()))
            
        return filtered_docs_list

## @brief Wrapper to encapsulate the user experience
#
#
#
class Handler(object):
    
    def __init__(self, args):
        
        self._args = args.__dict__

        _gd_client = gdata.docs.client.DocsClient(source='GDataCopier-v3')
        _gd_client.ssl = True        

        self._auth_provider = gdatacopier.auth.Provider(
            client_id=gdatacopier.OAuthCredentials.CLIENT_ID, 
            client_secret=gdatacopier.OAuthCredentials.CLIENT_SECRET)

        self._proxy_client = GDocClientProxy(docs_client=_gd_client)
            
        # If Logged in ensure we restore the access token
        if self._auth_provider.is_logged_in():
            self._proxy_client.auth_token = self._auth_provider.get_access_token()
            
        
    ## @brief Attemptes to perform OAuth 2.0 login
    #
    #  If the user has an accessible browser the webbrowser package will attempt to 
    #  automatically redirect them to the URL, on headless machiens the user is
    #  excepected to copy and paste the prompted URL into a browser.
    #
    #  Once the authenticaiton is complete, the user is expected to hit enter to
    #  allow GDataCopier to complete the authentcation process.
    #
    def login(self):

        if self._auth_provider.is_logged_in():
            print "already logged in, try logging out."
            return
            
        try:

            auth_url = self._auth_provider.get_auth_url()
            
            if not auth_url:
                print "having trouble getting an auth url, check your network and try again"
                
            if not webbrowser.open(auth_url):
                print "visit %s to authorise GDataCopier to use your account" % auth_url
                
            raw_input("once, you've authorised GDataCopier, hit enter to continue")

            self._proxy_client.auth_token = self._auth_provider.get_access_token()
                        
        except socket.gaierror:
            print "can't talk to Google servers, problem with your network?"
        except gdata.client.RequestError:
            print "unable to get OAuth token from Google, hit enter too soon?"
        except keyring.backend.PasswordSetError:
            print "error writing to keychain"
          
    ## @brief Revokes a OAuth token if available
    #  
    def logout(self):
        
        try:
            self._auth_provider.logout()
            print "successfully revoked OAuth token, user logged out."
            
        except gdata.service.NonOAuthToken:
            print "no OAuth token found, logout failed."
        except keyring.backend.PasswordSetError:
            print "error writing to keychain"
            
            
    ## @brief Lists filtered list of documents on Google servers
    #
    def list(self):
        
        for doc in self._proxy_client.get_docs_list():
            print "%-40s %-18s %s" % (doc.title[0:39], doc.date_string, doc.document_type)
        
            
            