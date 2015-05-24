## Dependencies ##

Everything works and works really well, but since GDataCopier works around the current limitations of the Google Data API, here is what it assumes. If any of this is changed by Google GDataCopier will cease to work.

  * POST parameters for the login request
  * Dependencies on Cookies to maintain an authenticated session
  * GET parameters for the export requests
  * List of accepted User-agent values
  * Accessing the GET requests over HTTPS (GDataCopier conducts all its transactions over HTTPS)

## GData API ##

Google make available an API that allows people to list documents via Atom feeds. Each document in Google docs is identified using a docment id. The API has various functions to be able to upload content into the Google document server but none to extract documents out.


The GData API is a set of RESTful calls to the Google servers, along with managing cookies and session ids. The API is available for various languages and in this case Python.


The session information and cookies retruned using the GData API don't  provide enough authority to access the URLs that allow us to export  documents published using Google docs.


GoogleDocCopier uses the GData API to obtain information about documents but creates another connection using the Python urllib2 libraries to  download the documents

## Google is fussy about User agents ##

Google's servers are really fussy about unknown user agents. I found this the hard way, by sending various POST requests and wondering why they were getting redirected.

All requests must be accompanied with a known User-agent. GoogleDocCopier pretends to be FireFox 2.0.0.6.

## Login POST request ##

To be able to download documents by making RESTful URL calls to the Google servers, we have to first be able to login and get a copy of the Cookies set by the authentication server.

This is done by sending a POST request to https://www.google.com/accounts/ServiceLoginAuth

We need to send the following POST data:

  * PersistentCookies: true
  * Email: username@gmail.com
  * Passwd: password
  * continue: Is the URL you get redirected to after login
  * followup: Same as above, used at different instances

Notice that the value of PersistentCookies is set to true, this sends back a copy of the cookies for us to use later. Look at the login function in gdatacopier.py for a Python implementation of the above.

If the authentication succeeded we will get at least 2 cookies back and a request to redirect outselves to the location specified by the continue or  followup parameter

A Wget example of the above POST request would look like

```
wget --save-cookies cookies.txt --post-data"continue=http://docs.google.com&followup=http://docs.google.com&
Email=devraj&Passwd=password&PersistentCookie=true" https://www.google.com/accounts/ServiceLoginAuth?service=writely -O file.txt -c
```

## Handling Cookies and Redirects ##

The authentication servers send about three HTTP redirects, primarily to check for Cookies, Browsers, and then finally a page that has a META tag and some JavaScript to redirect the user to the value in continue or followup (POST parameters).

In this case urllib2 will handle all the redirect requests and end up with the contents of the final page. We will ignore the final redirect request since its sent as HTML content.

## Downloading the document using a GET requests ##

Once you have logged in downloading the document can be done by making the following GET requests. Note that the User-agent must be set to something popular otherwise your reuqest will be rejected.

You will need to load the cookies file and you will need to provide a meaningful file name to save the output to. The GET will need to contain the following variables

  * command - tells the web application what to do
  * exportformat - a valid export format string
  * docID - Google ID of the document you are interested in

Here is a Wget example to download a document

```
wget --user-agent "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20061201 Firefox/2.0.0.6 (Ubuntu-feisty)" 
--load-cookies cookies.txt -O somedoc.odf 
"http://docs.google.com/MiscCommands?command=saveasdoc&exportformat=oo&docID=docment_id"
```

## Hosted versus Normal Google accounts ##

URLs for Hosted accounts differ from the URLs for normal Google accounts for all the above examples. GoogleDocCopier will use the appropriate URLs based on the nature of the user account.

Presentation export works similar to document downloads

Hosted accounts URLs look like, where yoursdomain.com is the hosted domain

  * Authentication URL, https://www.google.com/a/yourdomain.com/LoginAction
  * Portal page for documents, http://docs.google.com/a/yourdomain.com/
  * Documents download URL, http://docs.google.com/a/yourdomain.com/MiscCommands?command=saveasdoc&exportformat=oo&docID=docid
  * Spreadsheet download URL, http://spreadsheets.google.com/a/yourdomain.com/pub?output=odf&key=docid

## Related resources ##
  * [Downloading Google documents](http://googlesystem.blogspot.com/2007/07/download-published-documents-and.html)
  * [Python HTTPS Proxy](http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/456195)