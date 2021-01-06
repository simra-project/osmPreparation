
import pandas as pd

import numpy as np

from itertools import starmap

from shapely.geometry.polygon import Polygon 

import geopandas as gpd

import mapJcts_clustAssist_jcts as mapping

import collections

import os

# INTERNAL IMPORTS: 

import OSM_jcts

import tidyData_Jcts

import utils

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

def determine_inconsistencies (small_buf, large_buf):

    # TO DETERMINE: which junctions clusters (consisting of individual - isolated - junctions without neighbours
    #               or multiple junctions that were clustered together due to overlapping surfaces) are 
    #               idential in both data frames, i.e. appear irrespective of buffer size? Which ones don't?

    # STRATEGY:
    # (1) Currently, junction IDs appear in the form [3485629] (isolated junction without neighbours) or
    #     [7837590, 872343, 96245] (junction cluster, i.e. merge of multiple individual junctions). 
    #      Convert these data types to sets of ints/longs, sorted strings or some other form that allows
    #      for comparison irrespective of order.

    small_buf['id'] = small_buf['id'].sort_values().apply(lambda l: sorted(l)).map(lambda s: ', '.join(map(str, s)))

    large_buf['id'] = large_buf['id'].sort_values().apply(lambda l: sorted(l)).map(lambda s: ', '.join(map(str, s)))

    # (2) Grab the two ID columns from the df and determine their intersection 
    #     (= the clusters that consistently appear in both data frames)

    small_buf_clust_set = set(small_buf['id'])

    large_buf_clust_set = set(large_buf['id'])

    consistent_solutions = small_buf_clust_set.intersection(large_buf_clust_set)

    # (3) Flag the inconsistent rows in the two dfs (= rows whose ids aren't contained in consistent_solutions). 
    #     Split dfs accordingly. Return.

    small_buf['clust_inconsist'] = small_buf['id'].map(lambda x: 0 if x in consistent_solutions else 1)

    large_buf['clust_inconsist'] = large_buf['id'].map(lambda x: 0 if x in consistent_solutions else 1)

    small_buf_inconsist = small_buf[small_buf['clust_inconsist'] == 1].copy() 

    small_buf_consist = small_buf[small_buf['clust_inconsist'] == 0].copy() 

    large_buf_inconsist = large_buf[large_buf['clust_inconsist'] == 1].copy()

    return small_buf_inconsist, small_buf_consist, large_buf_inconsist

#*******************************************************************************************************************
# (*) Call all functions in logical order.

def meta_assist (region, small_buf, large_buf):    

    # Get data frames for small_buf (more conservative buffer parameter) and large_buf (more liberal buffer parameter)

    small_buf = OSM_jcts.main(region, small_buf)

    large_buf = OSM_jcts.main(region, large_buf)

    # Determine where the two data frames (and thus the clustering solutions for smaller and larger buffer) differ

    small_buf_inconsist, small_buf_consist, large_buf_inconsist = determine_inconsistencies(small_buf, large_buf)

    mapping.runAllMapTasks(region, small_buf_inconsist, large_buf_inconsist)

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

    # Find out if we're operating in 'junctions'-subdirectory or its parent directory,
    # PyPipeline_ (background: we want to write all files related to junctions to the
    # junctions subdirectory)

    cwd = os.getcwd()

    in_target_dir = utils.inTargetDir(cwd) # bool

    # Write small_buf_inconsist pickle

    small_buf_inconsist_path = f"jcts_small_buf_inconsist_{region}" if in_target_dir else utils.getSubDirPath(f"jcts_small_buf_inconsist_{region}")

    small_buf_inconsist.to_pickle(small_buf_inconsist_path)

    # Write large_buf_inconsist pickle

    large_buf_inconsist_path = f"jcts_large_buf_inconsist_{region}" if in_target_dir else utils.getSubDirPath(f"jcts_large_buf_inconsist_{region}")

    large_buf_inconsist.to_pickle(large_buf_inconsist_path)

    # Write consistent clusters pickle

    consistent_clusters_path = f"jcts_consistent_clusters_{region}" if in_target_dir else utils.getSubDirPath(f"jcts_consistent_clusters_{region}")

    small_buf_consist.to_pickle(consistent_clusters_path)
