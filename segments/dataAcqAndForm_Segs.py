
import pandas as pd
import numpy as np

import requests
import config
import json
import utils

# ********************************************************************************************************************
    
tags = ['motorway','trunk','primary','secondary','secondary_link','tertiary','tertiary_link','living_street','residential', 'unclassified', 'pedestrian', 'cycleway', 'path', 'track']
# tags = ['motorway','trunk','primary','secondary','secondary_link','tertiary','tertiary_link','living_street','residential', 'unclassified', 'pedestrian', 'cycleway', 'path', 'track']
# tags = ['trunk','primary','secondary','secondary_link','tertiary','tertiary_link','living_street','residential', 'unclassified', 'pedestrian', 'cycleway', 'path', 'track']

# (1) Get data from OSM, input param = bounding box

def getFromOverpass(bbox, ways, nodes):

    ##############################################################################################################
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

    compactOverpassQLstring = '[out:json][timeout:3600];('
    for tag in tags:
        for obj in objects:
            compactOverpassQLstring += '%s["highway"="%s"](%s,%s,%s,%s);' % (obj, tag, minLat, minLon, maxLat, maxLon)
#    compactOverpassQLstring += 'way[bicycle=yes](%s,%s,%s,%s);' % (minLat, minLon, maxLat, maxLon)
#    compactOverpassQLstring += 'way[bicycle=designated](%s,%s,%s,%s);' % (minLat, minLon, maxLat, maxLon)
    compactOverpassQLstring += ');out body;>;out skel qt;'

    osmrequest = {'data': compactOverpassQLstring}

    # osmurl = 'http://overpass-api.de/api/interpreter'

    osmurl = 'http://vm3.mcc.tu-berlin.de:8088/api/interpreter'
    # print(osmrequest)

    osm = requests.get(osmurl, params=osmrequest)

    print("Completed request to overpass, status was {0!s}".format(osm.status_code))

    ##############################################################################################################
    # c)  Reformat the JSON to fit in a Pandas Dataframe

    osmdata = osm.json()
    osmdata = osmdata['elements']

    for dct in osmdata:
        if dct['type']=='way':
            for key, val in dct['tags'].items():
                dct[key] = val
            del dct['tags']
            if dct not in ways:
                ways.append(dct)
        else:
            if dct not in nodes:
                nodes.append(dct)

    return ways, nodes # resp osmdata

# ********************************************************************************************************************
# (2) Construct a df containing highways (streets, way objects) from the raw osmdata

# def getHighwayDf(osmdata):

def getHighwayDf(ways):

    # osmdf = pd.DataFrame(osmdata)

    highwaydf = pd.DataFrame(ways)[['highway','id','ref','lanes','lanes:backward','name','nodes']]

    # 'id', 'highway', 'lanes', 'lanes:backward', 'name', 'maxspeed', 'nodes', 'ref'

    # Zu kleine Straßen raus werfen:

    highwaydf = highwaydf[highwaydf['highway'].isin(tags)]

    # Replace `NaN` with word `unknown` and reset the index:

    highwaydf = highwaydf.fillna(u'unknown').reset_index(drop=True)

    # split the df into two new dfs according to highwayname == 'unknown'

    highways_no_names = highwaydf[highwaydf['name'] == 'unknown'].copy()
    highways_with_names = highwaydf[highwaydf['name'] != 'unknown'].copy()

    # for rows with missing names, replace 'name' with str('ref')
    highways_with_names = highways_with_names.drop('ref', axis=1)
    highways_no_names = highways_no_names.drop('name', axis=1)
    highways_no_names['ref'] = highways_no_names['ref'].map(lambda r: str(r))
    highways_no_names.rename(columns = {'ref':'name'}, inplace = True)

    highwaydf = pd.concat([highways_with_names, highways_no_names], ignore_index = True, sort = False)

    # Map ids to list to facilitate cluster comparison in manualClusterPrep
    # COMMENT OUT TO PREVENT THIS

    highwaydf['id'] = highwaydf['id'].map(lambda i: [i])

    # *********************************************************************
    
    return highwaydf

# ********************************************************************************************************************
# (3) Construct a df containing nodes from the raw osmdata - this project is concerned with highways rather than
#     nodes, but we need the node data to enrich our highwaydf with information that is only contained in node objects
#     (specifically, highways in OSM consist in lists of nodes, which are represented as ids. Only the node objects
#     themselves contain the geospatial coordinates corresponding to node ids. Hence we need a nodesdf in order to 
#     map the highways' lists of node ids onto the node coordinates).
#     -
#     Return a dictionary structure containing node ids as keys and their coords as values for easy lookup.

def getCoordsFromNodes(nodes):
        
    nodesdf = pd.DataFrame(nodes)

    idCoords_dict = pd.Series(list(zip(nodesdf.lat.values,nodesdf.lon.values)),index=nodesdf.id).to_dict()

    return idCoords_dict

# ********************************************************************************************************************
# (0) Call all the functions in this script in logical order.

def metaFunc(bbox, region):

    ways, nodes = [[], []]
    if region == "Ruhrgebiet":
        ruhrgebiet_dict = {k: v for k, v in config.paramDict.items() if (k.startswith('Ruhrgebiet') and len(k) == 12)}
        for key, value in ruhrgebiet_dict.items():
            print("segs getFromOverpass for: " + key)
            ways, nodes = getFromOverpass(value["bounding_box"], ways, nodes)
    else:
        ways, nodes = getFromOverpass(bbox, ways, nodes)

    highwaydf = getHighwayDf(ways)

    idCoords_dict = getCoordsFromNodes(nodes)
    
    return highwaydf, idCoords_dict