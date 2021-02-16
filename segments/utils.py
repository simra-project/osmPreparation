
import os

paramDict = {
    "augsburg": {
        "bounding_box": [10.763362,48.249337,10.959333,48.468336],
        "centroid": [48.354761, 10.896351],
        "neighbour_param": 80, 
        "sorting_params": ['minx','maxy'],  # wide bounding box - sort by lower left corner.
        "small_buf_default": 1,             # medium-sized city (< 1 Mio. inhabitants)
        "large_buf_default": 1.25            # medium-sized city (< 1 Mio. inhabitants)
    },
    "bern": {
        "bounding_box": [7.423641,46.93916,7.469955,46.962112],
        "centroid": [46.945876,7.415994],
        "neighbour_param": 100, # place-holder
        "sorting_params": ['minx','maxy'],  # long-ish bounding box - sort by upper left corner.
        "small_buf_default": 1,             # small-sized city (< 200k inhabitants)
        "large_buf_default": 1.25           # small-sized city (< 200k inhabitants)
    },  
    "pforzheim": {
        "bounding_box": [8.653482,48.873994,8.743249,48.910329],
        "centroid": [48.877046,8.710584],
        "neighbour_param": 100,
        "sorting_params": ['minx','maxy'],  # long-ish bounding box - sort by upper left corner.
        "small_buf_default": 1,             # small-sized city (< 200k inhabitants)
        "large_buf_default": 1.25           # small-sized city (< 200k inhabitants)
    },
    "wuppertal": {
        "bounding_box": [7.014072,51.165803,7.31343,51.318062],
        "centroid": [51.240631,7.163216],
        "neighbour_param": 80,
        "sorting_params": ['minx','maxy'],  # wide bounding box - sort by lower left corner.
        "small_buf_default": 1,             # medium-sized city  (< 1 Mio. inhabitants)
        "large_buf_default": 1.25           # medium-sized city  (< 1 Mio. inhabitants)
    },
    "wedding": {
        "bounding_box": [13.319638,52.538373,13.382339,52.570332],
        "centroid": [52.555071, 13.349667],
        "neighbour_param": 100,
        "sorting_params": ['minx','maxy'],  # square bounding box - sort by upper left corner (although it doesn't really matter).
        "small_buf_default": 1,             # large city (>1 Mio. inhabitants)
        "large_buf_default": 1.25           # large-sized city (> 1 Mio. inhabitants)
    },
    "hannover": {
        "bounding_box": [9.60443,52.305137,9.918426,52.454335],
        "centroid": [52.3796, 9.7617],
        "neighbour_param": 200,
        "sorting_params": ['minx','maxy'],  # square bounding box - sort by upper left corner (although it doesn't really matter).
        "small_buf_default": 1,             # medium-sized city (< 1 Mio. inhabitants)
        "large_buf_default": 1.25           # medium-sized city (< 1 Mio. inhabitants)
    },

    # limiting stuttgart to city center for testing purposes
    # REMEMBER TO UNDO!!!!

    "stuttgart": {
        "bounding_box": [9.164437,48.771372,9.207154,48.798472],
        #"bounding_box": [9.038601,48.692019,9.31582,48.866399],
        "centroid": [48.7825,9.1831],
        "neighbour_param": 300,
        "sorting_params": ['minx','maxy'],  # long-ish bounding box - sort by upper left corner.
        "small_buf_default": 1,             # medium-sized city (< 1 Mio. inhabitants)
        "large_buf_default": 1.25           # medium-sized city (< 1 Mio. inhabitants)
    }
}

def inTargetDir (cwd):

    cwd_parts = cwd.split("/")

    return (cwd_parts[len(cwd_parts)-1] == 'segments')

def getSubDirPath (file_, subdir = 'segments'):

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

