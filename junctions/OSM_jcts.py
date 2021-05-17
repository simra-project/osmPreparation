#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import time
import datetime
import argparse
import time

pd.set_option('display.max_columns', 200)

import utils
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

    nodesdf = dfShizzle.metaFunc(utils.paramDict[region]["bounding_box"])

    junctionsdf = findJunctions.getJunctionsDf(nodesdf, region)

    bufferedJunctionsDf = bufferJcts.bufferize(junctionsdf, buffer_size)

    nonIsolatedJunctions, isolatedJunctions = clusterJcts.cluster(bufferedJunctionsDf)

    completeJunctions = tidyData_Jcts.tidyItUp(region, utils.paramDict[region]["centroid"], nonIsolatedJunctions, isolatedJunctions, buffer_size)

    # Write to pickle for future use

    file_name = f"{region}_junctions_buffer={buffer_size}"

    path = utils.getSubDirPath(file_name, "pickled_data")

    # Write data frame to pickle folder; include buffer_size in the file name
    # ==> purpose of this is to be able to reuse data in the manual merging
    #     tool so if a data set for a specific region and buffer size already
    #     exists it can be utilized rather than computing everything from scratch again

    completeJunctions.to_pickle(path)

    return completeJunctions

if __name__ == "__main__":

    # Create the argument parser and add arguments

    parser = argparse.ArgumentParser()

    parser.add_argument(dest='region', type=str, help="The region to compute junctions for.")

    parser.add_argument(dest='buf_size', type=float, help="By how much the one-dimensional junction points will be buffered.")

    # Parse the input parameters

    args = parser.parse_args()

    start_time = time.time()

    completeJunctions = main(args.region, args.buf_size)

    print("--- %s seconds ---" % (time.time() - start_time))

    file_name = f"{args.region}_junctions_complete_{datetime.date.today()}.csv"

    path = utils.getSubDirPath(file_name, "csv_data")

    completeJunctions.to_csv(path, index=False, sep="|")

