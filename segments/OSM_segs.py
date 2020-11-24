
#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import requests
import json

import dataAcqAndForm_Segs as dfShizzle
import segmentizeAndEnrich
import bufferSegs
import clusterSegs
import tidyData_Segs

# ARGUMENTS.
#  * region: a string - which region are we currently looking at? Required for writing files.
#  * boundingBox: bounding box for region; used for querying data from Overpass API
#  * bbCentroid: the bounding box centroid (a lat/lon pair); required for map creation
#  * sortingParams: either ['lat','lon'] or ['lon','lat']; that's because we're sorting the junctions
#                  by location to make some operations more efficient and it is more sensible to
#                  sort by lat resp. lon first depending on the shape of the bounding box 
#                  (long but slim bounding box: sort by lat first; wide but low bb: sort by lon first) 

def main(args):

    # region, boundingBox, bbCentroid, neighbourParam, bufferSize, sortingParams = args

    region, boundingBox, bbCentroid, sortingParams, neighbourParam = args

    highwaydf, junctionsdf, idCoords_dict = dfShizzle.metaFunc(boundingBox, region)

    unfoldedEnrichedDf = segmentizeAndEnrich.metaFunc(highwaydf, junctionsdf, idCoords_dict)

    bufferedDf = bufferSegs.bufferize(unfoldedEnrichedDf)

    oddballs, normies = clusterSegs.cluster(bufferedDf, junctionsdf, sortingParams, neighbourParam)

    completeSegments = tidyData_Segs.tidyItUp(region, bbCentroid, oddballs, normies, neighbourParam)

    completeSegments.to_csv(region + '_segments_complete.csv', index=False, sep="|")

    return f'Finished script for {region}!'

main(["stutt",[9.038601,48.692019,9.31582,48.866399],[48.778461,9.177910],['minx','maxy'],100])


    



