#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  gdatacopier, Command line utilities to manage your Google docs
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
import mimetypes
import re

import gdata.service
import gdata.client

import gdatacopier.auth

class RegexPatterns:
    
    EMAIL_AND_PATH = re.compile('([\w\-\.+]+@(\w[\w\-]+\.)+[\w\-]+:/[\w\-]+:^(.+)/([^/]+)$)')

## @brief Wrapper to encapsulate the user experience
#
#
#
class Handler(object):
    
    def __init__(self, args):
        
        self._args = args.__dict__

        self._auth_provider = gdatacopier.auth.Provider(
            client_id=gdatacopier.OAuthCredentials.CLIENT_ID, 
            client_secret=gdatacopier.OAuthCredentials.CLIENT_SECRET,
            scope=gdatacopier.OAuthCredentials.SCOPE,
            user_agent=gdatacopier.OAuthCredentials.USER_AGENT)

        self._proxy_client = gdatacopier.ui.GDocClientProxy(auth_provider=self._auth_provider)
            
        
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
                
            token = raw_input("paste the auth token from your browser here: ")
            
            refresh_token = self._auth_provider.get_access_token(token)
                        
        except socket.gaierror:
            print "can't talk to Google servers, problem with your network?"
        except gdata.gauth.OAuth2AccessTokenError:
            print "unable to get OAuth token from Google, hit enter too soon?"
        except keyring.backend.PasswordSetError:
            print "error writing to keychain"
          
    ## @brief Revokes a OAuth2 token if available
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
        
        try:

            totals = {}
        
            for doc in self._proxy_client.get_docs_list():

                printable_name = doc.document_type

                if mimetypes.guess_extension(doc.document_type):
                    printable_name = mimetypes.guess_extension(doc.document_type)[1:]
            
                print "%-40s %-18s %s" % (doc.title[0:39], doc.date_string, printable_name)
            
                if doc.document_type in totals:
                    totals[doc.document_type] = totals[doc.document_type] + 1
                else:
                    totals[doc.document_type] = 1
            
            self._print_totals_string(totals)
        
        except gdata.client.Unauthorized:
            
            print "you are either not logged in or are not allowed impersonate this user"
        
        
    ## @brief Turns a totals summary and prints out the string
    #
    def _print_totals_string(self, totals):
        
        totals_summary = ""
        for type_name, type_count in totals.items():

            printable_name = type_name

            if mimetypes.guess_extension(type_name):
                printable_name = mimetypes.guess_extension(type_name)[1:]
                
            totals_summary = "%s%i %s(s), " % (totals_summary, type_count, printable_name)
            
        print "\n%s" % totals_summary[:-2]
        
