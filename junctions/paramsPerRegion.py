
paramDict = {
    "bern": {
        "bounding_box": [7.423641,46.93916,7.469955,46.962112],
        "centroid": [46.945876,7.415994],
        "neighbour_param": 100, # place-holder
        "sorting_params": ['lon','lat'] # long-ish bounding box - prioritize sorting via lon over lat.
    },
    "pforz": {
        "bounding_box": [8.653482,48.873994,8.743249,48.910329],
        "centroid": [48.877046,8.710584],
        "neighbour_param": 100,
        "sorting_params": ['lon','lat'] # long-ish bounding box - prioritize sorting via lon over lat.
    },
    "wupp": {
        "bounding_box": [7.014072,51.165803,7.31343,51.318062],
        "centroid": [51.240631,7.163216],
        "neighbour_param": 80,
        "sorting_params": ['lat','lon'] # wide bounding box - prioritize sorting via lat over lon.
    },
    "stutt": {
        "bounding_box": [9.038601,48.692019,9.31582,48.866399],
        "centroid": [48.778461,9.177910],
        "neighbour_param": 80,
        "sorting_params": ['lon','at'] # long-ish bounding box - prioritize sorting via lon over lat.
    }
}