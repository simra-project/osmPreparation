
from itertools import starmap

from collections import Counter

import numpy as np

# ## Cluster junctions

# This implementation is following a brute-force approach with O(n^2) complexity, more elegantly it could be done with a [union find algo](https://medium.com/jeremy-gottfrieds-tech-blog/weighted-union-find-a-fascinating-and-elegant-algorithm-ae61aa0ab1e1). (See also the [Algorithms, Pt. I course by Princeton University on Coursera](https://www.coursera.org/learn/algorithms-part1#enroll))

# ***UPDATE: we're not at n^2 anymore!!!***
# 
# How so, you ask? Well:
# - firstly, we sort the df according to geospatial location. There's multiple strategies for doing this: a) according to upper left corner of polygon (minx, maxy); b) according to polygon centroid, c) simple: in the case of junction just lat/lon.
# - then we're only looking at the X data points above/below each junction to find neighbours.

#*******************************************************************************************************************
# (1) Define functionality for determining a junction's neighbours

# a) Check if the overlap of two junction polygons is above a specified threshold - could be parameterized as well,
#    of course (didn't seem necessary so far, but might be done in the future.)

def largeIntersection(poly1, poly2):
    return poly1.intersects(poly2) and ((poly1.intersection(poly2).area/poly1.area)*100) > 8

# c) Check if two junctions share a square (which means they should end up in the same cluster)
def sharedSquare(lst1, lst2): 
    lst3 = [value for value in lst1 if value in lst2]
    if lst3 != []:
        for elem in lst3:
            if 'platz' in elem or 'Platz' in elem:
                return True
    return False

# c) Put it all together to assign its neighbours to each junction

def neighbourFindingWrapper(junctionsdf):

    def getNeighbours(outerInd, outerPoly, outerHighways):

        # Filter df according to poly overlap or shared square

        neighs = junctionsdf[junctionsdf.apply(lambda row: (largeIntersection(row['poly_geometry'],outerPoly) or sharedSquare(row['highwaynames'], outerHighways)), axis=1)]
        
        neighbours = list(neighs.index)

        neighbours.remove(outerInd)               
                        
        return neighbours

    # Use buffer trick if polygon is invalid
    # https://stackoverflow.com/questions/13062334/polygon-intersection-error-in-shapely-shapely-geos-topologicalerror-the-opera

    junctionsdf['poly_geometry'] = junctionsdf['poly_geometry'].map(lambda poly: poly if poly.is_valid else poly.buffer(0))   

    junctionsdf['neighbours'] = [x for x in starmap(getNeighbours, list(zip(junctionsdf.index,junctionsdf['poly_geometry'],junctionsdf['highwaynames'])))]

    return junctionsdf

#*******************************************************************************************************************
# (2) Split the df according to 'junction has/does not have neighbours'

def splitDf (junctionsdf):

    ## a) Deal with nonIsolatedJunctions

    ###### NOTE: the '.copy()' tells pandas we're creating copies of the original df; doing so prevents the 'settings with copy warning'. 

    nonIsolatedJunctions = junctionsdf.loc[junctionsdf['neighbours'].map(lambda d: len(d)) > 0, :].copy()

    # Sort by location once more to make the clustering process we'll perform on this df more efficient.

    nonIsolatedJunctions.sort_values(by=['lat','lon'],inplace=True)

    nonIsolatedJunctions.reset_index(inplace=True, drop=True)

    ## b) Deal with isolatedJunctions

    isolatedJunctions = junctionsdf.loc[junctionsdf['neighbours'].map(lambda d: len(d)) == 0, :].copy()

    isolatedJunctions.reset_index(inplace=True, drop=True)

    #isolatedJunctions = isolatedJunctions.drop('level_0', axis=1)

    return nonIsolatedJunctions, isolatedJunctions

#*******************************************************************************************************************
# (3) Functionality for performing the actual clustering on nonIsolatedJunctions

def expandNeighbours(df, neighbourParam, clusterInd, outerLoopInd, currNeighbours, included):
    
    lower = max(outerLoopInd-neighbourParam, 0)
    
    current = lower
    
    upper = min(outerLoopInd+neighbourParam, len(df)-1)
    
    members = [outerLoopInd]
    
    while current < upper:

        theseNeighbours = []
        
        theseNeighbours.extend(df.at[current,'neighbours'])
        
        theseNeighbours.append(df.at[current,'id'])
            
        # Expand the list of neighbours and neighbours' neighbours as
        # we iterate through the df.
    
        if not(current in members) and any(x in currNeighbours for x in theseNeighbours):

            currNeighbours.extend(theseNeighbours)
        
            # If another row belonging to the cluster has been found, 
            # assign it the cluster id ...
        
            df.at[current,'neighbour_cluster'] = clusterInd
            
            # ... and append the row's index to the list of included
            # rows.
            
            included.append(current)
            
            # add the row's index to the cluster member list to avoid 
            # getting caught in an endless loop
            
            members.append(current)
            
            # TRESET HE INDEX TO 0 SO WE'RE STARTING TO ITERATE THROUGH
            # THE DF FROM THE TOP AGAIN EVERY TIME A NEIGHBOUR CLUSTER
            # HAS BEEN EXPANDED BY ONE MORE JUNCTION

            current = lower
                
        else:
                
            current += 1
        
    return included

def clusterNeighbours(df, neighbourParam):
    
    clusterInd = 0
    
    # Store the indices of rows we've already assigned a cluster to.
    
    included = []
    
    for ind in df.index:
        
        currNeighbours = []
        
        # Do not look at rows we've already assigned clusters to 
        # (at least not in this - the outer - loop)
        
        if ind in included:

            continue

        else:
            
            # Assign the current cluster index to the row.
        
            df.at[ind,'neighbour_cluster'] = int(clusterInd)
            
            # Add the current row's index to the list of rows that were already visited.
            
            included.append(ind)
            
            # Initialize list of neighbours in cluster with this row's neighbours.
        
            currNeighbours.extend(df.at[ind,'neighbours'])
            
            # Add the row's index to the neighbour list too.
            
            currNeighbours.append(df.at[ind,'id'])
            
            #if not (currNeighbours == [] or np.isnan(currNeighbours)):
        
            # Now iterate through the df again to find the neighbours' neighbours.

            included = expandNeighbours(df, neighbourParam, clusterInd, ind, currNeighbours, included)
                    
            # No more extended neighbours, up the cluster numbers
        
            clusterInd += 1

    return df

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

    def gierkePlatzSituation(rowHighways, clusterHighways, sharedHighways):
    
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

        elif gierkePlatzSituation(rowHighwayNames, clusterHighwayNames, sharedHighways):

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

def cluster (junctionsdf, neighbourParam, sortingParams):

    # I.) Determine which junctions have neighbours and which do not 

    junctionsdf = neighbourFindingWrapper(junctionsdf)

    # II.) Split the df according to 'junction has/does not have neighbours'

    nonIsolatedJunctions, isolatedJunctions = splitDf(junctionsdf)

    # III.) Cluster the nonIsolatedJunctions

    nonIsolatedJunctions = clusterNeighbours(nonIsolatedJunctions, neighbourParam)

    # IV.) Separate undesired merges

    nonIsolatedJunctions = clusterCorrection(nonIsolatedJunctions)

    # V.) Add a cluster to the isolated junctions too (each will have their own, due to their isolation :'( ))

    max_ni_clust = nonIsolatedJunctions['neighbour_cluster'].max() 

    isolatedJunctions["neighbour_cluster"] = isolatedJunctions.index.map(lambda x: max_ni_clust + x)

    return nonIsolatedJunctions, isolatedJunctions



    




    