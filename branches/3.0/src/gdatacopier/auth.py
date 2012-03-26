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

import gdata.gauth
import gdata.docs.client

import keyring
    
class Provider(object):

    def __init__(self, docs_client, consumer_key='anonymous', consumer_secret='anonymous'):

        self._consumer_key = consumer_key
        self._consumer_secret = consumer_secret
        
        self._scopes = ['https://docs.google.com/feeds/']
        
        self._gd_client = docs_client
        
    def is_logged_in(self):
        return False
            
    def get_auth_url(self, app_domain=None):

        self._request_token = self._gd_client.GetOAuthToken(self._scopes, None, self._consumer_key, consumer_secret=self._consumer_secret)
        
        auth_url = None
        if app_domain:
            auth_url = self._request_token.generate_authorization_url(google_apps_domain=app_domain)
        else:
            auth_url = self._request_token.generate_authorization_url()
            
        return str(auth_url)
        
    def get_access_token(self):
        
        access_token = None
        
        if self.is_logged_in():
            pass
        else:
            access_token = self._gd_client.GetAccessToken(self._request_token)

        return access_token
                
    def get_client(self):
        return self._gd_client

    def logout(self):
        self._gd_client.RevokeOAuthToken()
        
        
    
    