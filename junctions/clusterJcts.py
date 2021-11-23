
from tqdm import tqdm

from collections import Counter

import numpy as np
import pandas as pd
import h3

# ## Cluster junctions

#*******************************************************************************************************************
# (1) Define functionality for determining a junction's neighbours

# a) Check if the overlap of two junction polygons is above a specified threshold - could be parameterized as well,
#    of course (didn't seem necessary so far, but might be done in the future.)

def largeIntersection(poly1, poly2):
    if not (poly1.intersects(poly2)):
        return False
    elif (((poly1.intersection(poly2).area/poly1.area)*100) > 8):
        return True
    elif (((poly1.intersection(poly2).area/poly2.area)*100) > 8):
        return True

# c) Check if two junctions share a square (which means they should end up in the same cluster)
def sharedSquare(lst1, lst2): 
    lst3 = [value for value in lst1 if value in lst2]
    if lst3 != []:
        for elem in lst3:
            if 'platz' in elem or 'Platz' in elem:
                return True
    return False

# c) Put it all together to assign its neighbours to each junction

def findNeighboursH3(junctionsdf):

    # Now more efficient using h3
    # Python API can be found here: https://github.com/uber/h3-py/blob/master/src/h3/api/_api_template.py

    # define h3 resolution
    # Resolution 8 corresponds to an average hexagon area of 0.737 km^2 
    # (the higher the resolution, the smaller the area covered by each individual hexagon,
    # see https://h3geo.org/docs/core-library/restable/)
    h3_resolution = 8

    # Add h3 column - each junction is assigned a spatial index based on its lat/lon
    junctionsdf["h3"] = junctionsdf.apply (lambda row: h3.geo_to_h3(row["lat"], row["lon"], h3_resolution), axis=1)

    # Use buffer trick if polygon is invalid
    # https://stackoverflow.com/questions/13062334/polygon-intersection-error-in-shapely-shapely-geos-topologicalerror-the-opera
    junctionsdf['poly_geometry'] = junctionsdf['poly_geometry'].map(lambda poly: poly if poly.is_valid else poly.buffer(0))

    # Isolate the h3 & index columns
    df_h3_only = pd.DataFrame(junctionsdf.h3.tolist(), index=junctionsdf.index)

    # set up tdqm for progress bar
    ops_number = junctionsdf.index.size
    bar = tqdm(total=ops_number, desc="Computing Neighbours")

    neighbours_list = []

    # Iterate over junctionsdf and look for neighbours among junctions in the same h3 ring

    checked = 0

    for ind in junctionsdf.index:

        row = junctionsdf.loc[ind]
        ######## for some reason, row["h3"] contains multiple identical elements. In that case, take the first.
        if isinstance(row["h3"], pd.Series):
            row = row.iloc[0]

        '''
        API for k_ring: 
        'Return unordered set of cells with H3 distance `<= k` from `h`.
        That is, the "filled-in" disk.'
        
        As opposed to hex_ring:
        'Return unordered set of cells with H3 distance `== k` from `h`.
        That is, the "hollow" ring.'

        Source: https://github.com/uber/h3-py/blob/master/src/h3/api/_api_template.py
        '''

        h3_disk = h3.k_ring(row["h3"], 1)

        # From https://stackoverflow.com/questions/53342715/pandas-dataframe-select-rows-where-a-list-column-contains-any-of-a-list-of-strin
        rows_to_check = junctionsdf[df_h3_only.isin(h3_disk).any(1).values]
        checked += rows_to_check.size

        neighbour_rows = rows_to_check[rows_to_check.apply(lambda apply_row: (largeIntersection(apply_row['poly_geometry'],row["poly_geometry"]) or sharedSquare(apply_row['highwaynames'], row['highwaynames'])), axis=1)]

        # Grab indices of those rows that passed the filter
        neighbours = neighbour_rows.index.tolist()
        # remove use from the neighbourslist
        neighbours.remove(ind)

        neighbours_list.append(neighbours)
        bar.update(1)

    print(f"Checked on average {checked / junctionsdf.index.size} entries for neighbours")

    # remove row number
    junctionsdf.drop(columns=['h3'], inplace=True)
    junctionsdf['neighbours'] = neighbours_list
    bar.close()

    # junctionsdf.dropna(subset=['neighbours'], inplace=True)

    return junctionsdf

def getNeighbours(outerInd, outerPoly, outerHighways, row_number, index_list, poly_list, highway_list):
    max_row_diff = 1500
    # we do not need to check all rows for neighbours. to be safe, let's check max_row_diff above and max_row_diff below row number
    lower_range = max(0, row_number - max_row_diff)
    upper_range = min(len(index_list), row_number + max_row_diff)

    # check largeIntersection or sharedSquare for each item in poly_list/highway_list
    neighbours = []
    for i in range(lower_range, upper_range):
        if outerInd == index_list[i]:
            continue

        intersection = largeIntersection(poly_list[i], outerPoly)
        square = sharedSquare(highway_list[i], outerHighways)

        if intersection or square:
            diff_percentage = abs(row_number - i) / float(max_row_diff)
            if diff_percentage >= 0.8:
                print("Row difference at {0!s}%, absolute max_row_diff is {1!s}".format(diff_percentage, abs(row_number - i)))

            neighbours.append(index_list[i])

    return neighbours

#*******************************************************************************************************************
# (2) Split the df according to 'junction has/does not have neighbours'

def splitDf (junctionsdf):

    ## a) Deal with nonIsolatedJunctions

    ###### NOTE: the '.copy()' tells pandas we're creating copies of the original df; doing so prevents the 'settings with copy warning'. 

    nonIsolatedJunctions = junctionsdf.loc[junctionsdf['neighbours'].map(lambda d: len(d)) > 0, :].copy()

    ## b) Deal with isolatedJunctions

    isolatedJunctions = junctionsdf.loc[junctionsdf['neighbours'].map(lambda d: len(d)) == 0, :].copy()

    return nonIsolatedJunctions, isolatedJunctions

#*******************************************************************************************************************
# (3) Functionality for performing the actual clustering on nonIsolatedJunctions

def clusterNeighbours(df):

    clusterInd = 0
    
    # Store the indices of rows we've already assigned a cluster to.
    
    included = []
    
    for ind in df.index:
        
        # Do not look at rows we've already assigned clusters to 
        # (at least not in this - the outer - loop. Why?
        # because a cluster detected in the inner loop is complete.)
        
        if ind in included:

            continue

        else:

            currNeighbours = []
            
            # Assign the current cluster index to the row.
        
            df.at[ind, 'neighbour_cluster'] = clusterInd

            # Add the current row's index to the list of rows that were already visited.
            
            included.append(ind)
            
            # Initialize list of neighbours in cluster with this row's neighbours.
            # NOTE: 'extend' adds a list to another list while avoiding creating a 
            #       list of lists. 'Append' adds a single element to a list.
        
            currNeighbours.extend(df.at[ind,'neighbours'])
            
            # Add the row's index to the neighbour list too.
            
            currNeighbours.append(ind)
        
            # Now iterate through the df again to find the neighbours' neighbours.

            ######## flatten the list if currNeighbours is a list of lists
            currNeighboursCleaned = []
            for i, elem in enumerate(currNeighbours):
                if isinstance(currNeighbours[i], list):
                    for j, elem2 in enumerate(currNeighbours[i]):
                        currNeighboursCleaned.append(currNeighbours[i][j])
                else:
                    currNeighboursCleaned.append(currNeighbours[i])

            included = expandNeighbours(df, clusterInd, ind, list(set(currNeighboursCleaned)), included)
            # No more extended neighbours, up the cluster numbers
        
            clusterInd += 1

    return df

def expandNeighbours(df, clusterInd, outerInd, currNeighbours, included):
    # Create a queue based on currNeighbours (the neighbours of the data point in the
    # row considered in the outer loop).

    neighbour_queue = []

    for elem in currNeighbours:

        neighbour_queue.append(elem)
    
    while len(neighbour_queue) != 0:

        # Remove first element from queue

        nextNeighbour = neighbour_queue.pop(0)
        ######## skip this neighbour if it is already in included (because, somehow there are still duplicates...)
        if nextNeighbour in included:
            continue

        # Add nextNeighbour to the list of included data points so it won't be
        # considered in the outer loop

        included.append(nextNeighbour)

        # Assign the cluster nr. to nextNeighbour
        print(f"clusterInd: {clusterInd}")
        print(f"df.loc[{nextNeighbour}]:\n {df.loc[nextNeighbour]}")
        print(f"df.loc[{nextNeighbour}].size: {df.loc[nextNeighbour].size}")
        print(f"df.loc[{nextNeighbour}].shape: {df.loc[nextNeighbour].shape}")
        df.at[nextNeighbour, 'neighbour_cluster'] = clusterInd

        # Grab the next neighbour's neighbours

        nextNeighsNeighs = df.at[nextNeighbour,'neighbours']

        # Find any distinct neighbours of this neighbour (that aren't already contained in the cluster)

        distinctNewNeighs = [x for x in nextNeighsNeighs if x not in currNeighbours]
        
        # If any distinct new neighbours have been found, add them to the cluster members list (currNeighbours)
        # as well as the queue

        if distinctNewNeighs != []:

            currNeighbours.extend(distinctNewNeighs)

            neighbour_queue.extend(distinctNewNeighs)
        
    return included

#*******************************************************************************************************************
# (4) Separate undesired merges

def clusterCorrection(nonIsolatedJunctions):

    nonIsolatedJunctions.loc[:,'unmerge'] = ''

    ## a) Set up some stuff that will help us find out where clustering produced undesired results

    ### Aggregate highwaynames and -types in each cluster

    highwaysPerCluster = nonIsolatedJunctions[['highwaynames','highwaytypes','neighbour_cluster']].copy()

    highwaysPerClusterDict = highwaysPerCluster.groupby('neighbour_cluster').agg('sum').to_dict() 

    #### Determine the size of neighbour clusters

    membersPerCluster = nonIsolatedJunctions.groupby('neighbour_cluster').size().to_dict()

    ### Set up a function for determining if a junction is located at a large highway:

    def largeHighwayJunction(highwayTypeList, clusterSize):
    
        largeBois = ['primary','secondary','secondary_link']
    
        return len([s for s in highwayTypeList if any(xs in s for xs in largeBois)]) >= (clusterSize - 1)

    ### Set up a function for determining if a list of highwaynames contains the word 'platz'/'Platz' (square):
    ### [obvsly this one needs to be adapted for non-German-speaking locations]

    def checkForSquare(highwayNameList):
    
        matchers = ['Platz','platz']
    
        # Yup this is very 'pythonic' ... I speak pythonic now!! Jk I stole it from the internet

        return [s for s in highwayNameList if any(xs in s for xs in matchers)] != []

    ### This function targets a situation that was observed at Gierkeplatz in Berlin-Charlottenburg:
    ### here one too many junctions was merged into a cluster constituting a square; 
    ### this case can be described as a junction sharing only one distinct highway with a 
    ### cluster that contains a square; however that one shared highway is not the square described
    ### by the cluster.

    def gierkePlatzSituation(clusterHighways, sharedHighways):
    
        # (1) The cluster contains a square.
        
        if checkForSquare(clusterHighways):
            
        # (2) rowHighways and (clusterHighways - rowhighways) only share one element.
        
            if len(sharedHighways) == 1:
        
        # (3) If the previous two conditions are met and the one additional highway contained in
        #     sharedHighways is not a square, unmerge.
        
                if not checkForSquare(sharedHighways):
            
                    return True
        
        return False

    #### Finally, this function uses all the data and functionality defined above to determine 
    #### where we need to un-merge.

    def rowsToUnmerge(clusterHighwayTypes, clusterHighwayNames, clusterSize, rowHighwayNames):
        
        # Subtract the current row's (junction's) list of associated highways from the ones in the
        # cluster the row (junction) belongs to WHILE BOTH MAY STILL CONTAIN DUPLICATES!! 
        # Logic behind this: we want to find out which elements rowhighways and clusterhighways truly
        # have in common (if we didn't do this subtraction first all of the highways in rowhighways
        # would be included in clusterhighways)

        res = list((Counter(clusterHighwayNames) - Counter(rowHighwayNames)).elements())
                
        # Use this neat set operation to remove duplicates

        noDupsRes = list(set(res))

        sharedHighways = list(set([value for value in rowHighwayNames if value in noDupsRes]))

        # Don't unmerge if the row (junction) shares more than one highway with the cluster.

        if len(sharedHighways) >= 2:

            return False

        # Don't unmerge if we're dealing with a small cluster.

        elif clusterSize <= 3:

            return False

        # Don't unmerge if we're dealing with a junction located at a very large highway:

        elif largeHighwayJunction(clusterHighwayTypes, clusterSize):

            return False

        elif gierkePlatzSituation(clusterHighwayNames, sharedHighways):

            return True

        else:

            return False

    ## b) Now apply all of the stuff defined in a).

    clusterHighwayTypes = nonIsolatedJunctions['neighbour_cluster'].map(highwaysPerClusterDict.get('highwaytypes', {}).get)

    clusterHighwayNames = nonIsolatedJunctions['neighbour_cluster'].map(highwaysPerClusterDict.get('highwaynames', {}).get)

    clusterSizes = nonIsolatedJunctions['neighbour_cluster'].map(membersPerCluster.get)
    rowHighwayNames = nonIsolatedJunctions['highwaynames']

    nonIsolatedJunctions.loc[:,'unmerge'] = np.vectorize(rowsToUnmerge)(clusterHighwayTypes,clusterHighwayNames,clusterSizes,rowHighwayNames)

    ### unmergeFPs = unmerge false positives

    def unmergeFPs(df):

        nextCluster = (df['neighbour_cluster'].max() + 1)
        
        for ind in df.index:
            
            if df.at[ind,'unmerge'] == True:
                
                df.at[ind,'neighbour_cluster'] = nextCluster
                
                nextCluster += 1
                
            else:
                
                continue

    unmergeFPs(nonIsolatedJunctions)

    nonIsolatedJunctions = nonIsolatedJunctions.drop("unmerge",axis=1)

    return nonIsolatedJunctions

#*******************************************************************************************************************
# (X) Call all the functions required for clustering in logical order.

def cluster (junctionsdf):

    # 0.) Drop rows with ^ in relevant columns
    junctionsdf = junctionsdf[junctionsdf['highwaynames'].astype(bool)]
    junctionsdf = junctionsdf[junctionsdf['highwaytypes'].astype(bool)]
    junctionsdf = junctionsdf[junctionsdf['poly_geometry'].astype(bool)]

    junctionsdf.dropna(subset=['highwaynames','poly_geometry','highwaytypes'], inplace=True)

    # I.) Determine which junctions have neighbours and which do not 

    junctionsdf.set_index('id', inplace=True)

    junctionsWithNeighbourProperty = findNeighboursH3(junctionsdf)

    # II.) Split the df according to 'junction has/does not have neighbours'

    nonIsolatedJunctions, isolatedJunctions = splitDf(junctionsWithNeighbourProperty)

    # III.) Cluster the nonIsolatedJunctions

    nonIsolatedJunctions = clusterNeighbours(nonIsolatedJunctions)

    # IV.) Separate undesired merges

    nonIsolatedJunctions = clusterCorrection(nonIsolatedJunctions)

    # V.) Reset indices to normal integer ones

    nonIsolatedJunctions.reset_index(inplace=True, drop=False)

    isolatedJunctions.reset_index(inplace=True, drop=False)

    # VI.) Add a cluster to the isolated junctions too (each will have their own, due to their isolation :'( ))

    max_ni_clust = nonIsolatedJunctions['neighbour_cluster'].max() 

    isolatedJunctions["neighbour_cluster"] = isolatedJunctions.index.map(lambda x: max_ni_clust + x)

    return nonIsolatedJunctions, isolatedJunctions



    




    