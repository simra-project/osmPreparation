#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import requests
import json
import paramsPerRegion
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
#  * buffer_size: junctions are buffered into two-dimensional shapes according to the mean width of the
#                highways intersecting at this junction multiplied with a factor. This factor varies 
#                depending on the city layout.
#  * sortingParams: either ['lat','lon'] or ['lon','lat']; that's because we're sorting the junctions
#                   by location to make some operations more efficient and it is more sensible to
#                   sort by lat resp. lon first depending on the shape of the bounding box 
#                   (long but slim bounding box: sort by lat first; wide but low bb: sort by lon first) 

def main(region, buffer_size):

    nodesdf = dfShizzle.metaFunc(paramsPerRegion.paramDict[region]["bounding_box"])

    junctionsdf = findJunctions.getJunctionsDf(nodesdf, region)

    bufferedJunctionsDf = bufferJcts.bufferize(junctionsdf, buffer_size)

    nonIsolatedJunctions, isolatedJunctions = clusterJcts.cluster(bufferedJunctionsDf, paramsPerRegion.paramDict[region]["neighbour_param"], paramsPerRegion.paramDict[region]["sorting_params"])

    completeJunctions = tidyData_Jcts.tidyItUp(region, paramsPerRegion.paramDict[region]["centroid"], nonIsolatedJunctions, isolatedJunctions, buffer_size, paramsPerRegion.paramDict[region]["sorting_params"])

    return completeJunctions

if __name__ == "__main__":
    completeJunctions = main("stutt",2.5)
    completeJunctions.to_csv("stutt" + '_junctions_complete.csv', index=False, sep="|")
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
