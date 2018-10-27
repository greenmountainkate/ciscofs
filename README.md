## Cisco FSE File Parsing Exercise

Author: Katherine Brown

### Program Description

This program monitors a Watched folder, checking at 10 minute intervals for new .html files.  If new html files are found, the files
are sequentially parsed, the text is lightly cleaned, html headers and scripts are removed, as is extraneous whitespace and punctuation.
Files that experience parsing errors or with empty or missing html bodies are moved to the Error folder and a timestamped error message is logged in
the error_files collection of the database.  If the file is successfully parsed, a document is made in the parsed_files database,
which contains a unique id, stored in the _id field, the stripped headers as a list, which is stored in the headers field, and a
dictionary of keywords, each of which is a key for a list containing a tuple for each document where that keyword was found, containing the 
unique doc id and frequency in that document.  The cleaned text without headers is stored in the Clean Text folder, with the filename
format of "_id".txt where "_id" is the document's unique id from it's parsed_files document _id field.  Finally, the original file is moved
from the Watched folder to the Parsed Files folder.

This project was written on Fedora and tested on RHEL 7 running as a VM in GNOME Boxes.  

### Requirements

This project requires Python 3 and pip.  If the current operational Python version is not Python 3, enable Python 3 in working terminal via 
the following command:
```
# scl enable rh-python36 bash
```

The included requirements.txt will supply all necessary libraries except NLTK, if the
following command is executed within the virtual environment where the program will be executed:
```
(venv) pip install -r requirements.txt
```
The NLTK library is not included in the Python libraries on RHEL, so NLTK and NLTK_Data must be installed using the following commands:

```
# sudo python -m pip install nltk
# sudo python -m nltk.downloader -d /usr/share/nltk_data all
```

To install a Mongo database on RHEL, create an /etc/yum/repos.d/mongodb-org-4.0.repo file containing the following:

```
[mongodb-org-4.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/$releasever/mongodb-org/4.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-4.0.asc
```
then run the following command:
```
sudo yum install -y mongodb-org
```

To set up database data path and begin mongo daemon, run following commands:
```
mkdir data
echo "mongod --dbpath=data" > mongod
chmod a+x mongod
./mongod
```
 To activate virtual environment, run:
 
 ```
 # source venv/bin/activate activate
 ```
 
 Before running the program, update config.yml to point to the folder paths for the watched, error, parsed, and clean text folders,
 wherever they are located on local machine.
 
 Start program execution by running:
 
 ```
 (venv) python process.py
 ```
 
