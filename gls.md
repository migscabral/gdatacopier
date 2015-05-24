### Introduction ###

Since 2.0 we have split our utility in two, the first gls which provides ways of listing various documents and the second gcp, which allows you to copy files to-and-from your computer to the Google servers.

gls does more than listing documents, it can filter the document list feed based on parameters that you provide, it's behaviour is quite close to that of ls apart from its sytax.

The server string closely resembles scp, please read the documentation to

### Requirements ###

  * Python 2.4
  * GData Python API 2.0.2+

Tested under Mac OSX and Linux. Windows testing pending.

### Usage ###

gls.py [options](options.md) username@gmail.com:/[doctype](doctype.md)/foldername/Pattern

Both doctype and foldername are optional parameters, doctype may have the value of all, docs, sheets, slides, pdf

If you provide a Pattern string the title of the document will be matched, an asterisk at the end of the Pattern string will make the title search non-exact.

### Parameters ###

-p or --password to provide passwords in the command line
-d or --debug to increase verbosity, prints Python error messages as well
-h or --help to print out help screen


### Usage examples ###

List all documents, sheets, slides for username@gmail.com

```
./gls.py username@gmail.com:/
```

List all folders for username@gmail.com

```
./gls.py username@gmail.com:/folders
```

List all sheets for username@gmail.com

```
./gls.py username@gmail.com:/sheets
```

List all documents for username@gmail.com in the Documentation folder

```
./gls.py username@gmail.com:/docs/Documentation
```

List all documents for username@gmail.com where the title contains the string GTE

```
./gls.py  username@gmail.com:/docs/Documentation/GTE*
```

List all objects in the folder Documentation for username@gmail.com

```
./gls.py username@gmail.com:/all/Documentation
```

List all documents for username@gmail.com in all where the title contains the words Over

```
./gls.py username@gmail.com:/docs/all/Over*
```