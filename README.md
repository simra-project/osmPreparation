
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
* `OSM_jcts.py`: this is the main script in this logical unit. Parameters characterizing a specific geographical region are handed to the main function (*region*, *buffer_size*)/retrieved from a dictionary contained in `paramsPerRegion.py` (*bounding_box*, *centroid*, *neighbourParam*, sortingParams). These are:
    * a string specifying the name of the **region**; required for writing files. 
    * a **bounding box** describing the region in `[minLon,minLat,maxLon,maxLat]` format. Required for querying the raw Open Street Maps data from the Overpass API.
    * a **centroid** in `[lat,lon]` format. This is required for mapping. 
    * a so-called ***neighbourParam***: individual junctions are clustered and merged wherever appropriate. Imagine a large junction: it is actually comprised of many smaller junctions. To represent this concept in the data, junctions are clustered. For the purpose of clustering junctions, we first sort them by location. After sorting, it is obviously not economical to compare every junction to every other junction in the data frame to determine if they're neighbours. Instead, we're only looking at the x rows above and below each junction. However, this x will be different for different regions (as the data frames are of different sizes).
    * **buffer_size**: junctions are buffered into two-dimensional shapes according to the mean width of the highways intersecting at this junction multiplied with a factor. This factor varies depending on the city layout. 
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

## Manually editing junction and/or segment clusters

Clearly, no one value for **buffer_size** will deliver optimal clustering results in all cases. Therefore, once a fairly good value for **buffer_size** has been determined manual editing can be performed to optimize the clustering result. Concretely, the clustering solutions will be compared for a more conservative and a more liberal buffer size. The logic here is that the conservative- and the liberal buffer will for many cases produce the same clustering solutions, but in some cases, the liberal buffer will have produced additional merges where the conservative buffer hasn't. Hence, the user will be able to look at the locations where these differences have occurred and decide whether the more conservative or more liberal solution should be accepted into the final data frame.

For junctions and segments each, there now exist scripts that guide the user through the process of manual cluster editing: `manualMergeCLIFlow_jcts.py` and `manualMergeCLIFlow_segs.py`. These are designed to enable a user-friendly step-by-step process, making it possible to use the functionality without having to dig into the code first. The actual logic is contained in the scripts `manualMergePrep_jcts.py`/`manualMergePrep_segs.py`, `manualMergeTool_jcts.py`, `manualMergeTool_segs.py`, and `mapJcts_clustAssist.py`/`mapSegs_clustAssist.py`. 

* Firstly, the user is prompted to provided the **region** to work with as a lowercase string (e.g., 'berlin'). 
* Then, the default values for a rather conservative and rather liberal buffer are presented, so the user can either accept them or provide custom values. When providing custom values, ensure that they aren't too far apart (a difference of 0.25 is usually ideal) - the further apart they are, the more choices between conservative and liberal solutions will have to be performed. 
* Thereafter, the complete data for both buffer sizes is either retrieved from memory (if available) or computed and a comparison is carried out: where do the two data sets differ regarding the clustering solutions that were produced? - A HTML map displaying the differences is generated, and the user is informed of its location in the project directory.
* The user is then asked if she wants to perform any modifications. It is important to know that per default, all of the conservative clustering solutions (on the map: green shapes) will be accepted; i.e., editing is only necessary of there are any conservative clusters that shall be DELETED or REPLACED by there more liberal counterparts (on the map: blue shapes). If NO is selected, a data frame consisting of the entire conservative clustering solution (including both rows with clusters that are the same in the more liberal data set and rows that differ from the more liberal data set) is written to csv.
* If the user does want to perform any editing, she is prompted to decide between replacement and deletion (of conservative clusters = green shapes on the map).
* For deletion, the cluster number of the to-be-deleted cluster is to be provided (obtainable by clicking the marker belonging to the cluster/shape in question).
* For replacement, the cluster numbers of two or more conservative clusters (green shapes) need to be entered one after the other. Conceptually, a replacement will always mean that two or more conservative clusters/green shapes are replaced by one more liberal cluster/blue shape as the more liberal buffer will have resulted in additional merges compared with the more conversative one. After all of the to-be-replaced clusters' numbers have been entered, the user is asked to provide the number of the more liberal cluster (= blue shape) that will be included in the final data frame instead. After the operation is finished, the result can be seen in orange (orange marker, orange polygon) on the map.
* After completing one deletion or replacement process, the user can either decide to continue editing or finish the procedure. If the latter is chosen, the data (consisting of rows that were identical between the two data sets all along, the rows of the conservative buffer data set that differ from their more liberal counterparts but weren't deleted or replaced, plus the rows of the more liberal buffer data sets that differ from their more conservative counterparts and were manually chosen to replace them) is written to csv.



