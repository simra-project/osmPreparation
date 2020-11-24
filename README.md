
# SimRa Analysis Pipeline

## Introduction

TU Berlin's Mobile Cloud Computing Group have launched their  [SimRa project](https://www.digital-future.berlin/en/research/projects/simra/ "SimRa Project Site") in 2018. Its aim is to collect data on near-accidents and hazardous situations in bicycle traffic in Berlin and other metropolitan areas via a smartphone app (available for Android and iOS).

The project's *Analysis Pipeline* enables the mapping of incident data to junctions and segments (sections of roads between two junctions). This mapping allows for the aggregation of incident data per location and hence facilitates the identification of particularly dangerous spots and areas.

What the current project mainly does is
1. obtain the desired geographical information (junctions, segments) from the raw Open Street Maps data (neither of these types are explicitly contained in the raw data), 
1. transform the one-dimensional raw OSM data to polygons (Open Street Maps follows a graph theory data model, i.e. there are nodes and edges, with the edges being collections of nodes). 

## Installation/Set-Up

Python version: 3.8.3 64-bit

**Recommended**: this project was built using [pipenv](https://pipenv-fork.readthedocs.io/en/latest/basics.html "Pipenv documentation"). Install pipenv on your machine, navigate to the project directory and run `pipenv install` to activate the environment (pipenv gets all the information it needs from the `Pipfile`). That's it! (For a crash course on pipenv, please refer to [this tutorial](https://www.youtube.com/watch?v=6Qmnh5C4Pmo "Pipenv Crash Course by Traversy Media")).

**Alternatively**: if you don't want to use pipenv for whatever reason you might have to avoid this amazing package, a `requirements.txt` file is provided as well. You can run `pip install -r 'requirements.txt'` inside the project folder to install all of the required packages.

## Getting junction data

The project is logically separated into scripts dealing with junction data and scripts concerned with segment data. It is crucial that the junction unit is run first as it generates a data set the segments unit requires (this way redundant computations are avoided). 

The junction unit comprises the following scripts:
* `OSM_jcts.py`: this is the main script in this logical unit. Parameters characterizing a specific geographical region are handed to the main function. These are:
    * a string specifying the name of the **region**; required for writing files.
    * a **bounding box** describing the region in `[minLon,minLat,maxLon,maxLat]` format. Required for querying the raw Open Street Maps data from the Overpass API.
    * a **bounding box centroid** in `[lat,lon]` format. This is required for mapping. 
    * a so-called ***neighbourParam***: individual junctions are clustered and merged wherever appropriate. Imagine a large junction: it is actually comprised of many smaller junctions. To represent this concept in the data, junctions are clustered. For the purpose of clustering junctions, we first sort them by location. After sorting, it is obviously not economical to compare every junction to every other junction in the data frame to determine if they're neighbours. Instead, we're only looking at the x rows above and below each junction. However, this x will be different for different regions (as the data frames are of different sizes).
    * **bufferSize**: junctions are buffered into two-dimensional shapes according to the mean width of the highways intersecting at this junction multiplied with a factor. This factor varies depending on the city layout. 
    * **sortingParams**: either `['lat','lon']` or `['lon','lat']`; that's because we're sorting the junctions by location to make some operations more efficient and it is more sensible to sort by lat resp. lon first depending on the shape of the bounding box (long but slim bounding box: sort by lat first; wide but low bb: sort by lon first) 
* `dataAcqAndForm_Jcts.py`: the purpose of this script is to first query the geographical data for the region defined by the bounding box provided from the Open Street Maps server via the Overpass API; then generate a pandas data frame containing node data and another one containing highway data (nodes, i.e. individual lat/lon pairs, and highways, i.e. collections of nodes, are the only two data types present in the raw OSM data); and add some additional properties to the data.
* `findJunctions.py`: unsurprisingly, this script determines which nodes contained in the raw OSM data can be regarded junctions, and delivers a data frame containing those (it not only hands this data frame over to the main function for subsequent processing, but also writes a csv file containing the junction ids, latitudes and longitudes, which will later be used by the segments unit of the project).
* `bufferJcts.py`: this script creates two-dimensional shapes from the one-dimensional raw data. The resulting polygons as well as their vertices (lists of lats/lons) are stored in the data frame.
* `clusterJcts.py`: as outlined above, junctions are clustered to represent larger junctions consisting of multiple smaller junctions. This is currently accomplished by looking at the overlap of polygons corresponding to junctions; however, manual corrections are planned in the near future.
* `tidyData_Jcts.py`: in this script, junctions whose polygons overlap are merged and the final data frame is stored in memory.
* `mapJcts.py`: this script is used to generate a `.html` map displaying the geometric shapes created. If such a map is not required, the call to the script made by the `tidyData_Jcts.py` script can be commented out.

The main output of the junctions unit is a `{region}_junctions_complete.csv` file (e.g., `berlin_junctions_complete.csv`).

## Getting segment data

This logical unit of scripts mostly performs computations analogous to the junction unit described above, only for street segments rather than junction nodes. Hence, only where the segments unit deviates from what the junction unit does additional explanations will be provided.

* `OSM_segs.py`: 
    * the segment unit's main script's main function (double genitive, excuse the lack of elegance here) currently accepts one parameter less than its junctions equivalent; that is because it has (so far) not appeared necessary to vary the **bufferSize** depending on the respective geographical region. 
    * furthermore, code for performing computations for multiple regions concurrently is not provided atm; however, if required it can easily be copied from `OSM_jcts.py` (omitting the **bufferSize** for each region).
* `segmentizeAndEnrich.py`: this script reads the csv file generated in `findJunctions.py` from memory. The file contains the ids, latitudes and longitudes of junction nodes. This information is used to break highways into segments at junctions. 

The main output of the segments unit is a `{region}_segments_complete.csv` file (e.g., `berlin_segments_complete.csv`).