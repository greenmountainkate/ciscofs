# coding=utf-8
"""
This module moves files between folders.
"""
import os
import shutil


def move_to_folder(source, dest, file):
    """
    Moves a file from source folder to destination folder
    :param source: string that holds path to source folder
    :param dest: string that holds path to destination folder
    :param file: string that holds filename of file to be moved
    :return: the destination folder as a string, if move was successful
    """
    try:
        return shutil.move(os.path.join(source, file), os.path.join(dest, file))
    except FileNotFoundError as e:
        print("Error in moving {0} from {1} to {2}.  File location unchanged. ".format(
            file, source, dest), e)
        return None
    except NotADirectoryError as e:
        print("Error in moving {0} from {1} to {2}.  File location unchanged. ".format(
            file, source, dest), e)
        return None