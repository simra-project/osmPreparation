
import os

paramDict = {
    "augsburg": {
        "bounding_box": [10.763362,48.249337,10.959333,48.468336],
        "centroid": [48.354761, 10.896351],
        "neighbour_param": 80, 
        "sorting_params": ['lat','lon'],  # wide bounding box - sort by lower left corner.
        "small_buf_default": 2.25,          # medium-sized city (< 1 Mio. inhabitants)
        "large_buf_default": 2.5            # medium-sized city (< 1 Mio. inhabitants)
    },
    "bern": {
        "bounding_box": [7.423641,46.93916,7.469955,46.962112],
        "centroid": [46.945876,7.415994],
        "neighbour_param": 100, # place-holder
        "sorting_params": ['lon','lat'],  # long-ish bounding box - sort by upper left corner.
        "small_buf_default": 2,             # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25           # small-sized city (< 200k inhabitants)
    },  
    "pforzheim": {
        "bounding_box": [8.653482,48.873994,8.743249,48.910329],
        "centroid": [48.877046,8.710584],
        "neighbour_param": 100,
        "sorting_params": ['lon','lat'],  # long-ish bounding box - sort by upper left corner.
        "small_buf_default": 2,             # small-sized city (< 200k inhabitants)
        "large_buf_default": 2.25           # small-sized city (< 200k inhabitants)
    },
    "wuppertal": {
        "bounding_box": [7.014072,51.165803,7.31343,51.318062],
        "centroid": [51.240631,7.163216],
        "neighbour_param": 80,
        "sorting_params": ['lat','lon'],  # wide bounding box - sort by lower left corner.
        "small_buf_default": 2,             # medium-sized city  (< 1 Mio. inhabitants)
        "large_buf_default": 2.25           # medium-sized city  (< 1 Mio. inhabitants)
    },
    "stuttgart": {
        "bounding_box": [9.038601,48.692019,9.31582,48.866399],
        "centroid": [48.778461,9.177910],
        "neighbour_param": 80,
        "sorting_params": ['lon','lat'],  # long-ish bounding box - sort by upper left corner.
        "small_buf_default": 2.25,          # medium-sized city (< 1 Mio. inhabitants)
        "large_buf_default": 2.5            # medium-sized city (< 1 Mio. inhabitants)
    }
}
def inTargetDir (cwd):

    cwd_parts = cwd.split("/")

    return (cwd_parts[len(cwd_parts)-1] == 'junctions')

def getSubDirPath (file_, subdir = 'junctions'):

    # Concatenate path using os library so system can tell which part of the
    # path is a directory and which is a file name.

    subdir_path = os.path.join(subdir, file_)

    return subdir_path

def fileExists (file_name):

    cwd = os.getcwd()

    if (inTargetDir(cwd)):

        path = getSubDirPath(file_name,'pickled_data')

        return os.path.isfile(path)

    else:

        sub_one = getSubDirPath(file_name, 'pickled_data')

        sub_two = getSubDirPath(sub_one)

        return os.path.isfile(sub_two)