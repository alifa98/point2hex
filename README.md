# Point To Hexagon
This is an implementation of how to convert trajecotry datasets to a higher-order trajectory datasets.
We provide the code and datasets used in our paper: [title](link).

<img src="img/heatmap1.png" alt="Overview of tesselation" width="900">


<!-- TABLE OF CONTENTS -->
## Table of Contents
- [Point TO Hexagon](#point-to-hexagon)
  - [Table of Contents](#table-of-contents)
  - [Description](#description)
  - [Dependencies](#dependencies)
    - [Routing engine](#routing-engine)
  - [Convert check-ins to route points](#convert-check-ins-to-route-points)
    - [Data Format](#data-format)
    - [Command Arguments for Converting Check-in Data to Trajectory Points](#command-arguments-for-converting-check-in-data-to-trajectory-points)
    - [Map-matching](#map-matching)
    - [using other routing engines](#using-other-routing-engines)
  - [Convert route points to hexagon sequences](#convert-route-points-to-hexagon-sequences)
    - [Map-matching](#map-matching-1)
    - [Converting to hexagon sequences](#converting-to-hexagon-sequences)
  - [Publish datasets](#publish-datasets)
  - [License](#license)
  - [Contact](#contact)
  - [Acknowledgments](#acknowledgments)
  - [Citation](#citation)


<!-- DESCRIPTION -->
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

### Routing engine
We are using OSRM as the routing engine and map-matching engine.

Here is a link to learn how to install and run OSRM.
[How to setup OSRM usgin Docker](https://github.com/Project-OSRM/osrm-backend#using-docker)

Also we are using H3 as the hexagon tesselation engine.

For the python code you can install the dependencies by running:
```sh
pip install -r requirements.txt
```


## Convert check-ins to route points

To convert check-ins to route points, we need to use a routing engine to generate the route points between the source and destination of each check-in.
Make sure you have the information of the routing engine you are using, such as the host and port of the routing engine.

### Data Format
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

### using other routing engines
Our implementation is compatible with other routing engines, you just need to implement the routing engine api like `lib/api/OpenSteetMap.py` file and change the api class in `loc2point_run.py` to your routing engine api class.

## Convert route points to hexagon sequences

### Map-matching


### Converting to hexagon sequences
* From route points to hexagon sequences:
  ```sh
  python preprocess/porto.py --res 9
  ```
  Alternatively, run the bash script in which you can define your job 
  ```sh
  bash job.sh

## Visulization

<!-- USAGE EXAMPLES -->
## Usage

* From check-ins to rounte points:
  to be filled


  ```


<!-- PUBLISH DATASETS -->
## Publish datasets 

Due to the storage limit, you can find more datasets on [Zenodo](https://zenodo.org/). 


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.




<!-- CONTACT -->
## Contact

Your Name - [@twitter_handle](https://twitter.com/twitter_handle) - email@email_client.com

Project Link: [https://github.com/github_username/repo_name](https://github.com/github_username/repo_name)




<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* []()
* []()
* []()

## Citation

If you like our work and/or use the code/datasets we provide, please consider citing our work as:

to be filled...

Alternatively, you can use the following BibTeX formatting:

```
insert BibTeX formatting
```
