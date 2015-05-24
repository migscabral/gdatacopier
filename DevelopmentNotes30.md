

# Introduction #

This is a working document for GDataCopier 3.0 development. Most of this information will eventually end up as official documentation for this project.

Follow the development branch [here](https://gdatacopier.googlecode.com/svn/trunk)

## Feature Set ##

GDataCopier aims to deliver these new features

  * OAuth 2.0 login, we might drop username / password based logins completely - **completed**
  * Admin level user impersonation support for Google Apps users
  * Sync option, to prune documents on the local machine as they are deleted on the Cloud
  * Support and test any document policy
  * API documentation via [Doxygen](http://www.stack.nl/~dimitri/doxygen/)

Also check the [Issues list](http://code.google.com/p/gdatacopier/issues/list), we will fix all reported bugs.

## System Requirements ##

  * Python 2.6+
  * [GData Client Library](http://code.google.com/p/gdata-python-client/downloads/list) 2.0.16+
  * Ability to establish HTTPS connections, check if you are using Proxies.

Was developed and tested under OS X, tested under Linux. If you are using Windows and find any issues please report it to us.

## GData API ##

GDataCopier is written in Python and uses the [GData Python API](http://code.google.com/apis/documents/docs/3.0/developers_guide_python.html).

# Programming references #

  * [Adding Colour to Linux Command line utilities](http://travelingfrontiers.wordpress.com/2010/08/22/how-to-add-colors-to-linux-command-line-output/), talks about Python command line utilities.
  * [Setup mime types for Subversion repo](http://wisdom.etk.com.au/index.php/Setting_up_mime-types_for_serving_HTML_content_out_of_Subversion), useful for Doxygen based documentation.
  * [Python Keyring](http://pypi.python.org/pypi/keyring)
  * [Python OAuth Two legged example](http://code.google.com/p/gdata-python-client/source/browse/samples/oauth/TwoLeggedOAuthExample.py), demonstrates user impersonation.
  * [Python mimetype package](http://docs.python.org/library/mimetypes.html)
  * [Managing the OAuth key and secret](http://support.google.com/a/bin/answer.py?hl=en&answer=162105)
  * [Python Web Browser Controller API](http://docs.python.org/library/webbrowser.html), allows controlling a Web browser via  a Python script.
  * [Three Legged OAuth sample](http://code.google.com/p/gdata-python-client/source/browse/samples/oauth/oauth_example.py)
  * [Using administrative access to impersonate other domain users](http://packages.python.org/gdata/docs/impersonating.html), explains how you can impersonate users if you are an Apps domain admin.

# Authentication #

Authentication switched to OAuth 2.0, you will **no longer** be able to use Username / Password based Authentication, instead you must authorise against Google's authentication service.

This allows impersonating domain users if you are logged in as an Administrator.

  * [OAuth in the Google Data Protocol Client Libraries](http://code.google.com/apis/gdata/docs/auth/oauth.html#NoLibrary)
  * [OAuth 2 login on the client side](http://code.google.com/p/google-api-python-client/wiki/OAuth2), examples, tips and tricks.
  * [2 Legged OAuth in Python](http://gdatatips.blogspot.com.au/2008/11/2-legged-oauth-in-python.html), blog post from Google developer blog.
  * [OAuth 2.0 Python example](http://googleappsdeveloper.blogspot.com.au/2011/09/python-oauth-20-google-data-apis.html)
  * [OAuth 2.0 with the Provisioning and Email Settings APIs](http://code.google.com/googleapps/domain/articles/provisioningoauth2console.html), provides a good example of using OAuth 2 for Python command line applications. _Note_: Token has to be copied and pasted from the browser, OAuth for command line apps doesn't allow auto fetch of tokens.

[OAuth key and secret](http://support.google.com/a/bin/answer.py?hl=en&answer=162105) is available for Google Apps domains only.

GDataCopier will use a three legged OAuth routine to ensure all Google accounts are supported [three legged OAuth](http://code.google.com/apis/gdata/docs/auth/oauth.html).

These will be stored in the user's [Keyring](http://pypi.python.org/pypi/keyring). Please note you will need Keyring support installed, generally available by default on OS X, Linux and Windows.

# OAuth 2 authentication lifecycle #

```
>>> import gdata.gauth
>>> import gdata.docs.client
>>> token = gdata.gauth.OAuth2Token(client_id="351782124357.apps.googleusercontent.com", client_secret="xC3varEAS9pq--71p22oFoye", scope="https://docs.google.com/feeds/", user_agent="GDataCopier")
>>> token.generate_authorize_url(redirect_url="urn:ietf:wg:oauth:2.0:oob")
'https://accounts.google.com/o/oauth2/auth?redirect_url=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob&scope=https%3A%2F%2Fdocs.google.com%2Ffeeds%2F&redirect_uri=oob&response_type=code&client_id=351782124357.apps.googleusercontent.com'
>>> token.get_access_token("4/rs66xrzTNHkPsHj_0fi0ykH4Hxze")
<gdata.gauth.OAuth2Token object at 0x109ba2510>
>>> gd_client = gdata.docs.client.DocsClient(source='GDataCopier-v3')
>>> token.authorize(gd_client)
<gdata.docs.client.DocsClient object at 0x109ba2710>
>>> gd_client.GetAllResources()
```

## Refresh token example ##

Refresh tokens can be used to restore the session. Here's an example.

```
>>> my_refresh_token = token.refresh_token
>>> token2 = gdata.gauth.OAuth2Token(client_id="351782124357.apps.googleusercontent.com", client_secret="xC3varEAS9pq--71p22oFoye", scope="https://docs.google.com/feeds/", user_agent="GDataCopier", refresh_token=my_refresh_token)
>>> gd_client2 = gdata.docs.client.DocsClient(source='GDataCopier-v3')
>>> token2.authorize(gd_client2)
```

# Documentation #

Documentation of the internal API is generated via Doxygen, and is available via the [Subversion repository](http://gdatacopier.googlecode.com/svn/trunk/docs/html/index.html).