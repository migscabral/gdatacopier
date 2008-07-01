#!/usr/bin/env python

"""
    setup.py, Copyright (c) 2008 Eternity Technologies Pty Limited
	http://gdatacopier.googlecode.com/
    Distributed under the terms and conditions of the GNU/GPL v3

	Version 1.0.3
	
	Developed by Eternity Technologies 

	This is free software, and comes with ABSOLUTELY NO WARRANTY use of 
	this software is completely at your OWN RISK.
           
"""

from distutils.core import setup

__author__ = "Devraj Mukherjee <devraj@gmail.com>"

setup(name='GDataCopier',
      version='1.0.3',
      description='Bi-directional copy utility for Google Documents and Spreadsheets',
      author='Devraj Mukherjee',
      author_email='devraj@gmail.com',
      url='http://code.google.com/p/gdatacopier/',
      package_dir=['': 'src'],
      packages=['gdatacopier'],
     )


# Post Install operations are done here

# Install gdoc-cp.py in a location accessible by all users /usr/bin

