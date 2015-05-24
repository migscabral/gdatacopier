All usage examples are written using the short options, gdoc-cp supports a set of long options (if you prefer that).

You must always provide a username (-u) and password (-p). If you don't the command line utility will ask you to provide this via standard in.

If you are  exporting or import documents you will require to provide a Google document id (-g) and or instruct the program to download or upload sets of documents. You will also require to provide a local path or file name (-f).

While exporting document you need to specify a valid export format (-e pdf). Import automatically detects the content type of the file.

### List documents ###

List all documents for a user
```
./gdoc-cp.py -u someone@gmail.com -p password -l
```

List only documents for a user
```
./gdoc-cp.py -u someone@gmail.com -p password -d
```

List only spreadsheets for a user
```
./gdoc-cp.py -u someone@gmail.com -p password -s
```

### Export documents and spreadsheets to local disk ###

Download a single document to disk
```
./gdoc-cp.py -u someone@gmail.com -p password -g documentid -f files/google
```

Download all spreadsheets to disk
```
./gdoc-cp.py -u someone@gmail.com -p password -g spreadsheets -f files/google
```

Download all documents to disk
```
./gdoc-cp.py -u someone@gmail.com -p password -g documents -f files/google
```

Download every document to disk (default, exports in OASIS formats)
```
./gdoc-cp.py -u someone@gmail.com -p password -e default -g all -f files/google
./gdoc-cp.py -u someone@gmail.com -p password -e pdf -g all -f files/google
```

### Importing documents to Google Docs ###

To create a new Google document called "New Document" from an OpenOffice file called sample.odt
```
./gdoc-cp.py -u someone@gmail.com -p password -i -f files/sample.odt -t "New Document"
```

### Document & spreadsheet metadata export ###

While exporting documents you can also export extra information that Google makes available via the Atom feeds by using the -m option

```
./gdoc-cp.py -u someone@gmail.com -p password -e default -g all -f files/google -m
./gdoc-cp.py -u someone@gmail.com -p password -e pdf -g all -f files/google -m
```