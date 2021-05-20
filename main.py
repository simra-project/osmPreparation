
import sys
sys.path.insert(0, './junctions')
sys.path.insert(0, './segments')

import OSM_jcts
import OSM_segs

import utils
import config

import argparse
import datetime

if __name__ == "__main__":

    # Create the argument parser and add arguments

    parser = argparse.ArgumentParser()

    parser.add_argument(dest='region', type=str, help="The region to compute junctions for.")

    # Parse the input parameter

    args = parser.parse_args()

    # Look up buffer size from param_dict in config.py

    buf_size = config.paramDict[args.region]["small_buf_default"]

    # Run junctions main script

    completeJunctions, junctions_for_segs = OSM_jcts.main(args.region, buf_size)

    # Write junction data set to csv

    jcts_file_name = f"{args.region}_junctions_complete_{datetime.date.today()}.csv"

    junction_path = utils.getSubDirPath(jcts_file_name, "csv_data")

    completeJunctions.to_csv(junction_path, index=False, sep="|")

    # Write junction data subset to be used by segments script to csv

    jcts_for_segs_file_name = f"{args.region}_junctions_for_segs.csv"

    jcts_for_segs_path = utils.getSubDirPath(jcts_for_segs_file_name, "csv_data")

    junctions_for_segs.to_csv(jcts_for_segs_path)

    # Call segments script

    completeSegments = OSM_segs.main(args.region, junctions_for_segs)

    # Write segment data set to csv

    segs_file_name = f"{args.region}_segments_complete_{datetime.date.today()}.csv"

    segs_path = utils.getSubDirPath(segs_file_name, "csv_data")

    completeSegments.to_csv(segs_path, index=False, sep="|")

