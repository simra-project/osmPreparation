
import pandas as pd
import requests
import numpy as np

# ********************************************************************************************************************

tags = ['primary','secondary','secondary_link','tertiary','tertiary_link','living_street','residential']

# (1) Get data from OSM, input param = bounding box

def getFromOverpass(bbox):

    # a) Extract bb corners

    # Links unten
    minLat = bbox[1]
    minLon = bbox[0]

    # Rechts oben
    maxLat = bbox[3]
    maxLon = bbox[2]

    ##############################################################################################################
    # b) Construct the Overpass Query String: Request from [Overpass-Turbo](http://overpass-turbo.eu/)

    # 'unclassified', 'pedestrian', 'cycleway'
    objects = ['way'] # like way, node, relation

    compactOverpassQLstring = '[out:json][timeout:60];('
    for tag in tags:
        for obj in objects:
            compactOverpassQLstring += '%s["highway"="%s"](%s,%s,%s,%s);' % (obj, tag, minLat, minLon, maxLat, maxLon)
    compactOverpassQLstring += ');out body;>;out skel qt;'

    osmrequest = {'data': compactOverpassQLstring}

    #osmurl = 'http://overpass-api.de/api/interpreter'

    osmurl = 'http://vm3.mcc.tu-berlin.de:8088/api/interpreter'

    osm = requests.get(osmurl, params=osmrequest)

    ##############################################################################################################
    # c)  Reformat the JSON to fit in a Pandas Dataframe

    osmdata = osm.json()
    osmdata = osmdata['elements']

    for dct in osmdata:
        if dct['type']=='way':
            for key, val in dct['tags'].items():
                dct[key] = val
            del dct['tags']
        else:
            pass # nodes

    return osmdata

# ********************************************************************************************************************
# (2) Construct a df containing highways (streets, way objects) from the raw osmdata

def getHighwayDf(osmdata):

    columns = ['id', 'highway', 'lanes', 'lanes:backward', 'name', 'nodes']

    osmdf = pd.DataFrame(osmdata, columns = columns)

    highwaydf = osmdf.dropna(subset=['name','highway'], how='any')
    highwaydf.tail(5)

    # Zu kleine Straßen raus werfen:

    highwaydf = highwaydf[highwaydf['highway'].isin(tags)]

    # Replace `NaN` with word `unknown` and reset the index:

    highwaydf = highwaydf.fillna(u'unknown').reset_index(drop=True)
    
    return highwaydf

# ********************************************************************************************************************
# (3) Construct a df containing nodes (individual lat, lon pairs) from the raw osmdata

def getNodesDf(osmdata):

    nodes = []
    for dct in osmdata:
        #print dct
        if dct['type']=='way':
            pass
        elif dct['type']=='node':
            nodes.append(dct)
        else:
            pass

    nodecols = ['id','lat','lon']

    nodesdf = pd.DataFrame(nodes, columns = nodecols)

    return nodesdf

# ********************************************************************************************************************
# (4) We want to get information about the highways nodes belong to, e.g. street type and name, number of lanes etc.
#     This data is not stored for nodes in OSM. To obtain it, we need to map nodes onto highways they belong to. 
#     Highways (i.e., way objects in OSM) however only possess a reference to all the nodes they consist of in form of a list.
#     To map the highway properties onto individual nodes, we therefore need to 'explode' the highwaydf according to the node list
#     property. This can efficiently be achieved using numpy.

def getMoreNodeProps(highwaydf, nodesdf):

    vals = highwaydf.nodes.values.tolist()
    rs = [len(r) for r in vals]    
    ids = np.repeat(highwaydf.id, rs)
    name = np.repeat(highwaydf.name, rs)
    highway = np.repeat(highwaydf.highway, rs)
    lanes = np.repeat(highwaydf.lanes, rs)
    lanesBw = np.repeat(highwaydf['lanes:backward'], rs)

    explodedNodes = pd.DataFrame(np.column_stack((ids, name, highway, lanes, lanesBw, np.concatenate(vals))), columns=['highwayids','highwaynames','highwaytypes','highwaylanes','highwaylanesBw','id'])

    explodedNodes = explodedNodes.groupby('id', as_index = False).agg(list)

    nodesdf = nodesdf.merge(explodedNodes, on='id', how='left')

    nodesdf = nodesdf.fillna(u'unknown').reset_index(drop=True)

    return nodesdf

# ********************************************************************************************************************
# (0) Call all the functions in this script in logical order.

def metaFunc(bbox):

    osmdf = getFromOverpass(bbox)

    highwaydf = getHighwayDf(osmdf)

    nodesdf = getNodesDf(osmdf)

    enrichedNodesdf = getMoreNodeProps(highwaydf, nodesdf)
    
    return enrichedNodesdf



 