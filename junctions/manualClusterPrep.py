
import pandas as pd

import numpy as np

from itertools import starmap

from shapely.geometry.polygon import Polygon 

import geopandas as gpd

import mapJcts_clustAssist as mapping

import collections

# INTERNAL IMPORTS: 

import OSM_jcts

import tidyData_Jcts

import paramsPerRegion

#*******************************************************************************************************************
# (*) Generate data frames using functionality from the project's main script, 'OSM_jcts'

def getData (region, buffer_size):

    bounding_box, bb_centroid, neighbour_param, sorting_params = paramsPerRegion.paramDict[region]['bounding_box'], paramsPerRegion.paramDict[region]['centroid'], paramsPerRegion.paramDict[region]['neighbour_param'], paramsPerRegion.paramDict[region]['sorting_params']

    non_isolated_junctions, isolated_junctions = OSM_jcts.doUntilMerge(region, bounding_box, bb_centroid, neighbour_param, buffer_size, sorting_params)

    clustered_jcts_before_merge = pd.concat([non_isolated_junctions, isolated_junctions], ignore_index = True, sort = False)

    return clustered_jcts_before_merge

#*******************************************************************************************************************
# (1) Check where junctions have been assigned to different clusters depending on buffer size. 
#     Assign this new property ('clust_inconsist') to the data frame generated with the small buffer. 
#
#     (Because obviously, it is much easier to perform additional merges where they haven't yet taken place,
#     an operation we can perform based on the data generated using the small buffer, than to undo merges that
#     have already taken place, an operation we could possibly perform based on the data generated using the large 
#     buffer.)

# 'Comp' is for 'Comparison', not 'Computation' in case you were wondering (I personally was wondering one day
# after writing this)

def clusterComp (small_buf, large_buf):

    # (I.) Sort according to ID to make sure the two dfs are aligned.

    small_buf.sort_values(by='id',inplace=True)

    small_buf.reset_index(inplace=True, drop=True)

    large_buf.sort_values(by='id',inplace=True)

    large_buf.reset_index(inplace=True, drop=True)

    # (II.) Calculate difference: neighbour clusters have different members.

    small_buf['clust_inconsist'] = [x for x in starmap(lambda x, y: 1 if not set(x) == set(y) else 0, 
                                                        list(zip(small_buf['neighbours'],large_buf['neighbours'])))]

    return small_buf

#*******************************************************************************************************************
# (2) Split the df according to 'junction has/does not have neighbours'

def splitDf (junctionsdf):

    print(junctionsdf['neighbours'])

    ## a) Deal with nonIsolatedJunctions

    ###### NOTE: the '.copy()' tells pandas we're creating copies of the original df; doing so prevents the 'settings with copy warning'. 

    nonIsolatedJunctions = junctionsdf.loc[junctionsdf['neighbours'].map(lambda d: len(d)) > 0, :].copy()

    nonIsolatedJunctions.reset_index(inplace=True, drop=True)

    ## b) Deal with isolatedJunctions

    isolatedJunctions = junctionsdf.loc[junctionsdf['neighbours'].map(lambda d: len(d)) == 0, :].copy()

    isolatedJunctions.reset_index(inplace=True, drop=True)

    return nonIsolatedJunctions, isolatedJunctions

#*******************************************************************************************************************
# (3) Merge junctions according to their neighbour clusters:
#     polygon shapes of junctions in the same cluster are dissolved, i.e. melted together;
#     the remaining columns are also aggregated by cluster. 
#     (Naturally, these operations are only performed for the 'non-isolated junctions', i.e. those whose polygon surfaces
#     overlap with those of other junctions) 
#    
#     (This function isn't called directy by this script's main function, but only by split_and_plot. It is also
#     called by the manualMergeTool.)

def plotPrep (nonIsolatedJunctions):

    ## a) Merge neighbour clusters: dissolving geometric shapes according to a shared property can be achieved using [geopandas](https://www.earthdatascience.org/workshops/gis-open-source-python/dissolve-polygons-in-python-geopandas-shapely/)

    # Make a df with cluster ID and polygon only so we can use geopandas' dissolve method to merge the poly shapes for each cluster.

    geoJunctions = gpd.GeoDataFrame(nonIsolatedJunctions.neighbour_cluster, geometry=nonIsolatedJunctions.poly_geometry)

    junctionClusters = geoJunctions.dissolve(by='neighbour_cluster')

    ## (b) Join the remaining df columns too using pandas groupby and merge everything together

    nonIsolatedJunctions = nonIsolatedJunctions.drop(["poly_vertices_lats", "poly_vertices_lons", "poly_geometry"], axis=1)

    nonIsolatedJunctions = nonIsolatedJunctions.groupby('neighbour_cluster', as_index = False).agg({'id': lambda x: ', '.join(map(str, x)), 'lat': lambda x: ', '.join(map(str, x)), 'lon': lambda x: ', '.join(map(str, x)), 'highwayids': 'sum', 'highwaynames': 'sum', 'highwaytypes': 'sum', 'highwaylanes': 'sum','highwaylanesBw': 'sum', 'neighbours': 'sum','clust_inconsist': 'sum'})

    nonIsolatedMelt = pd.merge(nonIsolatedJunctions, junctionClusters, on='neighbour_cluster')

    return nonIsolatedMelt

#*******************************************************************************************************************
# (4) This function does many things, please refer to descriptions of the respective steps below

def split_and_plot (df, region, bufferSize):

    # Split the data frame according to which junctions do/do not have neighbours so neighbour clusters can be
    # dissolved (melted together).

    nonIsolatedJunctions, isolatedJunctions = splitDf(df)

    # Melt nonIsolatedJunctions together based on neighbour cluster

    nonIsolatedMelt = plotPrep(nonIsolatedJunctions)

    # Map 

    mapping.runAllMapTasks(region, nonIsolatedMelt, isolatedJunctions, bufferSize)

    # return

    complete_df = tidyData_Jcts.explodeAndConcat(nonIsolatedMelt, isolatedJunctions)

    return complete_df

#*******************************************************************************************************************
# (*) Call all functions in logical order.

def meta_assist (region, small_buf, large_buf):    

    merged_not_melted_small = getData(region, small_buf)

    # merged_not_melted_small.to_csv('merged_not_melted_small.csv', index=False, sep="|")

    merged_not_melted_large = getData(region, large_buf)

    # comp_res corresponds to small_buff enriched with the information on where clusters differ depending on buffer size
    # (property 'clust_inconsist')

    comp_res = clusterComp (merged_not_melted_small, merged_not_melted_large)

    # split_and_plot does everything else: merging, plotting, data hygiene

    complete_df = split_and_plot(comp_res, region, small_buf)

    complete_df.to_csv('manual_merging_target.csv', index=False, sep="|")

    complete_df.to_pickle("manualMergeTarget")

if __name__ == "__main__":
    meta_assist("pforz", 2, 3)