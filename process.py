# import subprocess
"""

"""
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
import string
from yaml import load
try: from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

#-----------MODULE-IMPORTS----------------------
from parseFile import parse_html_file
from processText import *
from fileIO import write_clean_text
from folderIO import move_to_folder

# load necessary folders' paths
with open("config.yml", 'r') as ymlfile:
    cfg = load(ymlfile, Loader=Loader)

watched_folder = cfg['folders'].get('watched') # folder to watch
parsed_files_folder = cfg['folders'].get('parsed') # parsedFiles folder
error_files_folder = cfg['folders'].get('error')  # folder to hold files unable to be parsed
clean_files_folder = cfg['folders'].get('clean')  # folder to hold clean text files

files1 = os.listdir(watched_folder)  # list of initial files in watched_folder

# ----------DB SETUP--------------------
client = MongoClient()

# create database (lazy creation)
db = client.ciscoFSE_database

# create collections (also lazy creation)
ParsedFiles = db.parsed_files
ErrorFiles = db.error_files


while True:

    time.sleep(8)  # TODO change to 600
    files2 = os.listdir(watched_folder)
    # see if there are new files added
    new = [f for f in files2 if all([not f in files1, f.endswith(".html")])]
    # if so parse files:
    for f in new:
        # parse file
        pf_obj = parse_html_file(os.path.join(watched_folder, f))

        # check if parse was unsuccessful
        if pf_obj is None:
            #move file to error folder
            move_to_folder(f, watched_folder, error_files_folder)
            #move to next file
            continue

        # pull headers to list
        header_list = get_headers(pf_obj)
        print(header_list)

        # get cleaned text as list
        word_list = clean_text(pf_obj)
        print("Length with headers: ", len(word_list))

        # get cleaned text without headers as list
        wl_no_headers = clean_text_remove_headers(pf_obj)
        print("Length without headers: ", len(wl_no_headers))

        # create document in database
        file_dict = {'FileName': f, 'FileLength': len(f), 'headers': header_list}
        print(file_dict)
        parsed_file_id = ParsedFiles.insert_one(file_dict).inserted_id

        # copy clean text to dbID.txt in clean file folder
        write_clean_text(word_list, str(parsed_file_id), clean_files_folder, ".txt")
        # copy clean text with headers removed to dbID_noheader.txt in clean file folder
        write_clean_text(wl_no_headers, str(parsed_file_id), clean_files_folder, "_noheaders.txt")

        # remove stop words from wordlist_no_headers
        wl_no_headers = clear_stop_words(wl_no_headers)
        print('Length after clear stopwords: ', len(wl_no_headers))
        print(wl_no_headers)


        #calculate tf for this doc then back calculate Idf and get updated tf-idf through database
        imp_words = pd.DataFrame({'docID': str(parsed_file_id), 'word': wl_no_headers})
        print(imp_words.head())

        print(imp_words.describe())

        # move parsed file to parsedFiles folder
        move_to_folder(watched_folder, parsed_files_folder, f)

    files1 = files2  # reset watched folder for next loop
