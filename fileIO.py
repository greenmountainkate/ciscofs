# coding=utf-8
"""

"""
import os


def write_clean_text(w_list, pf_id, folder, file_extension):
    """

    :param w_list:
    :param pf_id:
    :param folder:
    :param file_extension:
    :return:
    """
    # create file in clean_folder and open for writing
    with open(os.path.join(folder, "".join([pf_id, file_extension])), 'w+') as clean_file:
        for word in w_list:
            clean_file.write('{0} '.format(word))
