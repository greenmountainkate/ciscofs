# import subprocess
from pymongo import MongoClient
from bs4 import BeautifulSoup
# import nltk
# nltk.download('stopwords')
from nltk.corpus import stopwords
import pandas as pd
import numpy as np
import os
import time
import shutil
import sys
import string
from yaml import load, dump
try: from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

# necessary folders - TODO set up script to pull from one config file
with open("config.yml", 'r') as ymlfile:
    cfg = load(ymlfile, Loader=Loader)
    for section in cfg:
        print(section)
    print(cfg['folders'])
    print(cfg['folders'].get('parsed'))
    print(type(cfg['folders'].get('parsed')))

watched_folder = cfg['folders'].get('watched') #sys.argv[1]  # folder to watch
parsed_files_folder = cfg['folders'].get('parsed') #sys.argv[2]  # parsedFiles folder
error_files_folder = cfg['folders'].get('error') #sys.argv[3]  # folder to hold files unable to be parsed
clean_files_folder = cfg['folders'].get('clean') #sys.argv[4]  # folder to hold clean text files

files1 = os.listdir(watched_folder)  # list of files in watched_folder

# ----------DB SETUP--------------------
client = MongoClient()

# create database (lazy creation)
db = client.ciscoFSE_database

# create collections (also lazy creation)
ParsedFiles = db.parsed_files
ErrorFiles = db.error_files


# --------FUNCTION DEFINITIONS------------

def parse_html_file(file_to_parse):
    with open(file_to_parse) as ftp:
        # parse html file to tree object
        soup = BeautifulSoup(ftp, 'lxml')
        return soup


def get_headers(parsed_file_object):
    return [header for header in parsed_file_object.body.find_all(['h1', 'h2', 'h3', 'h4', 'h5'])]


def clean_text(pfo):
    return [word for text in pfo.body.stripped_strings for word in
            (repr(text)).translate(str.maketrans('', '', string.punctuation)).lower().split()]


def clean_text_remove_headers(parsed_file_object):
    for header in parsed_file_object.body.find_all(['h1', 'h2', 'h3', 'h4', 'h5']):
        header.decompose()
    return clean_text(parsed_file_object)


def write_clean_text(w_list, pf_id, file_extension):
    # create file in clean_folder and open for writing
    with open(os.path.join(clean_files_folder, "".join([pf_id, file_extension])), 'w+') as clean_file:
        for word in w_list:
            clean_file.write('{0} '.format(word))


def clear_stop_words(word_list):
    stop = set(stopwords.words('english'))
    return [word for word in word_list if word not in stop]


while True:

    time.sleep(8)  # TODO change to 600
    files2 = os.listdir(watched_folder)
    # see if there are new files added
    new = [f for f in files2 if all([not f in files1, f.endswith(".html")])]
    # if so parse file:
    for f in new:
        # parse file
        pf_obj = parse_html_file(os.path.join(watched_folder, f))

        # pull headers to list
        header_list = get_headers(pf_obj)

        # get cleaned text as list
        word_list = clean_text(pf_obj)
        print("Length with headers: ", len(word_list))

        # get cleaned text without headers as list
        wl_no_headers = clean_text_remove_headers(pf_obj)
        print("Length without headers: ", len(wl_no_headers))

        # create document in database
        file_dict = {'FileName': f, 'FileLength': len(f), 'headers': header_list}
        parsed_file_id = ParsedFiles.insert_one(file_dict).inserted_id

        # copy clean text to dbID.txt in clean file folder
        write_clean_text(word_list, str(parsed_file_id), ".txt")
        # copy clean text with headers removed to dbID_noheader.txt in clean file folder
        write_clean_text(wl_no_headers, str(parsed_file_id), "_noheaders.txt")

        # remove stop words from wordlist_no_headers
        wl_no_headers = clear_stop_words(wl_no_headers)
        print('Length after clear stopwords: ', len(wl_no_headers))


        #calculate tf for this doc then back calculate Idf and get updated tf-idf through database
        imp_words = pd.DataFrame({'docID': str(parsed_file_id), 'word': wl_no_headers})
        print(imp_words.head())

        print(imp_words.describe())

        # move parsed file to parsedFiles folder
        # combine paths and file
        parsed_folder = os.path.join(parsed_files_folder, f)
        # copy the parsed file to ParsedFilesFolder
        shutil.move(os.path.join(watched_folder, f), parsed_folder)

    files1 = files2  # reset watched folder for next loop
