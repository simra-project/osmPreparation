#!/usr/bin/env python
# coding: utf-8

import pandas as pd

import numpy as np
import datetime

import utils
import dataAcqAndForm_Segs as dfShizzle
import segmentizeAndEnrich
import bufferSegs
import clusterSegs
import tidyData_Segs

import time
import argparse

# ARGUMENTS.
#  * region: a string - which region are we currently looking at? Required for writing files.
#  * boundingBox: bounding box for region; used for querying data from Overpass API
#  * bbCentroid: the bounding box centroid (a lat/lon pair); required for map creation

def main(region):

    highwaydf, junctionsdf, idCoords_dict = dfShizzle.metaFunc(utils.paramDict[region]["bounding_box"], region)

    unfoldedEnrichedDf = segmentizeAndEnrich.metaFunc(highwaydf, junctionsdf, idCoords_dict)

    bufferedDf = bufferSegs.bufferize(unfoldedEnrichedDf)

    oddballs, normies = clusterSegs.cluster(bufferedDf, junctionsdf)

    completeSegments = tidyData_Segs.tidyItUp(region, oddballs, normies)
    
    # Write to pickle for future use

    file_name = f"{region}_segments"

    path = utils.getSubDirPath(file_name, 'pickled_data')

    completeSegments.to_pickle(path)

    return completeSegments

if __name__ == "__main__":

    # Create the argument parser and add arguments

    parser = argparse.ArgumentParser()

    parser.add_argument(dest='region', type=str, help="The region to compute junctions for.")

    # Parse the input parameters

    args = parser.parse_args()

    start_time = time.time()

    completeSegs = main(args.region)

    print("--- %s seconds ---" % (time.time() - start_time))

    file_name = f"hannover_segments_complete_{datetime.date.today()}.csv"

    path = utils.getSubDirPath(file_name, "csv_data")

    completeSegs.to_csv(path, index=False, sep="|")
