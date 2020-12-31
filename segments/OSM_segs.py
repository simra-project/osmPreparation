
#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import requests
import json

import paramsPerRegion
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
#  * sortingParams: either ['lat','lon'] or ['lon','lat']; that's because we're sorting the segments
#                   by location to make some operations more efficient and it is more sensible to
#                   sort by lat resp. lon first depending on the shape of the bounding box 
#                   (long but slim bounding box: sort by lat first; wide but low bb: sort by lon first) 

def main(region, buffer_size):

    highwaydf, junctionsdf, idCoords_dict = dfShizzle.metaFunc(paramsPerRegion.paramDict[region]["bounding_box"], region)

    unfoldedEnrichedDf = segmentizeAndEnrich.metaFunc(highwaydf, junctionsdf, idCoords_dict)

    bufferedDf = bufferSegs.bufferize(unfoldedEnrichedDf)

    oddballs, normies = clusterSegs.cluster(region, bufferedDf, junctionsdf)

    completeSegments = tidyData_Segs.tidyItUp(region, oddballs, normies)

    # completeSegments.to_csv(region + '_segments_complete.csv', index=False, sep="|")

    return completeSegments

if __name__ == "__main__":
    completeSegs = main("stutt",2.5)
    completeSegs.to_csv("stutt" + '_segments_complete.csv', index=False, sep="|")
    # main(["pforz",pforzbb,pforzCentroid,100,3,['lon','lat']])



    



