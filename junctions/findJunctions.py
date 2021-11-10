
from itertools import starmap

from collections import Counter

relevantTypes = ['primary','secondary','secondary_link','tertiary','tertiary_link','living_street','residential']

# ********************************************************************************************************************
# (*) Find out which nodes in the nodesdf are junctions.

# Helper function for determining if there are at least 2 occurrences of tiny road types in a given list of highwaytypes.

def tinyRoadAlert(highwaytypes):

    tinytypes = [x for x in highwaytypes if x in ['path','track','footway','unclassified', 'pedestrian', 'cycleway']]

    count = Counter(tinytypes)

    # return any(v >= 2 for v in count.values())

    return (sum(count.values()) / len(highwaytypes)) >= 0.5

def identifyjunction(highwayIDs, highwaytypes, highwaynames):
    
    # The node belongs to less than 2 highways and therefore definitely is not a junction;
    # exit
    
    if len(list(set(highwayIDs))) < 2:
        
        return 'no_junction'
    
    else:
           
    # We got more than 2 highways for this junction; put highwaytypes & highwaynames
    # into a nested dict (Python equivalent to a Map) with highwayids as keys
    # Structure of dict vals: tuple of the form (highwaytype, highwayname)
        
        highwayDict = dict(zip(highwayIDs, zip(highwaytypes, highwaynames)))
        
        # Extract highwaynames and types from dict

        hwNames = list((v[1] for v in highwayDict.values()))

        hwTypes = list((v[0] for v in highwayDict.values()))
        
    # Check for duplicated highwaynames by converting to set and then back to list.
        
        if len((list(set(hwNames)))) >= 2:

            if len([hwt for hwt in hwTypes if hwt in relevantTypes]) >= 2:
            
                return 'large_junction'

            else:
                
                return 'small_junction'

        # New: try to determine if we are dealing with tiny roads
        # That's because these often don't have names and hence the above criterion selecting based
        # on the presence of at least two distinct hwNames won't work

        elif tinyRoadAlert(hwTypes):

            return 'small_junction'
        
        else: 
            
            return 'no_junction'

# ********************************************************************************************************************
# (*) Call all the functions in this script in logical order.

def getJunctionsDf(nodesdf, region):

    nodesdf.loc[:,'junction'] = [x for x in starmap(identifyjunction, list(zip(nodesdf['highwayids'],nodesdf['highwaytypes'],nodesdf['highwaynames'])))]

    # jcts = ['small_junction','large_junction']

    junctionsdf = nodesdf[nodesdf['junction'] != 'no_junction']

    junctionsdf.reset_index(inplace=True)

    junctionsdf = junctionsdf.drop('index',axis=1)

    # Subset of the data set to be read by segments scripts

    junctions_for_segs = junctionsdf[['junction','id','lat','lon','highwaynames']]

    # Now we can get rid of the smaller junctions (only needed in the segments project so
    # it needs to be contained in the 'junctions_for_segs'-df)

    junctionsdf = junctionsdf[junctionsdf['junction'] == 'large_junction']

    junctionsdf.reset_index(inplace=True)

    junctionsdf = junctionsdf.drop(['index','junction'],axis=1)

    return junctionsdf, junctions_for_segs