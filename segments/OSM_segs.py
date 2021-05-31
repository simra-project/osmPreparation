#!/usr/bin/env python
# coding: utf-8

import pandas as pd

import datetime

import sys
sys.path.append("..")

import utils
import config
import dataAcqAndForm_Segs as dfShizzle
import segmentizeAndEnrich
import bufferSegs
import clusterSegs
import tidyData_Segs

import time
import argparse
import sys

# ARGUMENTS.
#  * region: a string - which region are we currently looking at? Required for writing files.
#  * junctionsdf: written by junctions subproject, required for segmenting highways (breaking them into components
#                 at junctions)
#  * boundingBox (READ FROM CONFIG): bounding box for region; used for querying data from Overpass API
#  * bbCentroid (READ FROM CONFIG): the bounding box centroid (a lat/lon pair); required for map creation

def main(region, junctionsdf):

    highwaydf, idCoords_dict = dfShizzle.metaFunc(config.paramDict[region]["bounding_box"])
    print("Created highwaydf and coordsdict")

    unfoldedEnrichedDf = segmentizeAndEnrich.metaFunc(highwaydf, junctionsdf, idCoords_dict)
    print("Unfolded the enrichted df")

    bufferedDf = bufferSegs.bufferize(unfoldedEnrichedDf)
    print("Created bufferDf")

    oddballs, normies = clusterSegs.cluster(bufferedDf, junctionsdf)
    print("Created segment clusters")

    completeSegments = tidyData_Segs.tidyItUp(region, oddballs, normies)
    print("Cleaned segments")
    
    # Write to pickle for future use

    file_name = f"{region}_segments"

    path = utils.getSubDirPath(file_name, "pickled_data", "segments")

    completeSegments.to_pickle(path)

    return completeSegments

if __name__ == "__main__":

    # Create the argument parser and add arguments

    parser = argparse.ArgumentParser()

    parser.add_argument(dest='region', type=str, help="The region to compute junctions for.")

    # Parse the input parameter

    args = parser.parse_args()

    # Read junctions data from csv

    # Read the junctions data from csv that was produced by the junctions sub-project.
    # It used to be read directly from the csv_data directory in the junctions subproject,
    # but now to enable utilization with docker and avoid mounting hell it has to be moved
    # manually from junctions/csv_data to segments/csv_data (unless the top level script
    # main.py in PyPipeline_ is used).
    # !!!!! Be sure to execute the junctions project first before executing the 
    #       segments project for the same region !!!!
    # (Otherwise, there might be no file to read.)

    subdir_path = utils.getSubDirPath(f"{args.region}_junctions_for_segs.csv", "csv_data", "segments")

    # Notify user if junctions_for_segs.csv is unavailable as the junctions project hasn't been
    # executed before the segments fraction
    try:
        junctionsdf = pd.read_csv(subdir_path)
    except FileNotFoundError: 
        print("Junctions file wasn't found! Please execute OSM_jcts.py for this region to generate it.")
        sys.exit()

    start_time = time.time()

    completeSegs = main(args.region, junctionsdf)

    print("--- %s seconds ---" % (time.time() - start_time))

    file_name = f"{args.region}_segments_complete_{datetime.date.today()}.csv"

    path = utils.getSubDirPath(file_name, "csv_data", "segments")

    completeSegs.to_csv(path, index=False, sep="|")
