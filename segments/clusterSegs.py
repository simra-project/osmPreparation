
from itertools import starmap

from geopandas import GeoSeries

from shapely.geometry import Point

import utils

#*******************************************************************************************************************
# (1) Find out which ways don't start and/or end with a junction. Wherever that is the case, we want to 
#     merge segments together in order to get rid of weird breaks - goal is to obtain a clean model of
#     street segments starting and ending at junctions.
#
#     Let an **ODDBALL** be a way that doesn't end or start with a junction (or neither).
#     
#     BELOW SOME CONSIDERATIONS THAT ARE RELEVANT WHEN ALL KINDS OF HIGHWAY TYPES ARE CONSIDERED:
#
#     TBD: we don't want small ways to weirdly be merged together  - e.g., pathways in a park 
#     would be at risk of becoming a weird giant cobweb. 
#     ***Q***: Why could this happen in the first place? - 
#     ***A***: because on our terms, a junction is a junction only if at least two of the highways associated with it are of a larger type.
#
#     Approaches so far:
#     1. allow a segment to become an oddball only if its type is contained in our list of relevantTypes --> nope, this didn't deliver
#     2. incorporate the 'phantom junctions' into oddball definition - those are intersections of more than two ways with less than 
#        two of those being of a relevantType. Hasn't worked out so far.

def oddballWrapper (segmentsdf, jctsdf):

    # these are ALL junctions (i.e., intersections of at least two highways, irrespective of their type)

    jctids = jctsdf['id'].values 

    # now we also need the LARGER junctions (i.e., intersections of at least two highways of a larger type)

    larger_jcts = jctsdf[jctsdf['junction'] == 'large_junction']

    larger_jctids = larger_jcts['id'].values 

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def findOddballs(highwaytype, nodes):

        lastNodeIdx = len(nodes) - 1

        if highwaytype in ['unclassified', 'pedestrian', 'cycleway']:

            if not(nodes[0] in jctids):
            
                return True
        
            elif not(nodes[lastNodeIdx] in jctids):
        
                return True
            
            else:
            
                return False

        else:
            
            if not(nodes[0] in larger_jctids):
                
                return True
            
            elif not(nodes[lastNodeIdx] in larger_jctids):
            
                return True
                
            else:
                
                return False

    # Determine oddballs in segments df

    segmentsdf.loc[:,'oddball'] = [x for x in starmap(findOddballs, list(zip(segmentsdf.loc[:,'highwaytype'], segmentsdf.loc[:,'segment_nodes_ids'])))]

    # split the df into two new dfs according to oddball property

    unfoldedOddballs = segmentsdf[segmentsdf['oddball'] == True].copy()
    unfoldedNormies = segmentsdf[segmentsdf['oddball'] == False].copy()

    unfoldedOddballs.reset_index(inplace=True)
    unfoldedOddballs = unfoldedOddballs.drop('index', axis=1)
    unfoldedNormies.reset_index(inplace=True)

    unfoldedOddballs = unfoldedOddballs.fillna(u'unknown').reset_index(drop=True)
    unfoldedNormies = unfoldedNormies.fillna(u'unknown').reset_index(drop=True)

    return unfoldedOddballs, unfoldedNormies

#*******************************************************************************************************************
# (2) Cluster & merge oddball segments: We want to merge oddball segments at those ends where they overlap without a 
#     junction being contained in the intersection. To do so, firstly assign its neighbours to each oddball segment. 
#     A neighbouring segment is a segment whose polygon a segments' polygon intersects with (again, without a junction 
#     being contained in that intersection).

def findNeighbours(unfoldedOddballs, sortingParams, junctionsdf, neighbourParam):

    # Sort according to upper left corner; sort by lon (minx) resp lat (maxy) first depending on the bounding box's shape. 

    unfoldedOddballs['minx'] = unfoldedOddballs['poly_geometry'].map(lambda p: p.bounds[0])

    unfoldedOddballs['maxy'] = unfoldedOddballs['poly_geometry'].map(lambda p: p.bounds[3])

    unfoldedOddballs.sort_values(by=sortingParams, inplace=True)

    unfoldedOddballs.reset_index(inplace=True)
    unfoldedOddballs = unfoldedOddballs.drop('index',axis=1)
    unfoldedOddballs.reset_index(inplace=True)

    junctionlats = junctionsdf.lat.values
    junctionlons = junctionsdf.lon.values
    junctionpoints = GeoSeries(map(Point, zip(junctionlats, junctionlons)))

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Define some inner functions we'll need for determining the segments' neighbours.

    ## a) isIntersectionValid: as a neighbouring segment is defined as a segment whose polygon a segments' polygon 
    ##                         intersects with WITHOUT a junction being contained in that intersection, this function
    ##                         checks for junctions in intersections.

    def isIntersectionValid(polyOne, outerInd, polyTwo, innerInd):

        if polyOne == polyTwo:
            
            return False
        
        intersection = polyOne.intersection(polyTwo)

        junctions_in_intersection = junctionpoints[lambda x: x.within(intersection)]
        
        if junctions_in_intersection.empty:
                                
            if not isMotorwayLanesIntersecting(outerInd, innerInd):

                return True
                                
        else:
    
            if isMotorwayLanesIntersecting(outerInd, innerInd):

                 print("Not merging highwaylanes traveling in opposite directions")

            else:

                print(f"Not merging because of junctions in segment overlap: {junctions_in_intersection}")

            return False

    def isMotorwayLanesIntersecting(outerInd, innerInd):

        # With this function, we want to make sure that separate, but parallel fractions of streets with traffic
        # going in the opposite direction (usually we're talking motorways here) are not merged. 
        # IDEA: motorways with separate parallel sections traveling in opposite directions will like
        #       (hopefully) exhibit the 'destination' feature (e.g. 'Dresden', 'Hamburg', 'Charlottenburg-Wilmersdorf', ...). 

        outerHighwayName = unfoldedOddballs.at[outerInd, 'highwayname']

        innerHighwayName = unfoldedOddballs.at[innerInd, 'highwayname']  

        outerHighwayDestination = unfoldedOddballs.at[outerInd, 'destination']

        innerHighwayDestination = unfoldedOddballs.at[innerInd, 'destination']  

        if (innerHighwayName == outerHighwayName) and (innerHighwayDestination != outerHighwayDestination):

            return True

        else:

            return False

    ## b) getNeighbours: unsurprisingly, this function assigns each segment its neighbours (definition of 'neighbour'
    ##                   in this context: see above)

    def getNeighbours(outerInd, outerPoly, outerHighway):
        
        neighbours = []
        
        lower = max(outerInd-neighbourParam, 0)
        
        upper = min(outerInd+neighbourParam, len(unfoldedOddballs)-1)
        
        # Use buffer trick if polygon is invalid
        # https://stackoverflow.com/questions/13062334/polygon-intersection-error-in-shapely-shapely-geos-topologicalerror-the-opera
        
        if not(outerPoly.is_valid):
            
            outerPoly = outerPoly.buffer(0)
        
        for i in range(lower, upper):
        
            innerID = unfoldedOddballs.at[i,'id']
            
            innerPoly = unfoldedOddballs.at[i,'poly_geometry']
            
            # Use buffer trick if polygon is invalid
            
            if not(innerPoly.is_valid):
            
                innerPoly = innerPoly.buffer(0)
            
            innerHighway = unfoldedOddballs.at[i,'highwayname']
                        
            if outerPoly.intersects(innerPoly): 
                    
                validIntersection = isIntersectionValid(outerPoly, outerInd, innerPoly, i)
                        
                if validIntersection and (outerHighway == innerHighway):
                        
                    neighbours.append(innerID)
                        
        return neighbours

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    unfoldedOddballs['neighbours'] = [x for x in starmap(getNeighbours, list(zip(unfoldedOddballs['index'],unfoldedOddballs['poly_geometry'],unfoldedOddballs['highwayname'])))]

    return unfoldedOddballs

#*******************************************************************************************************************
# (3) Find neighbour clusters (neighbours of neighbours of neighbours ...)

def clusterNeighbours(df, neighbourParam):
    
    clusterInd = 0
    
    # Store the indices of rows we've already assigned a cluster to.
    
    included = []
    
    for ind in df.index:
        
        currNeighbours = []
        
        # Do not look at rows we've already assigned clusters to 
        # (at least not in this - the outer - loop. Why?
        # because a cluster detected in the inner loop is complete.)
        
        if ind in included:

            continue

        else:
            
            # Assign the current cluster index to the row.
        
            df.at[ind, 'neighbour_cluster'] = clusterInd
            
            # Add the current row's index to the list of rows that were already visited.
            
            included.append(ind)
            
            # Initialize list of neighbours in cluster with this row's neighbours.
            # NOTE: 'extend' adds a list to another list while avoiding creating a 
            #       list of lists. 'Append' adds a single element to a list.
        
            currNeighbours.extend(df.at[ind,'neighbours'])
            
            # Add the row's index to the neighbour list too.
            
            currNeighbours.append(df.at[ind,'id'])
        
            # Now iterate through the df again to find the neighbours' neighbours.

            included = expandNeighbours(df, neighbourParam, clusterInd, ind, currNeighbours, included)
                    
            # No more extended neighbours, up the cluster numbers
        
            clusterInd += 1

    return df

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

#*******************************************************************************************************************
# (X) Call all the functions required for clustering in logical order.

# def cluster (segmentsdf, junctionsdf, neighbourParam, sortingParams):

def cluster (region, segmentsdf, junctionsdf):

    # 0.) Retrieve parameters from param dictionary

    sorting_params = utils.paramDict[region]["sorting_params"]

    neighbour_param = utils.paramDict[region]["neighbour_param"]

     # I.) Determine which segments are 'oddballs' (don't start and/or end with a junction)

    oddballs, normies = oddballWrapper(segmentsdf, junctionsdf)

    # II.) Assign each oddball segment its neighbours (other segments it intersects with without a junction being contained
    #      in that intersection).

    oddballsWithNeighbours = findNeighbours(oddballs, sorting_params, junctionsdf, neighbour_param)

    # III.) Cluster the oddball segments based on their neighbours

    oddballsWithNeighbours_clustered = clusterNeighbours(oddballsWithNeighbours, neighbour_param)

    # IV.) Add a cluster to the isolated segments too (each will have their own, due to their isolation :'( ))

    max_ni_clust = oddballsWithNeighbours_clustered['neighbour_cluster'].max() 

    normies["neighbour_cluster"] = normies.index.map(lambda x: max_ni_clust + x)

    return oddballsWithNeighbours_clustered, normies