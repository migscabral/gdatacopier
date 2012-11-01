.. GDataCopier documentation master file, created by
   sphinx-quickstart on Fri Nov  2 08:29:17 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

GDataCopier, a command line utility to manage Google Docs
=========================================================


.. toctree::
   :maxdepth: 2

   installation
   credits


Features
========

GDataCopier provides comprehensive set of tools for System Administrators (mostly on Unix like platforms) to list, manage, backup and synchronise documents stored on Google's Document Service. Some major features are:

* scp like syntax to list and copy documents
* filter documents based on folders, file names
* supports hosted and gmail accounts
* syncs date stamps with server
* download updated files only (great for offsite backup implementations)
* warn on overwrite (can override with parameters)
* summary of operations
* update document content using gcp
* move, remove, or make directories and organise your documents
* choose export format using command line parameter (defaults to `OpenDocument <http://en.wikipedia.org/wiki/OpenDocument>`_ formats)

Requirements
============

* Python 2.6+
* `GData Client Library <http://code.google.com/p/gdata-python-client/downloads/list>`_ ``2.0.16+`` (Ubuntu users please ensure you have the right version).
* Ability to establish HTTPS connections, check if you are using Proxies.
* `Python Keyring <http://pypi.python.org/pypi/keyring>`_, available via easy_install or PIP.

Was developed and tested under OS X, tested under Linux. If you are using Windows and find any issues please report it to us.