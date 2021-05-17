
# SimRa Analysis Pipeline

## Introduction

TU Berlin's Mobile Cloud Computing Group have launched their  [SimRa project](https://www.digital-future.berlin/en/research/projects/simra/ "SimRa Project Site") in 2018. Its aim is to collect data on near-accidents and hazardous situations in bicycle traffic in Berlin and other metropolitan areas via a smartphone app (available for Android and iOS).

The project's *Analysis Pipeline* enables the mapping of incident data to junctions and segments (sections of roads between two junctions). This mapping allows for the aggregation of incident data per location and hence facilitates the identification of particularly dangerous spots and areas.

What the current project mainly does is
1. obtain the desired geographical information (junctions, segments) from the raw Open Street Maps data (neither of these types are explicitly contained in the raw data), 
1. transform the one-dimensional raw OSM data to polygons (Open Street Maps follows a graph theory data model, i.e. there are nodes and edges, with the edges being collections of nodes). 

## Installation/Set-Up

### Strategy a) (recommended): using Docker.

The preferred way of setting up the projects is to use Docker. 

To this end, each of the `segments` and `junctions` subdirectories contains a `Dockerfile` (the two projects will be running in separate containers as they are mostly independent). 

What is a `Dockerfile`? From the documentation:

```
A `Dockerfile` is a text document that contains all the commands a user could call on the command line to assemble an image. Using `docker build` users can create an automated build that executes several command-line instructions in succession.
```

Contents of the (very basic) `Dockerfile` used here:
- `FROM python:3.8` : Every `Dockerfile` must begin with a `FROM` instruction which specifies the base/parent image from which to build. Here, we're using the offical Python 3.8 image as our base.
- `WORKDIR /src` : specifies our working directory **inside the container**.
- `COPY requirements.txt .` : copies `requirements.txt` into the working directory inside the container.
- `RUN pip install --no-cache-dir -r requirements.txt` : installs all the dependencies contained in `requirements.txt` in the container.
- `COPY *.py .` : copy all Python scripts into the container's working directory.
- `CMD [ "OSM_jcts.py" ]` : the main purpose of a `CMD` is to provide defaults for an executing container (these will be used if `Docker run` is executed without arguments). They can include an executable (such as the project's main script), or they can be used to provide default arguments for an `ENTRYPOINT` instruction.
- `ENTRYPOINT [ "python" ]` : thanks to this command, we don't have to include `python` when `docker run`-ning python scripts in our container.

Running the container:
- `docker build -t junctions:latest .` : builds the container image based on the `Dockerfile`. The name of the image will be `junctions`.
- `docker run -v "$(pwd)"/csv_data:/src/csv_data -v "$(pwd)"/html_maps:/src/html_maps -v "$(pwd)"/pickled_data:/src/pickled_data junctions OSM_jcts.py "leipzig" 2` : run `OSM_jcts.py`, mounting three volumes (here: directories): `csv_data`, `html_maps` and `pickled_data`. "leipzig" and "2" are passed to `OSM_jcts.py` as arguments (region, buffer size). `$(pwd)` gets the path to the directory in which the current process is executing (in Unix systems). It is in this example enclosed in quotation marks as there was a space in one of my directory names (Apple's fault!!!). `"$(pwd)"/html_maps` is the path of the to-be-mounted directory on the local machine. After the `:` follows the location the directory will be mounted into inside the container. `-v` stands for volume (we're mounting volumes).

For segments, the procedure is analogous.

***Known issue**: occasionally, `urllib3` will throw `IncompleteRead`/`ProtocolError` when querying the Overpass API from inside the container. Currently I am not aware of an amazing solution to this project but rebuilding the image and trying again (potentially a few times) has thus far solved the issue for me.

### Strategy b): using a virtual environment

Python version: 3.8.3 64-bit

A `requirements.txt` file is provided. 

To keep dependencies organized, you are advised to set up a virtual environment for each project (Python pain). The most straightforward virtual environment management strategy is to just use `venv`, a module that is shipped with Python since version 3.3 (no additional install required) and `pip`, the standard Python package management tool. 

To do so, navigate to the project's top level folder (i.e., one level above the segments/junctions subdirectories) and execute the command `python3 -m venv name_of_env`, replacing 'name_of_env' with the name you want to assign your virtual environment. A new directory containing the virtual environment will be generated in the current folder. Then, activate the virtual environment with the command `source name_of_env/bin/activate` (again, replacing 'name_of_env' with the name you have given your environment). 

Then run `python -m pip install -r 'requirements.txt'` inside the project folder to install all of the required packages.

## Obtaining junction data

The project is logically separated into scripts dealing with junction data and scripts concerned with segment data. When generating the data for a specific region, it is crucial that the junction unit is run first as it generates a data set the segments unit requires (this way redundant computations are avoided - recall that segments are obtained by splitting roads at junctions). 

`OSM_jcts.py` is the main script in this logical unit. When calling it, the two parameters `region` and `buffer size` must be provided. Example call: `python OSM_jcts.py "leipzig" 2`.

`OSM_jcts.py` outputs the following files: 
- `{region}_junctions_complete_{date}.csv`, e.g. `berlin_junctions_complete_2021-05-03.csv` (written into the `/csv_data` subdirectory). This file contains the geometric properties of all the junctions in the area (i.e., lists of latitudes and longitudes from which polygons can be created) as well as other relevant characteristics such as the names and types of the associated roads.
- `{region}_junctions_buffer={buffer_size}` (written into the `/pickled_data` subdirectory). `Pickle` is a Python serialization format that is much more enjoyable to read e.g. pandas data frames from than .csv. This pickle is generated for use by the manual merging tool (see below for more information).
- `{region}-jcts-map_{loads of arguments that might disappear soon}.html` (written into the `/html_maps` subdirectory). A html representation of the junctions in this region.

## Getting segment data

**Important**: as mentionend above, the segments project requires a file written by the junctions project (`{region}_junctions_for_segs.csv`). That is because in order to obtain segments, highways need to broken into pieces at junctions. Obviously it would be more aesthetic if the two projects were completely independet, but efficiency considerations outweigh aesthetic ones here. Long story short: in order to run the segments code for a specific region, you must have executed the junctions counterpart beforehand. Then, move the file from the `PyPipeline_/junctions/csv_data` directory into the `PyPipeline_/segments/csv_data` directory. You can do this manually or e.g. by running the command `mv "$(pwd)"/junctions/csv_data/leipzig_junctions_for_segs.csv "$(pwd)"/segments/csv_data/leipzig_junctions_for_segs.csv` in the `PyPipeline_/` directory.
(In case you're wondering, the reason why the `{region}_junctions_for_segs.csv`-file isn't written into the segments' csv folder is to ensure junctions and segments don't rw from/into each other's directories, as if they did we would have to mount even more directories when executing in Docker).

`OSM_segs.py` is the main script in this logical unit. When calling it, the parameter `region` must be provided. Example call: `python OSM_segs.py "leipzig"`.

`OSM_segs.py` outputs the following files: 
- `{region}_segments_complete_{date}.csv`, e.g. `berlin_segments_complete_2021-05-03.csv` (written into the `/csv_data` subdirectory). This file contains the geometric properties of all the segments in the area (i.e., lists of latitudes and longitudes from which polygons can be created) as well as other relevant characteristics such as the associated roads' names and types.
- `{region}_segments` (written into the `/pickled_data` subdirectory). `Pickle` is a Python serialization format that is much more enjoyable to read e.g. pandas data frames from than .csv. This pickle is generated for use by the manual merging tool (see below for more information).
- `{region}-segs-map_{date}.html` (written into the `/html_maps` subdirectory). A html representation of the segments in this region.

## Manually editing junction clusters

Clearly, no one value for **buffer_size** will deliver optimal clustering results in all cases. Therefore, once a fairly good value for **buffer_size** has been determined manual editing can be performed to optimize the clustering result. Concretely, the clustering solutions will be compared for a more conservative and a more liberal buffer size. The logic here is that the conservative- and the liberal buffer will for many cases produce the same clustering solutions, but in some cases, the liberal buffer will have produced additional merges where the conservative buffer hasn't. Hence, the user will be able to look at the locations where these differences have occurred and decide whether the more conservative or more liberal solution should be accepted into the final data frame.

For the junctions project, a CLI that guides the user through the process of manual cluster editing is now available: `manualMergeCLIFlow_jcts.py`. It is designed to enable a user-friendly step-by-step process, making it possible to use the functionality without having to dig into the code first. The actual logic is contained in the scripts `manualMergePrep_jcts.py`, `manualMergeTool_jcts.py`, and `mapJcts_clustAssist.py`. 

**IMPORTANT**: for running the `manualMergeCLIFlow_jcts.py` inside Docker, use the following command:

```
docker run -i -t -v "$(pwd)"/csv_data:/src/csv_data -v "$(pwd)"/html_maps:/src/html_maps -v "$(pwd)"/pickled_data:/src/pickled_data junctions manualMergeCLIFlow_jcts.py
```

The additional flags `-i -t` are required to enable an interactive shell inside the container for this application.

* Firstly, you will be prompted to provided the **region** to work with as a lowercase string (e.g., 'berlin'). 
* Then, the default values for a rather conservative and rather liberal buffer are presented (these are pulled from the `param_dict` in `utils.py` and can obviously be altered), so you can either accept them or provide custom values. When providing custom values, ensure that they aren't too far apart (a difference of 0.25 is usually ideal) - the further apart they are, the more choices between conservative and liberal solutions will have to be performed. 
* Thereafter, the complete data for both buffer sizes is either retrieved from memory (if available) or computed and a comparison is carried out: where do the two data sets differ regarding the clustering solutions that were produced? - A HTML map displaying the differences is generated, and you will be informed of its location in the project directory. NOTE: the pickled (serialized) data sets used for this procedure are tracked by git, so if a map appears that already contains orange shapes this means that previous manual editing has taken place. If this process shall be reverted and the manual editing be performed from the beginning again, please navigate to the `pickled_data` directory (within the `junctions`-directory) and delete the pickled data sets corresponding to the buffer sizes chosen, i.e. if you want to compare the two buffer sizes `2` and `2.25` for `leipzig`, delete `pickled_data/leipzig_junctions_buffer=2` and `pickled_data/leipzig_junctions_buffer=2.25` and start `manualMergeCLIFlow_jcts.py` again to perform manual editing based on pristine, un-edited datasets.
* You will then be prompted to open `manual_merge_config/{region}.toml` to add any desired modifications. Modifications fall into two categories: delete and replace. Add all the green (!) clusters you want to delete (there is no need to delete blue clusters as the data set corresponding to the green clusters is the one we're working with, i.e. it is the default and can be altered as desired by either deleting shapes or replacing them by blue ones) to the `delete`-list. If you don't want to delete any clusters, just leave the delete-list empty. For each of the clusters you want to modify, add an individual `[[modify]]` block, as shown in the example. This `toml` code
````
[[replace]]
old = [429.0, 433.0]
new = 48.0

[[replace]]
old = [509.0, 507.0]
new = 62.0
````
becomes
````
'replace': [{'old': [429.0, 433.0], 'new': 48.0}, {'old': [509.0, 507.0], 'new': 62.0}]
````
when read by python, i.e. a list of dictionaries.
* Once you're done adding the desired modifications to the config file, enter `ok` and the alterations will be executed.
* The data (consisting of those rows that were identical between the two data sets - conservative and liberal - all along, the rows of the conservative buffer data set that differ from their more liberal counterparts but weren't deleted or replaced, plus the rows of the more liberal buffer data sets that differ from their more conservative counterparts and were manually chosen to replace them) is written to csv. Modified clusters will appear in orange on the html map.

**NOTE**: The scenario where no replacements, but only deletions are to be performed is currently not supported by the CLI flow as it seems unlikely, but might be covered in the future.

## Manually editing segment clusters

Coming up.

