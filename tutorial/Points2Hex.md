

# Step by step tutorial for converting GPS trace data to hexagon trajectories

This is a step-by-step example of how to use Point2Hex to convert a GPS trace dataset to hexagon traajectories.


# Step 1: clone the repository
use the following command to clone the repository:
```bash
git clone https://github.com/alifa98/point2hex.git
```

# Step 2: Prepare the dataset
You can find the GPS traces toy dataset in the `data` folder in the current `tutorial` folder. The file name is `porto_toy.csv`. we are going to use this dataset for this tutorial. The dataset is a CSV file with first 10000 rows of the Porto dataset.

`porto_toy.csv`  header is as follows:

```
"TRIP_ID","CALL_TYPE","ORIGIN_CALL","ORIGIN_STAND","TAXI_ID","TIMESTAMP","DAY_TYPE","MISSING_DATA","TRAJ_COLUMN"
```

We just need the `TRAJ_COLUMN` column for this tutorial. The `TRAJ_COLUMN` column is a list of GPS points in the following format:

```
[[lon1, lat1], [lon2, lat2], ...]
```


# Step 3: Run the OSRM back-end

If you do not have any OSRM back-end, you can use the following command to run a docker container with OSRM back-end on you local machine.

You should download the map data for running a local OSRM back-end.
You can download the map data from [this website](https://download.geofabrik.de/).

For this tutorial we need the data for Porto, [download from here](https://download.geofabrik.de/europe/portugal-latest.osm.pbf)


Run the following commands in the folder that you have downloaded the map data:

```bash
docker run -t -v "${PWD}:/data" ghcr.io/project-osrm/osrm-backend osrm-extract -p /opt/car.lua /data/portugal-latest.osm.pbf || "osrm-extract failed"
docker run -t -v "${PWD}:/data" ghcr.io/project-osrm/osrm-backend osrm-partition /data/portugal-latest.osrm || "osrm-partition failed"
docker run -t -v "${PWD}:/data" ghcr.io/project-osrm/osrm-backend osrm-customize /data/portugal-latest.osrm || "osrm-customize failed"
```

This is the tricky part.
You need to run the OSRM back-end with a higher limit than default for matching service because the default limit is a small value (I guess 100) and you cannot map-match the GPS traces with more than 100 points.

For this purpose, you need to run the OSRM back-end using the following command:

```bash
docker run -t -i -p 5000:5000 -v "${PWD}:/data" ghcr.io/project-osrm/osrm-backend osrm-routed --max-matching-size 600 --algorithm mld /data/portugal-latest.osrm
```

The limit of the number of coordinates is set to 600 by passing an argument to `osrm-routed` in the docker container.
You can change it based on your needs.


# Step 3: Install the requirements
You can create a conda environment and install the requirements using the following commands:

```bash
conda env create --name point2hex --file=environments.yml
```

Then, activate the environment:

```bash
conda activate point2hex
```

# Step 4: Map-Match the GPS traces
You can use the following command to use matching service of the local OSRM back-end to map-match the GPS traces.

Run the following command in the root folder of the repository:

```bash
python matching_run.py tutorial/data/porto_toy.csv -o tutorial/data/porto_toy_map-matched.csv -c "TRAJ_COLUMN" -u "http://127.0.0.1:5000" -t 50
```

- The first argument is the path to the CSV file that contains the GPS traces.
- The `-o` argument is the name of the output file.
- The `-c` argument is the name of the column that contains the GPS traces in the CSV file.
- The `-u` argument is the URL of the local OSRM back-end.
- The `-t` argument is the number of threads that you want to use for map-matching.


# Step 5: Convert the trajectories to hexagon trajectories
You can use the following command to convert the trajectories to hexagon trajectories:

```bash
python point2hex_run.py tutorial/data/porto/ -o tutorial/data/porto_toy_hex-r10.csv -c "TRAJ_COLUMN" -r 10
```

- The first argument is the path to the folder that contains the CSV files that contain the GPS traces. (The output of the previous step, also csv files should have the same header)
- The `-o` argument is the name of the output file.
- The `-c` argument is the name of the column that contains the GPS traces in the input CSV files.
- The `-r` argument is the resolution of the hexagon grid. (The default value is 6)

Now you have your trajectories in hexagon format.
You can use them for your analysis.

# Step 6: Visualize the hexagon trajectories
when you have the hexagon trajectories, you can use the following command to visualize the hexagon in a hitmap:

```bash
python plot_run.py tutorial/data/porto_toy_hex-r10.csv -z 12 
```

- The first argument is the path to the CSV file that contains the hexagon trajectories.
- The `-z` argument is the zoom level of the map. (The default value is 12) (higher zoom level means zooming in)
- the output will be saved in the `out/plots/heatmap-*.jpg` file.





