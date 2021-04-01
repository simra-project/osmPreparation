
import pandas as pd
import numpy as np
from geopy import distance
from itertools import starmap

relevantTypes = ['primary','secondary','secondary_link','tertiary','tertiary_link','living_street','residential']

# ********************************************************************************************************************
# (1) Determine way segments.
#     -
#     Way objects in OSM are (potentially very long) lists of nodes, what we are interested in tho are 
#     segments of ways (representing a fraction of a highway that starts and ends with a junction node, containing
#     no junction nodes beyond these two). We're using the junctionsdf generated by the sibling project to segmentize
#     our ways.

def segmentingWrapper(highwaydf, junctionsdf):

    # these are ALL junctions (i.e., intersections of at least two highways, irrespective of their type)

    jctids = junctionsdf['id'].values 

    # now we also need the LARGER junctions (i.e., intersections of at least two highways of a larger type)

    larger_jcts = junctionsdf[junctionsdf['junction'] == 'large_junction']

    larger_jctids = larger_jcts['id'].values 

    # Helper fct for determining if a node is a junction 

    def isJct(node, highwaytype):

        if (highwaytype in relevantTypes) and (node in larger_jctids):

            return True

        elif (node in jctids):

            return True

        else:

            return False

    ########################################################################################################

    def getSegments(wayNodes, highwaytype):
        
        currSeg = []
        
        segments = []
        
        for n, node in enumerate(wayNodes):
            
            if n == (len(wayNodes) - 1):
                
                currSeg.append(node)
                
                segments.append(currSeg)
                
                return pd.Series(segments)
        
            elif (isJct(node,highwaytype)):
                
                if (n > 0):
                
                    currSeg.append(node)
            
                    segments.append(currSeg)
            
                currSeg = [node]
            
            else:
            
                currSeg.append(node)

    highwaydf.loc[:,'segments'] = [x for x in starmap(getSegments, list(zip(highwaydf.loc[:,'nodes'], highwaydf.loc[:,'highway'])))]

    return highwaydf

# ********************************************************************************************************************
# (2) Unfold the segmentized way data frame.
#     -
#    Each highway now has the property 'segments', a list of lists. Let's unfold/explode this so we obtain one row per segment.

def unfold(highwaydf):

    # Zuper cool numpy solution from https://stackoverflow.com/questions/53218931/how-to-unnest-explode-a-column-in-a-pandas-dataframe
    # OMG it's so fast!!

    vals = highwaydf.segments.values.tolist()
    rs = [len(r) for r in vals]  

    name = np.repeat(highwaydf.name, rs)
    highway = np.repeat(highwaydf.highway, rs)
    lanes = np.repeat(highwaydf.lanes, rs)
    lanesBw = np.repeat(highwaydf['lanes:backward'], rs)
    destinations = np.repeat(highwaydf.destination, rs)

    unfoldeddf = pd.DataFrame(np.column_stack((name, highway, lanes, lanesBw, destinations, np.concatenate(vals))), 
                                columns=['highwayname','highwaytype','highwaylanes','lanes:backward','destination','segment_nodes_ids'])
  
    '''
    * Manual remerging of segments shall be enabled via a CLI (> manualMergeCLIFlow_segs.py).
    * Manual remerging is done by computing clustering solutions for two different buffer sizes and determining 
      the differences between these solutions; segment clusters are compared based on strings containing the sorted 
      ids of the individual segments contained in them.
    * Segments are fractions of OSM ways; therefore, they inherit a range of properties from their 'parent' highways. 
      'id' is one of them. Hence, values in the 'id'-column aren't unique. 
    * It is nicer though to keep them unique, otherwise different clustering solutions cannot be compared. The easiest
      strategy for obtaining a unique id is to just use the index. 
    * QUICK RECAP OF THE CLUSTER COMPARISON PROCESS (because it can't be repeated often enough!):
        (1) map ids to lists; 
        (2) if two segments end up in the same cluster and hence ar geographically merged and property-wise aggregated, 
            their ids are concatenated; 
        (3) in the end, those id lists are sorted (to ensure identical clusters are recognized as such when represented
            as strings) and converted to string (so they can be put into sets, i.e. hashed); 
        (4) then, two data sets that are based on clustering solutions obtained with different values for buffer size can 
            be compared using their respective sets of segment clusters, with each segment cluster (irrespective of its 
            containing a single or multiple segment/s) represented by a string of id/s.  
    '''

    unfoldeddf['id'] = unfoldeddf.index.map(lambda x: [x])

    return unfoldeddf
    
# ********************************************************************************************************************
# (3) Map the segments' lists of node ids onto nodes' respective coordinates.
#     -
#     (highways in OSM consist in lists of nodes, which are represented as ids. Only the node objects
#     themselves contain the geospatial coordinates corresponding to node ids. Hence we need a nodesdf in order to 
#     map the highways' lists of node ids onto the node coordinates).

def coordMappingWrapper(unfoldeddf, nodecoords):

    def mapToCoords (nodeList) :
    
        coords = list(map(nodecoords.get, nodeList))
        
        lats, lons = zip(*coords)
            
        return lats, lons

    unfoldeddf.loc[:,'coords'] = unfoldeddf.loc[:,'segment_nodes_ids'].map(mapToCoords)

    lats = unfoldeddf.loc[:,'coords'].map(lambda x: (list(x[0])))
    lons = unfoldeddf.loc[:,'coords'].map(lambda x: (list(x[1])))

    unfoldeddf.loc[:,'lats'], unfoldeddf.loc[:,'lons'] = lats, lons

    return unfoldeddf

# ********************************************************************************************************************
# (4) Assign each segment its length.

def distAssignmentWrapper(unfoldeddf):

    def getDist(coords):
    
        lastIdx = len(coords) - 1
        
        first = (coords[0][0], coords[1][0])
        
        last = (coords[0][lastIdx], coords[1][lastIdx])
        
        return distance.distance(last,first).km * 1000

    unfoldeddf.loc[:,'seg_length'] = unfoldeddf.loc[:,'coords'].map(getDist)

    return unfoldeddf

# ********************************************************************************************************************
# (0) Call all the functions in this script in logical order.

def metaFunc(highwaydf, junctionsdf, nodecoords):

    segmentedDf = segmentingWrapper(highwaydf, junctionsdf)

    unfoldeddf = unfold(segmentedDf)

    unfoldeddf_nodeCoords = coordMappingWrapper(unfoldeddf, nodecoords)

    unfoldeddf_segLength = distAssignmentWrapper(unfoldeddf_nodeCoords)

    return unfoldeddf_segLength