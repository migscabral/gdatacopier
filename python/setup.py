#!/usr/bin/env python

"""
    setup.py, Copyright (c) 2008 Eternity Technologies Pty Limited
    http://code.google.com/p/gdatacopier/
    Released under the terms and conditions of the GNU/GPL

	Version 1.0.3
	
	Developed by Eternity Technologies 

	This is free software, and comes with ABSOLUTELY NO WARRANTY use of 
	this software is completely at your OWN RISK.
           
"""

from distutils.core import setup

setup(name='GDataCopier',
      version='1.0.3',
      description='Bi-directional copy utility for Google Documents and Spreadsheets',
      author='Devraj Mukherjee',
      author_email='devraj@gmail.com',
      url='http://code.google.com/p/gdatacopier/',
      packages=['distutils', 'distutils.command'],
     )
