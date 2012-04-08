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
        
    
## @brief
#
class Provider(object):

    def __init__(self, client_id, client_secret, scope, user_agent):

        self._keyring_proxy = KeyRingProxy()

        self._request_token = gdata.gauth.OAuth2Token(
           client_id=client_id, 
           client_secret=client_secret, 
           scope=' '.join(scope),
           user_agent=user_agent)
        
    def is_logged_in(self):
        return self._keyring_proxy.token
        
    def get_auth_url(self):

        auth_url = self._request_token.generate_authorize_url(redirect_url="urn:ietf:wg:oauth:2.0:oob")
        return str(auth_url)
        
    def set_access_token(self, token):
        self._keyring_proxy.token = token
        
    def authorize(self, client):
        return self._request_token.authorize(client)
                
    def logout(self):
        self._keyring_proxy.token = ""
        
        
    
    