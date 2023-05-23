# Point To Hexagon
This is an implementation of how to convert trajecotry datasets to a higher-order trajectory datasets.
We provide the code and datasets used in our paper: [title](link).


![Overview of Tesselation](img/heatmap1.png)


## Table of Contents
- [Point To Hexagon](#point-to-hexagon)
  - [Table of Contents](#table-of-contents)
  - [Description](#description)
  - [Dependencies](#dependencies)
    - [Routing Engine](#routing-engine)
    - [Tesselation Engine](#tesselation-engine)
    - [Python Dependencies](#python-dependencies)
  - [Convert Check-ins to Route Points](#convert-check-ins-to-route-points)
    - [Data format](#data-format)
    - [Command Arguments for Converting Check-in Data to Trajectory Points](#command-arguments-for-converting-check-in-data-to-trajectory-points)
    - [Map-matching](#map-matching)
    - [Using Other Routing Engines](#using-other-routing-engines)
  - [Convert Route Points to Hexagon Sequences](#convert-route-points-to-hexagon-sequences)
    - [Data format](#data-format-1)
    - [Command Arguments for Converting Route Points to Hexagon Sequences](#command-arguments-for-converting-route-points-to-hexagon-sequences)
    - [Map-matching](#map-matching-1)
  - [Visulization](#visulization)
  - [Published Datasets](#published-datasets)
  - [License](#license)
  - [Contact](#contact)
  - [Acknowledgments](#acknowledgments)
  - [Citation](#citation)


## Description
This repository contains a pipelie to to convert datasets from check-ins to hexagon sequences.

We usually have two types of trajectory datasets: check-ins and gps traces.

The check-in dataset is a sequence of check-ins, each of which is a pair of location as source and destination.
This type of dataset can be gathered from social media platforms or any platforms that allow users to input check-ins, or some organizations that collect check-ins from users.
For example check-ins in the taxi dataset are collected from taxi companies (we just have the source location and the destination location.)

Also we could have gps traces, which is a sequence of gps points. This GPS traces can be collected from GPS devices or mobile phones.
For example, the GPS traces in the taxi dataset are collected from GPS devices installed in taxis.
Or we can collect GPS traces from mobile phones, which is more common nowadays.
GPS traces are more accurate than check-ins, however, they are more difficult to collect and process, also the due to error in loacating the GPS points, the GPS traces are usually noisy and need to be cleaned and map-matched.

The following diagram shows the general pipeline of converting datasets to higher-order trajectory datasets.

![Overview of Data Conversion](img/pipeline.jpg)


## Dependencies

### Routing Engine
We are using OSRM as the routing engine and map-matching engine.

Here is a link to learn how to install and run OSRM.
[How to setup OSRM usgin Docker](https://github.com/Project-OSRM/osrm-backend#using-docker)

### Tesselation Engine
Also we are using H3 as the hexagon tesselation engine.
(Do we need install the H3 library other than the python package?)

### Python Dependencies
For the python code you can install the dependencies by running:
```sh
pip install -r requirements.txt
```


## Convert Check-ins to Route Points

To convert check-ins to route points, we need to use a routing engine to generate the route points between the source and destination of each check-in.
Make sure you have the information of the routing engine you are using, such as the host and port of the routing engine.

### Data format
The input data should be a csv file and, have the following columns:

```
start_point_lon, start_point_lat, end_point_lon, end_point_lat
```


### Command Arguments for Converting Check-in Data to Trajectory Points

The `loc2point_run.py` script accepts command-line arguments for converting check-in data to trajectory points. Below is a description of each argument:

- `input_file` (positional argument): The path to the input file containing the check-in data.

Optional arguments:

- `-o, --output`: The path to the output file. If not specified, the default value is `output.csv`.

- `-slon, --start-column-longitude`: The column name for the longitude of the start point. Default value: `start_point_lon`.

- `-slat, --start-column-latitude`: The column name for the latitude of the start point. Default value: `start_point_lat`.

- `-elon, --end-column-longitude`: The column name for the longitude of the end point. Default value: `end_point_lon`.

- `-elat, --end-column-latitude`: The column name for the latitude of the end point. Default value: `end_point_lat`.

- `-or, --output-route`: The column name for the route in the output file. Default value: `route_points`.

- `-u, --base-url`: The base URL of the routing service (specifically OSRM). Default value: `http://127.0.0.1:5000`.

- `-t, --threads`: The number of threads to use for processing. Default value: `70`.

- `-s, --split`: Flag to indicate whether to save the output of each thread separately.  If the split option is enabled, the output file will be multiple csv files (one for each thread.) Default value: `False`.

To run the script with the desired arguments, use the following command:

```
python loc2point_run.py [input_file] [-o OUTPUT] [-slon START_COLUMN_LONGITUDE] [-slat START_COLUMN_LATITUDE]
               [-elon END_COLUMN_LONGITUDE] [-elat END_COLUMN_LATITUDE] [-or OUTPUT_ROUTE] [-u BASE_URL]
               [-t THREADS] [-s]
```

Make sure to replace `[input_file]` with the actual path to the input file.

Note: The default values mentioned above are used when the corresponding argument is not provided.


### Map-matching
As we use OSRM to generate the route points, we do not need map matching for check-ins because we already have map-matched points for our trajectories.

### Using Other Routing Engines
Our implementation is compatible with other routing engines, you just need to implement the routing engine api like `lib/api/OpenSteetMap.py` file and change the api class in `loc2point_run.py` to your routing engine api class.

## Convert Route Points to Hexagon Sequences

### Data format
The input data should be a csv file and, have the following columns:

which the route points are in the following format:
```sh
python preprocess/preprocess.py --res 9 --data data/Archive/ --save nycTaxi
```


### Command Arguments for Converting Route Points to Hexagon Sequences

```sh
python preprocess/porto.py --res 9
```
Alternatively, run the bash script in which you can define your job 
```sh
bash job.sh
```

### Map-matching

For map-mathching of the route points, we use OSRM to map-match the route points to the road network.
You can run the `maching_run.py` script to map-match the route points.

The `maching_run.py` script accepts command-line arguments for map-matching the route points. Below is a description of each argument:

- TODO

Here is one example of running the map-matching on the porto dataset:

Noisy GPS Trace:

![Noisy GPS Trace](img/unmatched-gps-trace.png)


Map-Matched GPS Trace:

![Map-Matched GPS Trace](img/matched-gps-trace.png)



## Visulization


## Published Datasets 
Due to the storage limit, you can find more datasets on [Zenodo](https://zenodo.org/). 


## License
Distributed under the MIT License. See `LICENSE.txt` for more information.


## Contact

Your Name - [@twitter_handle](https://twitter.com/twitter_handle) - email@email_client.com

Project Link: [https://github.com/alifa98/point2hex](https://github.com/alifa98/point2hex)


## Acknowledgments
* []()
* []()
* []()

## Citation

If you like our work and/or use the code/datasets we provide, please consider citing our work as:

to be filled...

Alternatively, you can use the following BibTeX formatting:

```tex
insert BibTeX formatting
```
