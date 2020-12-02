#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import requests
import json
import dataAcqAndForm_Jcts as dfShizzle
import findJunctions
import bufferJcts
import clusterJcts
import tidyData_Jcts
pd.set_option('display.max_columns', 200)

import time

import concurrent.futures

# ARGUMENTS.
#  * region: a string - which region are we currently looking at? Required for writing files.
#  * boundingBox: bounding box for region; used for querying data from Overpass API
#  * bbCentroid: the bounding box centroid (a lat/lon pair); required for map creation
#  * neighbourParam: for the purpose of clustering junctions, we sort them by location.
#                    After sorting, it is obvsly not economical to compare every junction to every 
#                    other junction in the df to determine if they're neighbours. Instead, we're only
#                    looking at the x rows above and below each junction. However, this x will be
#                    different for different regions (as the dfs are of different sizes). Hence,
#                    for every region we're trying out different values for this parameter to compare
#                    the results and determine which value is most suitable.
#  * bufferSize: junctions are buffered into two-dimensional shapes according to the mean width of the
#                highways intersecting at this junction multiplied with a factor. This factor varies 
#                depending on the city layout.
#  * sortingParams: either ['lat','lon'] or ['lon','lat']; that's because we're sorting the junctions
#                   by location to make some operations more efficient and it is more sensible to
#                   sort by lat resp. lon first depending on the shape of the bounding box 
#                   (long but slim bounding box: sort by lat first; wide but low bb: sort by lon first) 

def doUntilMerge (region, boundingBox, bbCentroid, neighbourParam, bufferSize, sortingParams): 

    nodesdf = dfShizzle.metaFunc(boundingBox)

    junctionsdf = findJunctions.getJunctionsDf(nodesdf, region)

    bufferedJunctionsDf = bufferJcts.bufferize(junctionsdf, bufferSize)

    nonIsolatedJunctions, isolatedJunctions = clusterJcts.cluster(bufferedJunctionsDf, neighbourParam, sortingParams)

    return nonIsolatedJunctions, isolatedJunctions

def main(args):

    region, boundingBox, bbCentroid, neighbourParam, bufferSize, sortingParams = args

    nonIsolatedJunctions, isolatedJunctions = doUntilMerge(region, boundingBox, bbCentroid, neighbourParam, bufferSize, sortingParams)

    completeJunctions = tidyData_Jcts.tidyItUp(region, bbCentroid, nonIsolatedJunctions, isolatedJunctions, bufferSize, neighbourParam)

    completeJunctions.to_csv(region + '_junctions_complete.csv', index=False, sep="|")

    return f'Finished script for {region}!'

# Define params for different regions

## a) BoundingBoxes

# Working with smaller regions for now; for these, a browser can display a map of the complete area including 
# geometric shapes without dying, so no need to work with sub-bounding boxes and multiple maps.

### I) Bern

bernbb = [7.423641,46.93916,7.469955,46.962112]

### II) Augsburg

augsbb = [10.763362,48.249337,10.959333,48.468336]

### III) Pforzheim

pforzbb = [8.653482,48.873994,8.743249,48.910329]

### IV) Stuttgart

stuttbb = [9.038601,48.692019,9.31582,48.866399]

### V) Wuppertal

wuppbb = [7.014072,51.165803,7.31343,51.318062]

## b) Centroids

bernCentroid = [46.945876,7.415994]

augsCentroid = [48.354761, 10.896351]

pforzCentroid = [48.877046,8.710584]

stuttCentroid = [48.778461,9.177910]

wuppCentroid = [51.240631,7.163216]

## c) Set up param array

params = [
        ["augs",augsbb,augsCentroid,50,2.5,['lat','lon']],
        ["augs",augsbb,augsCentroid,80,2.5,['lat','lon']],
        #
        ["pforz",pforzbb,pforzCentroid,100,2.5,['lon','lat']],
        #
        # ["stutt",stuttbb,stuttCentroid,80,2.5,['lon','lat']],
        #
        ["wupp",wuppbb,wuppCentroid,130,2.5,['lat','lon']],
        #
        # ["wupp",wuppbb,wuppCentroid,80,2],
        # ["wupp",wuppbb,wuppCentroid,80,2.25],
        # ["wupp",wuppbb,wuppCentroid,80,2.5],
        ]

if __name__ == "__main__":
    main(["stutt",stuttbb,stuttCentroid,100,3,['lon','lat']])
    # main(["pforz",pforzbb,pforzCentroid,100,3,['lon','lat']])

'''
start = time.time()

with concurrent.futures.ProcessPoolExecutor() as executor: 

    # This way there are no 'future' objects involved, only the return values. 
    # These are returned in the order in which processes were started
    results = executor.map(main, params)

    # Result is just a string proclaiming that work for a specific region is complete.
    for result in results:
        print(result)

end = time.time()

print(end - start)

'''
