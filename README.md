
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

## Manually editing junction clusters

Clearly, no one value for **buffer_size** will deliver optimal clustering results in all cases. Therefore, once a fairly good value for **buffer_size** has been determined manual editing can be performed to optimize the clustering result. 

### a) Preparing the manual cluster editing

The script `manualClusterPrep.py` provides the relevant data for manual editing to be performed. In order to do so, choose values for a smaller, more conservative and a larger, more liberal buffer. They shouldn't be too far apart (that would be unreasonable and produce an unmanageable amount of inconsistencies) and the unknown 'optimal' buffer size should supposedly be located in between them. For most city layouts that aren't particularly narrow (Bern) or wide (Berlin), 2 and 2.5 should be suitable as small- and large buffer value, respectively. The lazier you are, the closer together they should be 🤪
Provide the name of the region in question as well as the values for the small and large buffer as input parameters to the `meta_assist`-function. Run.

The script will execute the main script `OSM_jcts.py` for the smaller and larger buffer and determine which clustering solutions appear in both cases (i.e., junctions that equally remain on their own respectively are merged identically) and which don't. For inconsistent cases, the two different solutions (using a smaller vs. larger buffer) will be plotted on a map named `{region}-jcts-manualClust_YYY-MM-DD.html` so that they can easily be compared. 
Additionally, three `pickled` data sets are produced by `manualClusterPrep.py`. `Pickle` is a python library for (de-)serializing data. By using it, we can avoid ugly and cumbersome csv-parsing (parsing lists from string 😱💀👿). these are: `consistent_clusters_{region}`,`small_buf_inconsist_{region}`, and `large_buf_inconsist_{region}`. **IMPORTANT**: ensure the map and the three pickled data sets are in the `junctions`-directory. If they aren't, move them for the second part of the procedure to work.

### b) Performing the manual cluster editing

Look at the map produced by `manualClusterPrep.py` (`{region}-jcts-manualClust_YYY-MM-DD.html`). Clustering solutions that differ depending on buffer size are presented, the large buffer solutions in blue, the small buffer ones in green. Smaller buffer solutions (i.e., more conservative merging) are accepted by default; should you discover a case where the more liberal large buffer solution is preferred, proceed as follows:

Assuming you want to replace two clusters `600.0` and `601.0` from the small buffer data set with cluster `605.0` from the large buffer data set, with the region being `Stuttgart`. In the junctions directory (where the output of `manualClusterPrep.py`, i.e. the map and the three pickled data sets also have to be located!), run:

```bash
python manualMergeTool.py --small_buf_clstrs='[600.0,601.0]' --large_buf_clstr=605.0 --region="stutt"
```

Reload the map. The replaced cluster will appear in orange (with cluster nr. `999999`). 

Once all corrections have taken place, scroll down to the bottom of `manualMergeTool.py` and re-do the in-/out-commenting like so:

```python
if __name__ == '__main__':
  # fire.Fire(update_clust)
  fire.Fire(save_result)
```

This way, the function `save_result` will be exposed as a command line interface (rather than `update_clust`). The manual editing result (i.e., a data frame containing both the consistent clustering solutions as well as the solution of choice for inconsistent cases - that is, the small buffer solution by default and the large buffer solution if manually chosen over the small buffer one): the output is a text file named `manual_merging_res_{region}_YYY-MM_DD.csv`

## Getting segment data

This logical unit of scripts mostly performs computations analogous to the junction unit described above, only for street segments rather than junction nodes. Hence, only where the segments unit deviates from what the junction unit does additional explanations will be provided.

* `OSM_segs.py`: 
    * the segment unit's main script's main function (double genitive, excuse the lack of elegance here) currently accepts one parameter less than its junctions equivalent; that is because it has (so far) not appeared necessary to vary the **bufferSize** depending on the respective geographical region. 
    * furthermore, code for performing computations for multiple regions concurrently is not provided atm; however, if required it can easily be copied from `OSM_jcts.py` (omitting the **bufferSize** for each region).
* `segmentizeAndEnrich.py`: this script reads the csv file generated in `findJunctions.py` from memory. The file contains the ids, latitudes and longitudes of junction nodes. This information is used to break highways into segments at junctions. 

The main output of the segments unit is a `{region}_segments_complete.csv` file (e.g., `berlin_segments_complete.csv`).