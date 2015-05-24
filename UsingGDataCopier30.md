**WARNING**: This is documentation for the current DevelopmentNotes30 version. If you wish to use this then please refer to the [svn branch](http://code.google.com/p/gdatacopier/source/browse/#svn%2Fbranches%2F3.0).

# Installation #

Currently available only via SVN.

## Requirements ##

  * Python 2.6+
  * [GData Client Library](http://code.google.com/p/gdata-python-client/downloads/list) 2.0.16+ (Ubuntu users please ensure you have the right version).
  * Ability to establish HTTPS connections, check if you are using Proxies.
  * [Python Keyring](http://pypi.python.org/pypi/keyring), available via easy\_install or PIP.

Was developed and tested under OS X, tested under Linux. If you are using Windows and find any issues please report it to us.

# Authentication #

These will be stored in the user's [Keyring](http://pypi.python.org/pypi/keyring). Please note you will need Keyring support installed, generally available by default on OS X, Linux and Windows.

## Logging In ##

GDataCopier uses three legged OAuth to login to the Docs service, it's able to remain logged in, this is handy if you are scripting GDataCopier to automate backups.

```
gdc login 
```

If the machine running GDataCopier has a graphical interface and Web browser, GDataCopier will attempt to launch your browser and allow you to login.

If you are using GDataCopier on a headless box, it will provide you a URL that you must copy / paste in a browser and grant access after Login.

## Logging Out ##

If you have chosen to store your credentials using Keyring, you can use the logout command to revoke access as follows.

```
gdc logout
```

## Default username and impersonating users ##

# Asking for help #

# Operations #

## Copy ##

## List ##

Once you've logged in you can list documents by using

```
gdc list
```

GDataCopier does not filter on the type of document because you can use standard Unix tools like grep to achieve that result, e.g

```
gdc list | grep spreadsheet
```

## Delete ##

## Sync ##

## Directories ##