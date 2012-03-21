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

class Handler(object):
    
    def __init__(self, auth_provider, args):
        self._auth_provider = auth_provider
        self._args = args
        
    def login(self):
        
        try:

            auth_url = self._auth_provider.get_auth_url()
            if not auth_url:
                print "having trouble getting an auth url, check your network and try again"
                
            if not webbrowser.open(auth_url):
                print "visit %s to authorise GDataCopier to use your account"

        except socket.gaierror:
            print "can't talk to Google servers, problem with your network?"
            