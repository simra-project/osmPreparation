
import sys
sys.path.insert(0, './junctions')
sys.path.insert(0, './segments')

import OSM_jcts
import OSM_segs

import utils
import config

import argparse
import datetime
import json

if __name__ == "__main__":

    # Create the argument parser and add arguments

    parser = argparse.ArgumentParser()

    parser.add_argument(dest='region', type=str, help="The region to compute junctions for.")

    # Parse the input parameter

    args = parser.parse_args()

    # Look up buffer size from param_dict in config.py

    buf_size = config.paramDict[args.region]["small_buf_default"]

    # Run junctions main script

    print("Running junctions main script")
    completeJunctions, junctions_for_segs = OSM_jcts.main(args.region, buf_size)
    print("Completed junctions main script")

    # Write junction data set to csv

    jcts_file_name = f"{args.region}_junctions_complete_{datetime.date.today()}.csv"

    junction_path = utils.getSubDirPath(jcts_file_name, "output_data")

    completeJunctions.to_csv(junction_path, index=False, sep="|")

    # Call segments script
    print("Running segments main script")
    completeSegments = OSM_segs.main(args.region, junctions_for_segs)
    print("Completed segments main script")

    # Write segments data set to csv

    segs_file_name = f"{args.region}_segments_complete_{datetime.date.today()}.csv"

    segs_path = utils.getSubDirPath(segs_file_name, "output_data")

    completeSegments.to_csv(segs_path, index=False, sep="|")

    # Write meta file

    meta_dict = {
        "bounding_box": config.paramDict[args.region]["bounding_box"],
        "centroid": config.paramDict[args.region]["centroid"],
        "junctions_buffer": config.paramDict[args.region]["small_buf_default"],
        "datetime": str(datetime.date.today())
    }

    # the json file where the output must be stored
    meta_path = utils.getSubDirPath(f'{args.region}_meta.json', 'output_data')
  
    with open(meta_path, 'w') as json_file:
        json.dump(meta_dict, json_file)