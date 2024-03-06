# Point to Hexagon
This is an implementation of how to convert trajectory datasets to higher-order trajectory datasets.
We provide the code and datasets used in our paper: [Point2Hex: Higher-order Mobility Flow Data and Resources](link).


![Overview of Tessellation](img/heatmap1.png)


## Table of Contents
- [Point to Hexagon](#point-to-hexagon)
  - [Table of Contents](#table-of-contents)
  - [Description](#description)
  - [Tutorial on How to Use the Code](#tutorial-on-how-to-use-the-code)
  - [Dependencies](#dependencies)
    - [Routing Engine](#routing-engine)
    - [Tessellation Engine](#tessellation-engine)
    - [Python Dependencies](#python-dependencies)
  - [Convert Check-ins to Route Points](#convert-check-ins-to-route-points)
    - [Data Format](#data-format)
    - [Command Arguments for Converting Check-in Data to Trajectory Points](#command-arguments-for-converting-check-in-data-to-trajectory-points)
    - [Map Matching](#map-matching)
    - [Using Other Routing Engines](#using-other-routing-engines)
  - [Convert Route Points to Hexagon Sequences](#convert-route-points-to-hexagon-sequences)
    - [Data Format](#data-format-1)
    - [Map Matching](#map-matching-1)
    - [Command Arguments for Converting Route Points to Hexagon Sequences](#command-arguments-for-converting-route-points-to-hexagon-sequences)
  - [Visualization](#visualization)
    - [Command-line Arguments](#command-line-arguments)
    - [Running the Script](#running-the-script)
  - [Output](#output)
  - [Published Datasets](#published-datasets)
  - [License](#license)
  - [Contact](#contact)
  - [Citation](#citation)


## Description
This repository contains a pipeline to convert datasets from check-ins to hexagon sequences.

We usually have two types of trajectory datasets: check-ins and GPS traces.

A check-in dataset is a sequence of check-ins, each of which is a pair of locations as the source and destination of a trip (Taxi), or a single location as a check-in location (FourSquare).
This type of dataset can be gathered from social media platforms or any platforms that allow users to input check-ins, or from organizations that collect check-ins from users.
For example, check-ins in the taxi dataset are collected from taxi companies (we only have the source location and the destination location),
or in the FourSquare dataset, the check-ins are collected from users (we have the check-in location, date, and the user ID).

We could also have GPS traces, which are a sequence of GPS points. These GPS traces can be collected from GPS devices or mobile phones.
For example, the GPS traces in the Porto taxi dataset are collected from GPS devices installed in taxis,
or we can collect GPS traces from mobile phones, which is more common nowadays.

GPS traces are more accurate than check-ins; however, they are more difficult to collect and process. Also, due to errors in locating the GPS points, the GPS traces are usually noisy and need to be cleaned and map-matched.

The following diagram shows the general pipeline for converting datasets to higher-order trajectory datasets.

![Overview of Data Conversion](img/pipeline-new.png)


## Tutorial on How to Use the Code
- [Convert a GPS-based Trajectory Dataset to Hexagon Sequences](tutorial/Points2Hex.md)

## Dependencies

### Routing Engine
We are using OSRM as the routing engine and map-matching engine.

Here is a link to learn how to install and run OSRM: [How to setup OSRM using Docker](https://github.com/Project-OSRM/osrm-backend#using-docker)

### Tessellation Engine
We are also using H3 as the hexagon tessellation engine.


### Python Dependencies
For the Python code, you can install the dependencies by running the following command:
```sh
conda env create --name point2hex --file=environment.yml
```

The command above will create a conda environment named `point2hex` and install the dependencies in that environment.

To run the command, you need to have conda installed on your system.


## Convert Check-ins to Route Points

To convert check-ins to route points, we need to use a routing engine to generate the route points between the source and destination of each check-in.
Make sure you have the information of the routing engine you are using, such as the host and port of the routing engine.

### Data Format
The input data should be a CSV file and should have the following columns:

```
start_point_lon, start_point_lat, end_point_lon, end_point_lat
```


### Command Arguments for Converting Check-in Data to Trajectory Points

The `loc2point_run.py` script accepts command-line arguments for converting check-in data to trajectory points.
Below is a description of each argument:

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

- `-s, --split`: Flag to indicate whether to save the output of each thread separately. If the split option is enabled, the output file will contain multiple CSV files (one for each thread). Default value: `False`.

To run the script with the desired arguments, use the following command:

```
python loc2point_run.py [input_file] [-o OUTPUT] [-slon START_COLUMN_LONGITUDE] [-slat START_COLUMN_LATITUDE]
               [-elon END_COLUMN_LONGITUDE] [-elat END_COLUMN_LATITUDE] [-or OUTPUT_ROUTE] [-u BASE_URL]
               [-t THREADS] [-s]
```

Make sure to replace `[input_file]` with the actual path to the input file.

Note: The default values mentioned above are used when the corresponding argument is not provided.


### Map Matching
As we use OSRM to generate the route points, we do not need map matching for check-ins because we already have map-matched points for our trajectories.

### Using Other Routing Engines
Our implementation is compatible with other routing engines. You just need to implement the routing engine API like the `lib/api/OpenStreetMap.py` file and change the API class in `loc2point_run.py` to your routing engine API class.

## Convert Route Points to Hexagon Sequences

If the dataset is a GPS-based dataset originally, we need to map-match the GPS points to the road network and then convert the map-matched GPS points to hexagon sequences.
If the dataset is a check-in dataset, and we have used a routing engine to generate the route points, we can directly convert the route points to hexagon sequences.

### Data Format
Each row in the input CSV files should have a column that contains a list of tuples or a list of lists, each containing two items (longitude and latitude).
For example: `[(long, lat), (long, lat),...(long, lat)]`.


### Map Matching

For map matching of the route points, we use OSRM to map-match the route points to the road network.
You can run the `matching_run.py` script to map-match the route points.

The `matching_run.py` script is designed to match route points on a map using a Map Matching Service.
It utilizes threading to improve performance by processing multiple routes simultaneously.
The script takes command-line arguments to specify input and output files, column names, base URL of the Map Matching Service, and the number of threads to use for parallel processing.

**Usage:**
```
python matching_run.py [input_file] [-o OUTPUT] [-c COLUMN] [-u BASE_URL] [-t THREADS]
```

**Arguments:**
- `input_file`: Path to the input file containing route data.
- `-o, --output OUTPUT`: Path to the output file where the matched route data will be saved. (Default: 'output.csv')
- `-c, --column COLUMN`: The name of the column in the input file that contains the route points. (Default: 'route_points')
- `-u, --base-url BASE_URL`: The base URL of the Map Matching Service. (Default: 'http://127.0.0.1:5000')
- `-t, --threads THREADS`: The number of threads to use for parallel processing. (Default: 70)

**Script Overview:**
1. Parse the command-line arguments.
2. Define the `MatchRoutePointsThread` class, which represents a thread responsible for matching route points.
3. Initialize the Map Matching Service API and the logger.
4. Load the input data file specified by `input_file`.
5. Split the data points into multiple segments based on the number of threads.
6. Create threads for each segment of data.
7. Start the threads to initiate the map matching process.
8. Wait for all threads to finish their execution.
9. Save the output data to the specified output file.
10. Display a completion message.

**Thread Execution:**
The script uses threading to process route points in parallel.
Each thread represents a segment of the data and is responsible for matching the route points within that segment.
The threads operate as follows:
1. Each thread retrieves route points from the input data for a trajectory.
2. If the number of route points is less than 2, a warning is logged, and the thread skips to the next trajectory.
3. The thread sends a request to the Map Matching Service API with the original route points.
4. If the response is successful, the matched route points are obtained from the response. If multiple segments are returned, the thread will send requests for routing between the matched segments (the routing is done by the OSRM routing engine, between the last point of the previous segment and the first point of the next segment of the trajectory).
5. If the response is not successful, an error is logged, and the thread skips to the next segment.
6. Once all threads have finished executing, the output data is saved to the specified output file.

**Example of Map Matching on the City Map**

Here is an example of running the map matching on the Porto dataset:


Noisy GPS Trace             |  Map-Matched GPS Trace
:-------------------------:|:-------------------------:
<img src=img/unmatched-gps-trace.png width=50% height=50%>  |  <img src=img/matched-gps-trace.png width=50% height=50%>


### Command Arguments for Converting Route Points to Hexagon Sequences

The `point2hex_run.py` script accepts command-line arguments for converting sequences of geographical coordinates into a sequence of hexagons.
Below is a description of each argument:

- `input_dir` (positional argument): The directory path where the input CSV files containing the route data are stored.

Optional arguments:

- `-o, --output`: The directory path where the output file will be stored. The output file will be named as `output_resX.csv`, where X denotes the resolution of hexagons. If not specified, the default value is `./` (current directory).

- `-r, --resolution`: A list of resolutions for generating hexagons, provided as comma-separated values. The default resolution is `6` if this argument is not provided.

- `-c, --column`: The name of the column in the input .csv files that contains route points. The default column name is `route_points` if this argument is not provided.

To run the script with the desired arguments, use the following command:

```
python point2hex_run.py [input_dir] [-o OUTPUT] [-r RESOLUTION] [-c COLUMN]
```

Make sure to replace `[input_dir]` with the actual path to the directory containing the input CSV files.

Note: The default values mentioned above are used when the corresponding argument is not provided.


## Visualization
The `plot_run.py` script reads an input CSV file containing higher order trajectory sequences and generates a hexagon heatmap visualization.
The script allows setting the zoom level of the map visualization via command-line arguments.

### Command-line Arguments

The script accepts the following command-line arguments:

- `input_file` (positional argument): The path to the input CSV file containing higher order trajectory sequences.

- `-z, --zoom` (optional argument): The zoom level of the map visualization. If not specified, the default zoom level is set to `12`.

### Running the Script

To execute the script, run the following command:

```bash
python plot_run.py <input_file> [-z ZOOM]
```

Here `<input_file>` should be replaced with the actual path to the input file, and `-z ZOOM` is an optional argument specifying the zoom level of the map.
If the zoom level is not provided, it defaults to `12`.

For example:

```bash
python plot_run.py ./input/data.csv -z 11.5
```

In this example, the script will read the CSV file from the `./input/data.csv` path, and the map zoom level will be `11.5`.


Note: The hexagons should be in a column named `higher_order_trajectory` separated by a space in the input file.
The column name is the same as the output column name of the `point2hex_run.py` script for hexagon sequences.


## Output

The script generates a heatmap visualization using the provided higher-order trajectory sequences.
The heatmap will be saved in the `out/plots` folder with the name `heatmap-zoomX-timestamp.jpeg`.


## Published Datasets
Due to storage limitations, you can find more datasets on [Zenodo](https://zenodo.org/records/8076553). 


## License
Distributed under the MIT License.


## Contact

Ali Faraji - faraji@yorku.ca

Jing Li - jliellen@yorku.ca

Project Link: [https://github.com/alifa98/point2hex](https://github.com/alifa98/point2hex)


## Citation

If you like our work and/or use the code/datasets we provide, please consider citing our work as:

Ali Faraji, Jing Li, Gian Alix, Mahmoud Alsaeed, Nina Yanin, Amirhossein Nadiri, and Manos Papagelis. 2023. Point2Hex: Higher-order Mobility Flow Data and Resources. In Proceedings of the 31st ACM International Conference on Advances in Geographic Information Systems (SIGSPATIAL '23). Association for Computing Machinery, New York, NY, USA, Article 69, 1–4. https://doi.org/10.1145/3589132.3625619


Alternatively, you can use the following BibTeX formatting:

```tex
@inproceedings{10.1145/3589132.3625619,
author = {Faraji, Ali and Li, Jing and Alix, Gian and Alsaeed, Mahmoud and Yanin, Nina and Nadiri, Amirhossein and Papagelis, Manos},
title = {Point2Hex: Higher-order Mobility Flow Data and Resources},
year = {2023},
isbn = {9798400701689},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = {https://doi.org/10.1145/3589132.3625619},
doi = {10.1145/3589132.3625619},
booktitle = {Proceedings of the 31st ACM International Conference on Advances in Geographic Information Systems},
articleno = {69},
numpages = {4},
keywords = {trajectory datasets, higher-order mobility flow datasets, generator},
location = {<conf-loc>, <city>Hamburg</city>, <country>Germany</country>, </conf-loc>},
series = {SIGSPATIAL '23}
}
```
