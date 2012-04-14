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

__all__     = ['Provider']
__author__  = 'devraj (Devraj Mukherjee)'
__version__ = '3.0'

## @brief Provides wrappers to OAuth2 authentication for Google servers
#
#

import gdatacopier

import gdata.gauth
import gdata.docs.client

import keyring


## @brief Provides a Proxy to the local Keychain service via Python's Keyring package
#
#  KeyRingProxy is used by the auth provider to store the OAuth 2 token, it can be used
#  to securely store any other properties that GDatacopier might require.
#
#  Python keyring support is provided by
#  http://pypi.python.org/pypi/keyring
#
#  available via pip or easy_install
#
class KeyRingProxy(object):
    
    def __init__(self):
        self._service_name = "GDataCopier"
    
    @property
    def refresh_token(self):
        return keyring.get_password(self._service_name, 'refresh_token')
        
    @refresh_token.setter
    def refresh_token(self, value):
        keyring.set_password(self._service_name, 'refresh_token', value)
        
    
## @brief Provides a Wrapper for OAuth 2 authentication against Google APIs
#
#  Uses refresh tokens to restore previously logged in sessions.
#
class Provider(object):

    def __init__(self, client_id, client_secret, scope, user_agent):

        self._keyring_proxy = KeyRingProxy()
        
        if self.is_logged_in():
            self._request_token = gdata.gauth.OAuth2Token(
               client_id=client_id, 
               client_secret=client_secret, 
               scope=' '.join(scope),
               user_agent=user_agent,
               refresh_token=self._keyring_proxy.refresh_token)
        else:
            self._request_token = gdata.gauth.OAuth2Token(
               client_id=client_id, 
               client_secret=client_secret, 
               scope=' '.join(scope),
               user_agent=user_agent)
            
    
    ## @brief Checks to see if user is logged in
    #
    def is_logged_in(self):
        return self._keyring_proxy.refresh_token
        
    ## @brief Get OAuth2 authentication URL
    #
    def get_auth_url(self):
        auth_url = self._request_token.generate_authorize_url(redirect_url="urn:ietf:wg:oauth:2.0:oob", access_type="offline")
        return str(auth_url)
        
    ## @brief Attempts to validate an OAuth2 token, on success saves refresh token
    # 
    #  @returns string refresh token obtained from login
    #
    def get_access_token(self, token):
        self._request_token.get_access_token(token)
        self._keyring_proxy.refresh_token = self._request_token.refresh_token
        return self._request_token.refresh_token
        
    ## @brief Authorizes a Google Docs client
    #
    def authorize_client(self, client):
        self._request_token.authorize(client)

    ## @brief Forget refresh token
    #
    def logout(self):
        self._keyring_proxy.refresh_token = ""
        
        
    
    