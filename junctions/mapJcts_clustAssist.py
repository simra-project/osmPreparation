
import folium

import geopandas as gpd

from shapely.ops import cascaded_union

from shapely.geometry.multipolygon import MultiPolygon

from shapely.geometry.polygon import Polygon

from statistics import mean

import paramsPerRegion # internal import

#*******************************************************************************************************************
# (*) Plot polygons onto map.

# This variant follows the following approach to plotting MultiPolygons:
# extract individual Polygons from MultiPolygons and plot these. 

def extractAndPlot (extractable_shape, neighbour_cluster, mmaapp, style, crs):

    if isinstance(extractable_shape, Polygon):
        
        lats, lons = extractable_shape.exterior.coords.xy
            
        poly_swapped = Polygon(zip(lons, lats))
            
        poly_geoDf = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[poly_swapped])
        
        folium.GeoJson(poly_geoDf, style_function=lambda x: style).add_to(mmaapp)

        lat, lon = extractable_shape.centroid.x, extractable_shape.centroid.y

        # folium.Marker([lat, lon], popup=f'<i>Neighbour-Cluster: {neighbour_cluster}</i>').add_to(mmaapp)

        folium.Marker([lat, lon], popup=f'<i>Neighbour Cluster: {neighbour_cluster}</i>').add_to(mmaapp)
            
    elif isinstance(extractable_shape, MultiPolygon):
            
        individual_polys = list(extractable_shape)
            
        for poly in individual_polys:
        
            extractAndPlot(poly, neighbour_cluster, mmaapp, style, crs)

def plotPolys (df, geomCol, map, style):

    crs = "EPSG:4326" # CRS = coordinate reference system, epsg:4326 = Europa im Lat/Lon Format
    
    for ind in df.index:

        # To add: 
        # * neighbour_cluster (to display in popup), 
        # * polygon centroid (for positioning marker),
        # * 'clust_inconsist' for highlighting junctions that have ended up in inconsistent clusters depending on 
        #   buffer size.

        if df.at[ind,'clust_inconsist'] > 0: 

            extractAndPlot(df.at[ind, geomCol], df.at[ind, 'neighbour_cluster'], map, {'fillColor': '#FFD700', 'lineColor': '#8c0d26'}, crs)

        else:

            extractAndPlot(df.at[ind, geomCol], df.at[ind, 'neighbour_cluster'], map, style, crs)

#*******************************************************************************************************************
# (*) Execute all the map jobs in logical order.

def runAllMapTasks (region, nonIsolatedJunctions, isolatedJunctions, bufferSize):

    bbCentroid = paramsPerRegion.paramDict[region]['centroid']

    neighbourParam = paramsPerRegion.paramDict[region]['neighbour_param']

    # I.) Set up our maps

    bbCentroid = paramsPerRegion.paramDict[region]['centroid']

    myMap = folium.Map(location=bbCentroid, zoom_start=15, tiles='cartodbpositron')

    # II.) Plot polys onto their respective maps

    plotPolys (nonIsolatedJunctions, 'geometry', myMap, {'fillColor': '#ff1493', 'lineColor': '#FF6347'})

    plotPolys (isolatedJunctions, 'poly_geometry', myMap, {'fillColor': '#7FFF00', 'lineColor': '#F5FFFA'})

    # III.) Export map as htmls

    myMap.save(f'{region}-jcts-map_buf={bufferSize}_np={neighbourParam}.html')
