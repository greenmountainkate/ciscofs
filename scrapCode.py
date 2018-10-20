# coding=utf-8
import sys
import string
from bs4 import BeautifulSoup


def clean_text(parsed_file_object):
    w_list = []
    # clean text (strip whitespace, remove punctuation, shiftcase to lower
    for text_block in parsed_file_object.body.stripped_strings:
        for word in (repr(text_block)).translate(str.maketrans('', '', string.punctuation)).lower().split():
            w_list.append(word)
    return w_list

def better_clean_text(pfo):
    return [word for text in pfo.body.stripped_strings for word in (repr(text)).translate(str.maketrans('','', string.punctuation)).lower().split()]

# file to parse
with open(sys.argv[1]) as ftp:
    #parse html file to tree object
    soup = BeautifulSoup(ftp, 'lxml')

    #pull headers to list
    header_list = []
    for header in soup.body.find_all(['h1', 'h2', 'h3', 'h4', 'h5']):
        header_list.append(header.get_text().lower())
    print(header_list)

    word_list = []
    # clean text (strip whitespace, remove punctuation, shiftcase to lower


    print(word_list)

    #h_list = []
    #for header in parsed_file_object.body.find_all(['h1', 'h2', 'h3', 'h4', 'h5']):
    #    h_list.append(header.get_text())
   # return h_list



watched_folder = sys.argv[1]  # folder to watch
parsed_files_folder = sys.argv[2]  # parsedFiles folder
error_files_folder = sys.argv[3]  # folder to hold files unable to be parsed
clean_files_folder = sys.argv[4]  # folder to hold clean text files