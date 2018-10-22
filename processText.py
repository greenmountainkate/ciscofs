# coding=utf-8
"""

"""
import string
from nltk.corpus import stopwords


def get_headers(parsed_file_object):
    """
    
    :param parsed_file_object: 
    :return: 
    """
    return [header.get_text() for header in parsed_file_object.body.find_all(['h1', 'h2', 'h3', 'h4', 'h5'])]


def clean_text(pfo):
    """

    :rtype: object
    """
    for scpt in pfo.body.find_all(['script']):
        scpt.decompose()  # remove scripts
    return [word for text in pfo.body.stripped_strings for word in
            (repr(text)).translate(str.maketrans('', '', string.punctuation)).lower().split()]


def clean_text_remove_headers(parsed_file_object):
    """
    
    :param parsed_file_object: 
    :return: 
    """
    for header in parsed_file_object.body.find_all(['h1', 'h2', 'h3', 'h4', 'h5']):
        header.decompose()
    return clean_text(parsed_file_object)


def clear_stop_words(word_list):
    """
    
    :param word_list: 
    :return: 
    """
    stop = set(stopwords.words('english'))
    return [word for word in word_list if word not in stop]
