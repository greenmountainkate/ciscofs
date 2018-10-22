# coding=utf-8
"""
This module moves files between folders.
"""
import os
import shutil


def move_to_folder(source_folder, dest_folder, file_to_move):
    """
    Moves a file from source folder to destination folder
    :param source_folder: string that holds path to source folder
    :param dest_folder: string that holds path to destination folder
    :param file_to_move: string that holds filename of file to be moved
    :return: the destination folder as a string, if move was successful
    """
    try:
        return shutil.move(os.path.join(source_folder, file_to_move), os.path.join(dest_folder, file_to_move))
    except FileNotFoundError as e:
        print("Error in moving {0} from {1} to {2}.  File location unchanged. ".format(
            file_to_move, source_folder, dest_folder), e)
        return None
    except NotADirectoryError as e:
        print("Error in moving {0} from {1} to {2}.  File location unchanged. ".format(
            file_to_move, source_folder, dest_folder), e)
        return None