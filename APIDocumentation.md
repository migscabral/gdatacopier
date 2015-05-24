Please note that the development of the GDataCopier API will be discontinued as of the 2.0 RoadMap. Google now officially provides a mechanism to export documents as part of the 1.3 GData API.

Thanks for your interest and using the GDataCopier API in the past.

## API documentation ##

GoogleDocCopier is a class that consits of the following methods, here is a brief commentary on each of them.

**def login(self, username, password):**
> Used to perform a login using the GData API and urllib2

> This method may raise the following exceptions:
    * NotLoggedInSimulatedBrowser
    * SimluatedBrowserLoginFailed
    * NotEnoughCookiesFromGoogle

**def logout(self):**

> Closes all connections and re-sets instance variables to default values. May be required if your script needs to re-login as multiple users.

**def export\_document(self, document\_id, file\_format, output\_path):**

> Exports a document, you will require to provide the Google document id, a file format that Google recognizes and a file name to write to.

> The GoogleDocFormat class helps you get the file\_formats right, the valid programmatic values are:

  * GoogleDocFormat.OOWriter
  * GoogleDocFormat.MSWord
  * GoogleDocFormat.PDF
  * GoogleDocFormat.RichText
  * GoogleDocFormat.Text

> This method may raise the following exceptions:
    * DocumentDownloadURLError
    * FailedToWriteDocumentToFile
    * FailedToDownloadFile
    * NotLoggedInSimulatedBrowser

**def import\_document(self, document\_path, document\_title = None):**
> Detects the content type of a document and accordingly imports it as a spreadsheet or a document. If a title is not provided, the first part of the file name will be used as the title.

> This method may raise the following exceptions:
    * FileNotFound
    * InvalidContentType
    * FailedToUploadFile

**def export\_spreadsheet(self, document\_id, file\_format, output\_path = None):**

**def cache\_document\_lists(self):**
> Calls get\_document\_list and get\_spreadsheet\_list and stores the output into two instance variables. This minimizes the number of restful calls that we make if we are downloading a whole bunch of documents.

> You don't have to use the caching features if you don't want to.

**def get\_cached\_document\_list(self):**
> Returns a set [.md](.md) of documents entries that have been previously cached. If the cache is empty, the method will download a live list, cache it and return the cached list.

**def get\_cached\_spreadsheet\_list(self):**

**def get\_document\_list(self):**

**def get\_spreadsheet\_list(self):**
> Returns a set [.md](.md) of dictionaries {} of spreadsheet information live from the Google servers. Each dictionary entry contains:

  * updated, the last update date for the document
  * google\_id, the document id extracted from the alternate url
  * title, the descriptive title for the document

**def has\_item(self, document\_id):**
> Checks to see if the provided Google document id exists. Returns True or False

**def is\_spreadsheet(self, document\_id):**
> Checks to see if the provided Google document id is a spreadsheet or not. Returns True or False.

**def is\_document(self, document\_id):**
> Checks to see if the provided Google document id is a document or not. Returns True or False