

GDataCopier is an active project, the following is our road map, it outlines new features and bug fixes for upcoming releases.

Current features on board for development and release as\*v3.0

  * Python 2.7 compatibility
  * Complete rewrite of command line scripts
  * Doxygen generated documentation of API
  * Any document policy support for backup
  * File based configuration of scripts
  * Address various reported content encoding issues, unicode characters and other non latin scripts
  * GID based export
  * OAuth based authentication, so users don't have to provide usernames and passwords via command line or configuration files


## Releases ##

## v2.1.2 ##

Released: 18th August 2010

Second Service release for 2.1

  * Fixes download PDF as PDF issue
  * Fixes file name encoding issues for non ascii character sets
  * Allows long TLDs as remote server name .info etc
  * Tested against GData 2.0.11 and Python 2.5

## v2.1.1 ##

Released: 3rd April 2010

Service release for v2.1

  * Fixes minor typos
  * Drops file extensions for imported document names
  * Download PDF as PDF resolved
  * Traceback error message trapped on failures
  * Silent mode stops printing license and copyright

**Credits:**

  * mjbauer95 for the patches and ideas submitted

## v2.1 ##

Released: 31st January 2010

**New Features**

  * Introduce gmkdir to make directories on Google servers
  * Introduce gmv to move documents from one folder to another on Google servers
  * Introduce grm to remove documents and folders
  * Allow user to change verbosity
  * Fail gracefully on Captcha login requests
  * Read passwords from a file
  * Updated previously uploaded documents

**Credits**

  * remi for submitting the patch to read passwords from a file
  * Update contents of existing documents on Google servers, feature development sponsored by Patrick Hochstenbach of  [Universiteitsbiliotheek Gent](http://lib.ugent.be/)


## v2.0.2 ##

Released: 1st November 2009

Currently available by checking out code in Subversion.

**New Features**

  * Adds -c command line parameter, that creates a sub-directory per document owner for better organisation of backed up documents
  * Adds -i to append the document id of the user to the filename, the id is base64 hashed
  * Fixes issue with detecting updating documents (critical)

**Bug fixes**

  * Defaults to PPT for presentations, ODF doesn't seem to be supported

**Credits**

  * gdazero for the document id append idea
  * eszpee for suggesting the verbosity level idea
  * Radu Negrean of [Unique Logo Design](http://uniquelogodesign.com) for contributing the logo