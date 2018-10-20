# coding=utf-8
import sys
import string
from bs4 import BeautifulSoup

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
    for text_block in soup.body.stripped_strings:
        print(repr(text_block))
        for word in (repr(text_block)).translate(str.maketrans('', '', string.punctuation)).lower().split():
            word_list.append(word)

    print(word_list)

