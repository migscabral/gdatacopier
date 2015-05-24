## Introduction ##

If you are behind a HTTP/HTTPS proxy then this document is for you, it outlines the environment variables you need to set to make GDataCopier work with proxies.

GDataCopier 2.0 does not use the Proxy directly, it depends on the GData API to handle the proxy and calls out to the Google servers.

The following is wisdom we have collected surfing the web, talking to the GData API developers and deployment experiences.

## Proxy and environment variables ##

The proxy handler implemented in GDataCopier excepts to an https:// address if you set the https\_proxy environment variable.

If you set it to a value starting with http:// it tries talk HTTP over an HTTPS connection which doesn't go so good.

GData API queries the environment for the http\_proxy variable for its use but the GData API requires you to set the https\_proxy variable.

## Howto ##

Simply export these variables using your shell before you run GDataCopier

  * _proxy-username_ with the proxy username
  * _proxy-password_ with the password for the proxy user
  * _http\_proxy_ with the url of the proxy to be used for http connections
  * _https\_proxy_ with the url of an HTTPS proxy that should be used, note this should start with https://

## BASH hyphen issues ##

If you are a BASH user then you will notice if you try and export a variable you will get the following error

```
surfboard:~/Work/gdatacopier devraj$ export proxy-username="username"
-bash: export: `proxy-username=username': not a valid identifier
```

## Working around BASH ##

You can use the env command to temporarily set the environment variables while you run GDataCopier.

```
env proxy-username="username" proxy-password="password" ./gls.py username@gmail.com:/sheets
```