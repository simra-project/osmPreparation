
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

    small_buf['clust_inconsist'] = [x for x in starmap(lambda y, z: 0 if set(y) == set(z) else 1, 
                                                        list(zip(small_buf['neighbours'],large_buf['neighbours'])))]

    large_buf['clust_inconsist'] = [x for x in starmap(lambda y, z: 0 if set(y) == set(z) else 1, 
                                                        list(zip(large_buf['neighbours'],small_buf['neighbours'])))]

    # (III.) Return inconsistent subsets of small_buf and large_buf

    small_buf_inconsist = small_buf[small_buf['clust_inconsist'] == 1] 

    small_buf_consist = small_buf[small_buf['clust_inconsist'] == 0] 

    large_buf_inconsist = large_buf[large_buf['clust_inconsist'] == 1]

    return small_buf_inconsist, small_buf_consist, large_buf_inconsist

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

# TODO RENAME!!!!!

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
# TODO RENAME!!!!!

def split_and_plot (small_buf_inconsist, large_buf_inconsist, region, bufferSize):

    # Split the data frame according to which junctions do/do not have neighbours so neighbour clusters can be
    # dissolved (melted together).

    nonIsolatedJunctions, isolatedJunctions = splitDf(small_buf_inconsist)

    # Melt nonIsolatedJunctions together based on neighbour cluster

    nonIsolatedMelt_small_buf = plotPrep(nonIsolatedJunctions)

    nonIsolatedMelt_large_buf = plotPrep(large_buf_inconsist)

    # Map 

    mapping.runAllMapTasks(region, nonIsolatedMelt_small_buf, isolatedJunctions, nonIsolatedMelt_large_buf, bufferSize)

    # return

    small_buf_inconsist_processed = tidyData_Jcts.explodeAndConcat(nonIsolatedMelt_small_buf, isolatedJunctions)

    large_buf_inconsist_processed = tidyData_Jcts.explodeAndConcat(nonIsolatedMelt_large_buf, pd.DataFrame())

    return small_buf_inconsist_processed, large_buf_inconsist_processed

#*******************************************************************************************************************
# (5) Process consistent junctions (where clustering solutions do not differ between large and small buffers):
#     merge junction clusters geometrically and aggregate the corresponding data, then put back into a df with
#     those junctions that do not belong to a junction cluster

def process_consistent_junctions(small_buf_consist):

    nonIsolated_consistent, isolated_consistent = splitDf(small_buf_consist)

    nonIsolated_consistent_melt = plotPrep(nonIsolated_consistent)

    small_buf_consist_processed = tidyData_Jcts.explodeAndConcat(nonIsolated_consistent_melt, isolated_consistent)

    return small_buf_consist_processed

#*******************************************************************************************************************
# (*) Call all functions in logical order.

def meta_assist (region, small_buf, large_buf):    

    merged_not_melted_small = getData(region, small_buf)

    # merged_not_melted_small.to_csv('merged_not_melted_small.csv', index=False, sep="|")

    merged_not_melted_large = getData(region, large_buf)

    # Get those subsets of the large-/small_buf-df where clusters differ depending on buffer size
    # (property 'clust_inconsist' == True)

    small_buf_inconsist, small_buf_consist, large_buf_inconsist = clusterComp(merged_not_melted_small, merged_not_melted_large)

    # Split the 'clust_inconsist' == True - subset of the small_buf_df into junctions with/without neighbours
    # (other junctions exhibiting an overlapping polygon surface);
    # dissolve/aggregate the non-isolated junctions per cluster;
    # plot the inconsistent clusters in the small_buf- and large_buf-df onto the same map for comparison purposes;
    # merge the isolated- and non-isolated junctions in the inconsistent subset of the small_buf-df back together
    # --> return the 'processed' inconsistent subset of the small_buf-df

    small_buf_inconsist_processed, large_buf_inconsist_processed = split_and_plot(small_buf_inconsist, large_buf_inconsist, region, small_buf)

    # small_buf_inconsist_processed.to_csv('manual_merging_target.csv', index=False, sep="|")

    # PICKLE (SERIALIZE) THREE DATA SETS FOR USE BY MANUALMERGETOOL:
    # (1) 'small_buf_inconsist': subset of the small buffer df where clustering solutions differ from the
    #     larger buffer solution.
    # (2) 'large_buf_inconsist': subset of the large buffer df where clustering solutions differ from the
    #     smaller buffer solution. 
    # (3) 'consistent_clusters': subset of the small buffer df where clustering solutions DO NOT differ from
    #     the larger buffer solution; i.e. if this subset was taken from the large buffer df it would be exactly
    #     the same.

    # INTENDED PROCESSING OF THESE DATA SETS IN MANUALMERGETOOL:
    # * The more conservative solutions contained in 'small_buf_inconsist' can be manually edited, i.e. replaced by the 
    #   more liberal solutions contained in 'large_buf_inconsist'. 
    # * That means, when a user compares the rivaling conservative vs. liberal solutions for inconsistent clusters, 
    #   she might decide to pick the liberal solution over the conservative one. 
    # * Hence, the respective rows belonging to the conservative solution are DELETED from the 'small_buf_inconsist'
    #   df and the respective row belonging to the liberal solution is taken from the 'large_buf_inconsist' data set
    #   and MOVED to 'small_buf_consist', our 'base' df which will be returned after all of the manual editing is
    #   finished. This means that the conflict has been resolved.
    # * When all editing is done, what remains of 'small_buf_inconsist' (i.e., the conservative solutions that
    #   were chosen over their liberal counterparts) is concatenated with 'consistent_clusters', which already
    #   contains all the more liberal solutions that were chosen over the conservative ones.

    small_buf_inconsist_processed.to_pickle("small_buf_inconsist")

    # small_buf_inconsist_processed.to_csv('small_buf_inconsist.csv', index=False, sep="|")

    large_buf_inconsist_processed.to_pickle("large_buf_inconsist")

    # large_buf_inconsist_processed.to_csv('large_buf_inconsist.csv', index=False, sep="|")

    small_buf_consist_processed = process_consistent_junctions(small_buf_consist)

    small_buf_consist_processed.to_pickle("consistent_clusters")

if __name__ == "__main__":
    meta_assist("stutt", 2, 2.5)