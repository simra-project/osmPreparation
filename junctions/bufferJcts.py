
import numpy as np

from statistics import mean

from geopandas import GeoSeries

from shapely.geometry import Point

from shapely.ops import transform

import pyproj

#*******************************************************************************************************************
# (0) Define some functions the actual buffer-function requires.

def hwBuffer (roadType) :
         switcher = {
                 'motorway': 9*2,
                 'trunk': 8*2,
                 'primary': 7.5*2,
                 'secondary' : 6*1.35,
                 'tertiary' : 5.5*1.35,
                 'unclassified': 4.5*1.35,
                 'residential' : 6*1.35,
                 'motorway_link': 7.5*2,
                 'trunk_link': 7.5*2,
                 'primary_link': 7.5*2,
                 'secondary_link': 6.5*1.35,
                 'tertiary_link': 5.5*1.35,
                 'living_street': 6.5*1.35,
                 'service': 5.5*1.35,
                 'pedestrian': 6.5*1.35,
                 'track': 2.5*1.35,
                 'bus_guideway': 5.5*1.35,
                 'escape': 5.5*1.35,
                 'raceway': 6.5*1.35,
                 'road': 6.5*1.35,
                 'footway': 2.5*1.35,
                 'bridleway': 2.5*1.35,
                 'steps': 2.5*1.35,
                 'path': 2.5*1.35,
                 'cycleway': 1.5*1.35
             }
         return switcher.get(roadType, 6.5)       

def getAvgWidth(highwaytypes):
    
    hwWidths = np.vectorize(hwBuffer)(highwaytypes)
    
    return np.mean(hwWidths,axis=0)

# ********************************************************************************************************************
# (1) Let the buffer magic happen!!!!

# In Python, loops are slow because many things happen at run time - if we use loops that operate element-wise,
# type-checking (and presumably other things) are done for every element => sloooooow!
# 
# If we apply function to whole data frame columns (= pd.Series) or, even better, numpy arrays, checks are only done
# once for every Series/array => faaaaaast!

def bufferize(junctionsdf, bufferSize):

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Define our transformers for projecting between coordinate systems
    # NOTE:
    # Projecting GeoSeries with GeoPandas native methods yielded distorted polygons.
    # 
    # Mapping with pyproj projections was super slow initially - until the cool modified version below came around!! Trick: these functions only create one transformer (singleton?) rather than a new one for every projection (at least that's my understanding ;) ) - i.e. they're faaaaaast
    # 
    # [GIS Stackexchange to the rescue! - See post at the very bottom, which saved the day.](https://gis.stackexchange.com/questions/127427/transforming-shapely-polygon-and-multipolygon-objects)

    projectToMeters = pyproj.Transformer.from_proj(
        pyproj.Proj('epsg:4326'), # destination coordinate system
        pyproj.Proj('epsg:3035')) # source coordinate system

    projectToLatLon = pyproj.Transformer.from_proj(
        pyproj.Proj('epsg:3035'), # destination coordinate system
        pyproj.Proj('epsg:4326')) # source coordinate system

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    lats = junctionsdf.lat.values
    lons = junctionsdf.lon.values

    points = GeoSeries(map(Point, list(zip(lats, lons))))

    # Project with pyproj transformer rather than GeoSeries methods.

    points_proj = points.map(lambda p: transform(projectToMeters.transform, p))

    highwaytypes = junctionsdf.highwaytypes.values

    highwaywidths = np.vectorize(getAvgWidth)(highwaytypes)

    # BUFFERSIZES:
    # - Berlin: highwaywidths*3.5
    # - Bern (more narrow city layout): highwaywidths*2
    # - other regions - tbd

    bufferedPoints = points_proj.buffer(highwaywidths*bufferSize, cap_style=1)

    simplified_points = bufferedPoints.simplify(7, preserve_topology=False)

    # Project with pyproj transformer rather than GeoSeries methods.

    reprojected_points = simplified_points.map(lambda p: transform(projectToLatLon.transform, p))

    junctionsdf.loc[:, 'poly_geometry'] = reprojected_points

    polyLats = reprojected_points.map(lambda x: x.exterior.coords.xy).map(lambda x: x[0])

    polyLons = reprojected_points.map(lambda x: x.exterior.coords.xy).map(lambda x: x[1])

    junctionsdf.loc[:, 'poly_vertices_lats'], junctionsdf.loc[:, 'poly_vertices_lons'] = polyLats, polyLons

    return junctionsdf



