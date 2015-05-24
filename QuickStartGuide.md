### v2.x Usage Examples ###

Here's a quick overview of how you would typically use GDataCopier utilities. The [wiki](http://code.google.com/p/gdatacopier/wiki) has a detailed manual page for each utility.

#### gcp ####

Export all documents for username@gmail that have changed since the last sync, and overwrite them if they already exists on the local system

```
./gcp.py -o -u username@gmail.com:/sheets /tmp
```

Export all documents where title matches Over for username@gmail.com as PDF

```
./gcp.py -f pdf username@gmail.com:/docs/all/Over* /tmp/
```

Export all presentations for username@gmail.com to /tmp

```
./gcp.py username@gmail.com:/slides /tmp
```

Imports all accepted files from /home/devraj to username@gmail.com. All unsupported formats will be ignored. gcp doesn't support recursively reading directories.

```
./gcp.py /home/devraj/ username@gmail.com:/
```

Imports Manual.doc to the Documentation folder for username@gmail.com, ensure that the folder exists on the Google document system.

```
./gcp.py /home/devraj/Manual.doc username@gmail.com:/Documentation
```


#### gls ####

List all documents for username@gmail.com in the Documentation folder

```
./gls.py username@gmail.com:/docs/Documentation
```

List all documents for username@gmail.com where the title contains the string GTE

```
./gls.py username@gmail.com:/docs/Documentation/GTE*
```

List all objects in the folder Documentation for username@gmail.com

```
./gls.py username@gmail.com:/all/Documentation
```


#### gmkdir ####

Make a folder called Documentation on the Google docs system

```
./gmkdir.py username@gmail.com:/Documentation
```

#### grm ####

Remove all documents that match GTE in the title

```
./grm.py username@gmail.com:/docs/all/GTES*
```