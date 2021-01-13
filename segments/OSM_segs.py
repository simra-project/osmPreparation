
#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import requests
import json
import os
import datetime

import utils
import dataAcqAndForm_Segs as dfShizzle
import segmentizeAndEnrich
import bufferSegs
import clusterSegs
import tidyData_Segs

# ARGUMENTS.
#  * region: a string - which region are we currently looking at? Required for writing files.
#  * boundingBox: bounding box for region; used for querying data from Overpass API
#  * bbCentroid: the bounding box centroid (a lat/lon pair); required for map creation
#  * neighbourParam: for the purpose of clustering segments, we sort them by location.
#                    After sorting, it is obvsly not economical to compare every segment to every 
#                    other segment in the df to determine if they're neighbours. Instead, we're only
#                    looking at the x rows above and below each segment. However, this x will be
#                    different for different regions (as the dfs are of different sizes). Hence,
#                    for every region we're trying out different values for this parameter to compare
#                    the results and determine which value is most suitable.
#  * buffer_size: segment are buffered into two-dimensional shapes according to the mean width of the
#                highway type. Standards likely differ per country.
#  * sortingParams: either ['minx','maxy'] or ['minx','miny]; that's because we're sorting the segments
#                   by location to make some operations more efficient and it is more sensible to
#                   sort by upper left corner resp. lower left corner first depending on the shape of the 
#                   bounding box 
#                   TODO: does this actually make a difference? Would make sense to test empirically .... 

def main(region, buffer_size):

    highwaydf, junctionsdf, idCoords_dict = dfShizzle.metaFunc(utils.paramDict[region]["bounding_box"], region)

    unfoldedEnrichedDf = segmentizeAndEnrich.metaFunc(highwaydf, junctionsdf, idCoords_dict)

    bufferedDf = bufferSegs.bufferize(unfoldedEnrichedDf, buffer_size)

    oddballs, normies = clusterSegs.cluster(region, bufferedDf, junctionsdf)

    completeSegments = tidyData_Segs.tidyItUp(region, oddballs, normies)
    
    # Write to pickle for future use

    # Find out if we're operating in 'segments'-subdirectory or its parent directory,
    # PyPipeline_ (background: we want to write all files related to segments to the
    # segments subdirectory)

    cwd = os.getcwd()

    in_target_dir = utils.inTargetDir(cwd)

    file_name = f"{region}_segments_buffer={buffer_size}"

    path = file_name if in_target_dir else utils.getSubDirPath(file_name, 'pickled_data')

    # Write data frame to pickle folder; include buffer_size in the file name
    # ==> purpose of this is to be able to reuse data in the manual merging
    #     tool so if a data set for a specific region and buffer size already
    #     exists it can be utilized rather than computing everything from scratch again

    completeSegments.to_pickle(utils.getSubDirPath(path))

    return completeSegments

if __name__ == "__main__":

    completeSegs = main("bern",1)

    # Find out if we're operating in 'segments'-subdirectory or its parent directory,
    # PyPipeline_ (background: we want to write all files related to segments to the
    # segments subdirectory)

    cwd = os.getcwd()

    in_target_dir = utils.inTargetDir(cwd)

    file_name = f"bern_segments_complete_{datetime.date.today()}.csv"

    path = file_name if in_target_dir else utils.getSubDirPath(file_name)

    completeSegs.to_csv(path, index=False, sep="|")

    



