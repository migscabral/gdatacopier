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
import gdata.service
import gdata.client

import gdatacopier.auth

class Handler(object):
    
    def __init__(self, args):
        self._gd_client = gdata.docs.client.DocsClient(source='GDataCopier-v3')
        self._auth_provider = gdatacopier.auth.Provider(docs_client=self._gd_client)
        self._args = args.__dict__
        
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
        
        try:

            google_apps_domain = self._args['apps-domain']
            auth_url = self._auth_provider.get_auth_url(google_apps_domain)
            
            if not auth_url:
                print "having trouble getting an auth url, check your network and try again"
                
            if not webbrowser.open(auth_url):
                print "visit %s to authorise GDataCopier to use your account" % auth_url
                
            raw_input("once, you've authorised GDataCopier, hit enter to continue")

            access_token = self._auth_provider.get_access_token()

        except socket.gaierror:
            print "can't talk to Google servers, problem with your network?"
        except gdata.client.RequestError:
            print "unable to get OAuth token from Google, hit enter too soon?"
          
    ## @brief Revokes a OAuth token if available
    #  
    def logout(self):
        
        try:
            self._auth_provider.logout()
            print "successfully revoked OAuth token, user logged out."
            
        except gdata.service.NonOAuthToken:
            
            print "no OAuth token found, logout failed."
            