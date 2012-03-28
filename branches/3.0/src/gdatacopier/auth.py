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

## @brief 
#
#

import gdatacopier

import gdata.gauth
import gdata.docs.client

import keyring


## @brief
#
class KeyRingProxy(object):
    
    def __init__(self):
        self._service_name = "GDataCopier"
    
    @property
    def token(self):
        return keyring.get_password(self._service_name, 'token')
        
    @token.setter
    def token(self, value):
        keyring.set_password(self._service_name, 'token', value)
        
    @property
    def token_secret(self):
        return keyring.get_password(self._service_name, 'token_secret')
        
    @token_secret.setter
    def token_secret(self, value):
        keyring.set_password(self._service_name, 'token_secret', value)
    
## @brief
#
class Provider(object):

    def __init__(self, client_id='anonymous', client_secret='anonymous'):

        self._client_id = client_id
        self._client_secret = client_secret
        self._keyring_proxy = KeyRingProxy()
        
        self._scopes = ['https://docs.google.com/feeds/']
        
    def is_logged_in(self):
        return self._keyring_proxy.token and self._keyring_proxy.token_secret
            
    def get_auth_url(self):

        #self._request_token = self._gd_client.GetOAuthToken(self._scopes, None, self._client_id, consumer_secret=self._client_secret)
        self._request_token = gdata.gauth.OAuth2Token(
           client_id=self._client_id, 
           client_secret=self._client_secret, 
           scope=' '.join(self._scopes),
           user_agent=gdatacopier.OAuthCredentials.USER_AGENT)
           
        auth_url = self._request_token.generate_authorize_url(redirect_url="http://localhost")
        return str(auth_url)
        
    def get_access_token(self):
        
        access_token = None
        
        if self.is_logged_in():
            access_token = gdata.gauth.OAuthHmacToken(self._client_id, self._client_secret, self._keyring_proxy.token, self._keyring_proxy.token_secret, gdata.gauth.ACCESS_TOKEN)
        else:
            #access_token = self._gd_client.GetAccessToken(self._request_token)
            access_token = self._request_token.get_access_token()
            self._keyring_proxy.token = access_token.token
            self._keyring_proxy.token_secret = access_token.token_secret

        return access_token
                
    def logout(self):
        self._keyring_proxy.token = ""
        self._keyring_proxy.token_secret = ""
        
        
    
    