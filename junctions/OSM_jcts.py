#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import time
import datetime
import argparse
import time

pd.set_option('display.max_columns', 200)

import sys
sys.path.append("..")

import utils
import config
import dataAcqAndForm_Jcts as dfShizzle
import findJunctions
import bufferJcts
import clusterJcts
import tidyData_Jcts

# ARGUMENTS.
#  * region: a string - which region are we currently looking at? Required for writing files.
#  * boundingBox: bounding box for region; used for querying data from Overpass API
#  * bbCentroid: the bounding box centroid (a lat/lon pair); required for map creation
#  * buffer_size: junctions are buffered into two-dimensional shapes according to the mean width of the
#                highways intersecting at this junction multiplied with a factor. This factor varies 
#                depending on the city layout.

def main(region, buffer_size):

    nodesdf = dfShizzle.metaFunc(config.paramDict[region]["bounding_box"])
    print("Created nodedf")

    junctionsdf, junctions_for_segs = findJunctions.getJunctionsDf(nodesdf, region)
    print("Got junctions for region {0!s}".format(region))

    bufferedJunctionsDf = bufferJcts.bufferize(junctionsdf, buffer_size)
    print("Created bufferDf")

    nonIsolatedJunctions, isolatedJunctions = clusterJcts.cluster(bufferedJunctionsDf)
    print("Created junction clusters")

    completeJunctions = tidyData_Jcts.tidyItUp(region, config.paramDict[region]["centroid"], nonIsolatedJunctions, isolatedJunctions, buffer_size)
    print("Cleaned junctions")

    # Write to pickle for future use

    file_name = f"{region}_junctions_buffer={buffer_size}"

    path = utils.getSubDirPath(file_name, "pickled_data", "junctions")

    # Write data frame to pickle folder; include buffer_size in the file name
    # ==> purpose of this is to be able to reuse data in the manual merging
    #     tool so if a data set for a specific region and buffer size already
    #     exists it can be utilized rather than computing everything from scratch again

    completeJunctions.to_pickle(path)

    return completeJunctions, junctions_for_segs

if __name__ == "__main__":

    # Create the argument parser and add arguments

    parser = argparse.ArgumentParser()

    parser.add_argument(dest='region', type=str, help="The region to compute junctions for.")

    parser.add_argument(dest='buf_size', type=float, help="By how much the one-dimensional junction points will be buffered.")

    # Parse the input parameters

    args = parser.parse_args()

    start_time = time.time()

    completeJunctions, junctions_for_segs = main(args.region, args.buf_size)

    print("--- %s seconds ---" % (time.time() - start_time))

    # Write entire data set to csv

    file_name = f"{args.region}_junctions_complete_{datetime.date.today()}.csv"

    path = utils.getSubDirPath(file_name, "csv_data", "junctions")

    completeJunctions.to_csv(path, index=False, sep="|")

    # Write data subset to be used by segments script to csv

    file_name_ = f"{args.region}_junctions_for_segs.csv"

    path_ = utils.getSubDirPath(file_name_, "csv_data", "junctions")

    junctions_for_segs.to_csv(path_)


