
import os
import json
import datetime

def getSubDirPath (file_, subdir, subproject = ''):

    # Concatenate path using os library so system can tell which part of the
    # path is a directory and which is a file name.

    curr_dir = os.path.abspath(os.path.dirname(__file__))

    file_path = os.path.join(curr_dir, subproject, subdir, file_)

    # Create directory if it doesn't already exist

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    return file_path

def fileExists (file_name):

    path = getSubDirPath(file_name,'pickled_data')

    return os.path.isfile(path)

# For writing to csv_data directory in PyPipeline_ directory

def getTopLevelDataPath (file_name) :

    parent_path = os.path.split(os.path.dirname(__file__))[0]

    return os.path.join(parent_path, 'csv_data', file_name)