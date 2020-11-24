
import fire

import pandas as pd

import numpy as np

import manualClusterPrep

import mapJcts_clustAssist as mapping

from itertools import starmap

from shapely.geometry.polygon import Polygon 

# ---------------------------------------------------------------------------------------------------

# (*) Helper func for parsing required list properties of df from string

def parseDf(df):

    df['neighbours'] = df['neighbours'].map(lambda x: x[1:(len(x)-1)]).map(lambda x: [int(idx) for idx in x.split(', ')] if x != "" else [])

    df['poly_vertices_lats'] = df['poly_vertices_lats'].map(lambda x: x[1:(len(x)-1)]).map(lambda x: [float(idx) for idx in x.split(', ')])

    df['poly_vertices_lons'] = df['poly_vertices_lons'].map(lambda x: x[1:(len(x)-1)]).map(lambda x: [float(idx) for idx in x.split(', ')])

    df['poly_geometry'] = [x for x in starmap(lambda lats, lons: Polygon(zip(lats, lons)), 
                                                                    list(zip(df['poly_vertices_lats'], df['poly_vertices_lons'])))]

    return df

# RE-MERGE!

# (*) Helper func for re-merging after clusters have been re-assigned

def reMerge(complete_df, new_clust):

    target = complete_df[complete_df["neighbour_cluster"] == new_clust] 

    # Grab the rows from complete_df that are NOT going to be merged

    remainder = complete_df[complete_df["neighbour_cluster"] != new_clust]

    # Melt target rows together

    melted_target = manualClusterPrep.plotPrep(target)

    return pd.concat([remainder, melted_target], ignore_index = True, sort = False)

# Expose functionality as CLI using fire library

# ($) Function for changing a junction's cluster manually via command line

def update_clust(curr_clust, new_clust, region, buffer_size):

    curr_clust = np.float64(curr_clust)
    new_clust = np.float64(new_clust)

    print("test")

    # complete_df = pd.read_csv(f'{region}_jcts_buf={buffer_size}_manual_merging_target.csv', sep='|')

    # complete_df = pd.read_csv('manual_merging_target.csv', sep='|')

    complete_df = pd.read_pickle("manualMergeTarget")

    complete_df.loc[:,'neighbour_cluster'] = complete_df['neighbour_cluster'].map(lambda x: x if x != curr_clust else new_clust)

    # Grab the rows from complete_df that are going to be merged

    # parsed_df = parseDf(complete_df)

    res = reMerge(complete_df, new_clust)

    complete_df = manualClusterPrep.split_and_plot(res, region, buffer_size)

    complete_df.to_csv('manual_merging_target.csv', index=False, sep="|")

if __name__ == '__main__':
  fire.Fire(update_clust)

# python manualMergeTool.py --curr-clust=600.0 --new_clust=605.0 --region="pforz" --buffer_size=2

