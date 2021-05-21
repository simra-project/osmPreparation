
# Set Python 3.8 as base image
FROM python:3.8

# Set working directory inside the container
WORKDIR /src

# Copy requirements.txt into the container
COPY requirements.txt .

# Install all dependencies from the requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy all python scripts into the container
COPY *.py .

# CMD will be run if 'docker run' is executed without parameters
CMD [ "OSM_jcts.py" ] 

# Adding this entrypoint means we don't have to include 'python' in 
# our Docker run commands
ENTRYPOINT [ "python" ]

# ********************************************************************
# HOW TO USE
# Execute these commands in a terminal inside the PyPipeline_/junctions directory

# STEP 1: build the image according to this Dockerfile:

# docker build -t junctions:latest .

# STEP 2: run the main script (OSM_jcts.py) inside the container, mounting
#         the three directories to which data is written/from which data is
#         read (csv_data, html_maps, pickled_data), and provide arguments
#         to 'OSM_jcts.py', e.g. here "leipzig" as region and 2 as buffer

# docker run -v "$(pwd)"/csv_data:/src/csv_data -v "$(pwd)"/html_maps:/src/html_maps -v "$(pwd)"/pickled_data:/src/pickled_data junctions OSM_jcts.py "leipzig" 2

# => $(pwd) gets the path to the directory in which the current process is executing. 
#           It is in this example in quotation marks as there was a space in one of my directory names (Apple's fault!!!)
# => "$(pwd)"/html_maps is the path of the to-be-mounted directory on the local machine. 
# => after the ":" follows the location the directory will be mounted to inside the container.
# => 'v' stands for 'volume'.