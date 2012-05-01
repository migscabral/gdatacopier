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

__all__     = ['text']
__author__  = 'devraj (Devraj Mukherjee)'
__version__ = '3.0'

import datetime
import re

import gdata.service
import gdata.client

import gdatacopier.auth

## @brief Represents a single Docs Entry, abstracts properties required by GDataCopier
#
class GDocEntry(object):
    
    def __init__(self, resource):
        self._title = resource.title.text
        self._owner = None
        self._last_modified_date = resource.updated
        self._document_type = resource.GetResourceType()
        
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
    
    def __init__(self, auth_provider):

        self._auth_provider = auth_provider
                
        self._gd_client = gdata.docs.client.DocsClient(source='GDataCopier-v3')

        if self._auth_provider.is_logged_in():
            self._auth_provider.authorize_client(self._gd_client)
            
        self._gd_client.ssl = True

    ## @brief Filters and returns a list of documents
    #
    def get_docs_list(self, owner_filter=None, title_filter=None):
        
        documents = self._gd_client.GetAllResources()
        filtered_docs_list = []

        for resource in documents:
            filtered_docs_list.append(GDocEntry(resource))
            
        return filtered_docs_list