### Introduction ###

gcp allows you to export or import documents to and from the Google document system. It's usage largely resembles scp. gcp syncs the local time stamp with that of the remote server time stamp. Combined with the "update" option it allows you to download documents that have changed on the Google servers since you last run your backup.

```
./gcp.py username@gmail.com:/[doctype]/[foldername]/Over* /local/path
```

doctype and foldername can be set to to the reserved word "all" where appropriate.

and `Over*` is the name of the document, the asterisk indicates that gcp should copy all documents that start with Over.

### Options ###

-u or --update downloads documents that have been updated on the remote server, ensure that you are syncing back to the same directory

-o or --overwrite forcefully overwrites any documents on the local folders, ensure you use this with the above option

-p or --password provides password in the command line

-f or --format export the files in a specific format, if not provided gcp chooses the open document formats. Please ensure you use a common format when exporting a combination of document types. Or refer to the section below for details on export formats.

-c creates directories per document owner username

-i adds a base64 hash of the document at the end of the file name

### Usage samples ###

Imports all accepted files from /home/devraj to username@gmail.com. All unsupported formats will be ignored. gcp doesn't support recursively reading directories.

```
./gcp.py /home/devraj/ username@gmail.com:/
```

Imports Manual.doc to the Documentation folder for username@gmail.com, ensure that the folder exists on the Google document system.

```
./gcp.py /home/devraj/Manual.doc username@gmail.com:/Documentation
```

Export all documents for username@gmail that have changed since the last sync, and overwrite them if they already exists on the local system

```
./gcp.py -o -u username@gmail.com:/sheets /tmp
```

Export all documents for username@gmail.com to /tmp

```
./gcp.py username@gmail.com:/docs/all/Over* /tmp/
```

### Cool examples ###

And now for my favourite, using gcp as a PDF convertor (if you haven't figured this out yet), upload a text or document using the following command

```
./gcp.py TextFileToConvertToPDF.txt username@gmail.com:/
```

The above command would create a document with the file name as the document title.

Ask gcp to export all documents that have the name TextFileToConvertToPDF back as a PDF. Obviously this is not deleted from the Google document system.

```
./gcp.py -f pdf username@gmail.com:/all/all/TextFileToConvertToPDF* .
```

### Formats ###

Google defines a list of formats that you can import / export documents in, they are centric to the type of document you are exporting or importing. The following are the accepted list of formats:

Documents:

  * doc
  * html
  * zip
  * odt
  * pdf
  * png
  * rtf
  * txt

Presentations:
  * pdf
  * png
  * ppt
  * swf
  * txt
  * zip
  * html
  * odt

Spreadsheets:

  * xls
  * ods
  * txt
  * html
  * pdf
  * tsv
  * csv

zip export the HTML file with all the require images.