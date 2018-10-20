#import subprocess
from pymongo import MongoClient
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import os
import time
import shutil
import sys
import string

#necessary folders - TODO set up script to pull from one config file
watched_folder = sys.argv[1] #folder to watch
parsed_files_folder = sys.argv[2] #parsedFiles folder
error_files_folder = sys.argv[3] #folder to hold files unable to be parsed
clean_files_folder = sys.argv[4] #folder to hold clean text files

files1 = os.listdir(watched_folder) #list of files in watched_folder

#----------DB SETUP--------------------
client = MongoClient()

#create database (lazy creation)
db = client.ciscoFSE_database

#create collections (also lazy creation)
ParsedFiles = db.parsed_files
ErrorFiles = db.error_files

#--------FUNCTION DEFINITIONS------------

def parse_html_file(file_to_parse):
    with open(file_to_parse) as ftp:
        # parse html file to tree object
        soup = BeautifulSoup(ftp, 'lxml')
        return soup

def get_headers(parsed_file_object):
    h_list = []
    for header in parsed_file_object.body.find_all(['h1', 'h2', 'h3', 'h4', 'h5']):
        h_list.append(header.get_text())
    return h_list

def clean_text(parsed_file_object):
    w_list = []
    # clean text (strip whitespace, remove punctuation, shiftcase to lower
    for text_block in parsed_file_object.body.stripped_strings:
        for word in (repr(text_block)).translate(str.maketrans('', '', string.punctuation)).lower().split():
            w_list.append(word)
    return w_list

def clean_text_remove_headers(parsed_file_object):
    for header in parsed_file_object.body.find_all(['h1', 'h2', 'h3', 'h4', 'h5']):
        header.decompose()
    w_list = []
    # clean text (strip whitespace, remove punctuation, shiftcase to lower
    for text_block in parsed_file_object.body.stripped_strings:
        for word in (repr(text_block)).translate(str.maketrans('', '', string.punctuation)).lower().split():
            w_list.append(word)
    return w_list

def write_clean_text(w_list, pf_id, file_extension):
    #create file in clean_folder and open for writing
    with open(os.path.join(clean_files_folder, "".join([pf_id, file_extension])),'w+') as clean_file:
        for word in w_list:
            print('{0} '.format(word))
            clean_file.write('{0} '.format(word))

while True:

    time.sleep(8) #TODO change to 600
    files2 = os.listdir(watched_folder)
    # see if there are new files added
    new = [f for f in files2 if all([not f in files1, f.endswith(".html")])]
    # if so parse file:
    for f in new:

        # parse file
        pf_obj = parse_html_file(os.path.join(watched_folder, f))


        # pull headers to list
        header_list = get_headers(pf_obj)

        #get cleaned text as list
        word_list = clean_text(pf_obj)
        print(word_list)

        #get cleaned text without headers as list
        wl_no_headers = clean_text_remove_headers(pf_obj)
        print(wl_no_headers)


        #create document in database
        file_dict = {'FileName': f, 'FileLength': len(f), 'headers': header_list}
        parsed_file_id = ParsedFiles.insert_one(file_dict).inserted_id

        # copy clean text to dbID.txt in clean file folder
        write_clean_text(word_list, str(parsed_file_id), ".txt")
        # copy clean text with headers removed to dbID_noheader.txt in clean file folder
        write_clean_text(wl_no_headers, str(parsed_file_id), "_noheaders.txt")

        imp_words = pd.DataFrame({'docID':str(parsed_file_id), 'word':wl_no_headers})
        print(imp_words.head())

        print(imp_words.describe())


        #move parsed file to parsedFiles folder
        # combine paths and file
        parsed_folder = os.path.join(parsed_files_folder, f)
        # copy the parsed file to ParsedFilesFolder
        shutil.move(os.path.join(watched_folder, f), parsed_folder)

    files1 = files2 #reset watched folder for next loop