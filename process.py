# coding=utf-8
"""

This file is the main start of program execution.  It connects to the db,
loads the folder structure from the yaml config file, and begins the cycle of
monitoring the target folder for new files.

"""
import os
from pymongo import MongoClient
from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

# -----------MODULE-IMPORTS----------------------
from parse_file import parse_html_file, parse_error
from process_text import *
from fileIO import write_clean_text
from folderIO import move_to_folder

# -------------FOLDER-SETUP------------------------

# load necessary folders' paths
with open("config.yml", 'r') as ymlfile:
    cfg = load(ymlfile, Loader=Loader)

watched_folder = cfg['folders'].get('watched')  # folder to watch
parsed_files_folder = cfg['folders'].get('parsed')  # parsedFiles folder
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

# -----------MAIN-EXECUTION---------


while True:

    time.sleep(600)  #check every 10 minutes.  Consider shifting to a chron script.
    files2 = os.listdir(watched_folder)
    # see if there are new files added
    new = [f for f in files2 if all([f not in files1, f.endswith(".html")])]
    # if so parse files:
    for f in new:
        # parse file
        pf_obj = parse_html_file(os.path.join(watched_folder, f), ErrorFiles)

        # check for structural parsing errors
        if (parse_error(error_db=ErrorFiles, watch_folder=watched_folder, error_folder=error_files_folder, f=f,
                        pf_obj=pf_obj)):
            continue  # move to next file

        # pull headers to list
        header_list = get_headers(pf_obj)

        # get cleaned text as list
        # word_list = clean_text(pf_obj)

        # get cleaned text without headers as list
        wl_no_headers = clean_text_remove_headers(pf_obj)

        # create document in database
        file_dict = {'headers': header_list, 'keyWords': {}}
        parsed_file_id = ParsedFiles.insert_one(file_dict).inserted_id

        # copy clean text to dbID.txt in clean file folder
        # write_clean_text(word_list, str(parsed_file_id), clean_files_folder, ".txt")

        # copy clean text with headers removed to dbID_noheader.txt in clean file folder
        write_clean_text(wl_no_headers, str(parsed_file_id), clean_files_folder, ".txt")

        # remove stop words from wordlist_no_headers
        wl_no_headers = clear_stop_words(wl_no_headers)

        # process cleaned word list
        process_imp_words(pf_db=ParsedFiles, error_db=ErrorFiles, file_id=parsed_file_id, word_list=wl_no_headers)

        # move parsed file to parsedFiles folder
        move_to_folder(source=watched_folder, dest=parsed_files_folder, file=f)

    files1 = files2  # reset watched folder for next loop
