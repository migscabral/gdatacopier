.. GDataCopier documentation master file, created by
   sphinx-quickstart on Fri Nov  2 08:29:17 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

GDataCopier, a command line utility to manage Google Docs
=========================================================

GDataCopier is a set of command line tools that ease management of Google Docs. GDataCopier is aimed towards power users / system adminstrators who are looking to automate management / backup of Google Docs. 

.. toctree::
   :numbered:
   :maxdepth: 2

   installation
   usage
   credits


Features
--------

GDataCopier provides comprehensive set of tools for System Administrators (mostly on Unix like platforms) to list, manage, backup and synchronise documents stored on Google's Document Service. Some major features are:

* scp like syntax to list and copy documents
* filter documents based on folders, file names
* supports hosted and gmail accounts
* syncs date stamps with server
* download updated files only
* warn on overwrite 
* summary of operations
* update document content using gcp
* move, remove, or make directories and organise your documents
* choose export format using command line parameter (defaults to `OpenDocument <http://en.wikipedia.org/wiki/OpenDocument>`_ formats)

Requirements
------------

* Python 2.6+
* `GData Client Library <http://code.google.com/p/gdata-python-client/downloads/list>`_ ``2.0.16+`` (Ubuntu users please ensure you have the right version).
* Ability to establish HTTPS connections, check if you are using Proxies.
* `Python Keyring <http://pypi.python.org/pypi/keyring>`_, available via easy_install or PIP.

Was developed and tested under OS X, tested under Linux. If you are using Windows and find any issues please report it to us.

Getting Help
------------

We encourge the use of our mailing lists (run on Google Groups) as the primary method of getting help. You can also write the developers through contact information `our website <http://etk.com.au>`_.

* `Discuss <http://groups.google.com/group/gdatacopier-discuss>`_ general discussion, help, suggest a new feature.
* `Announcements <http://groups.google.com/group/gdatacopier-announce>`_ security / release announcements.

Reporting Issues
^^^^^^^^^^^^^^^^

We prefer the use of our `Issue Tracker <https://code.google.com/p/gdatacopier/issues/list>`_ on Google Code, to triage feature requests, bug reports. 

Before you lodge a lodge a ticket:

* Ensure that you ask a question on our list, there might already be answer out there or we might have already acknowledged the issue
* Seek wisdom from our beautifully written documentation 
* Google to see that it's not something to do with your environment (versions of Pyton, GData Client library, etc)
* Check to ensure that you are *not* lodging a duplicate request.

When reporting issues:

* Include as much detail as you can about your environment (e.g OS, Python Version, Versions of libraries)
* Steps that we can use to replicate the bug
* Run GDataCopier in debug mode, to post more infomration on the error
