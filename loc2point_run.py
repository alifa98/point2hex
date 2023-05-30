"""
This module is used to generate points from locations using the OSRM API. It generates routes between locations and then
generates points on the route.

The input should be a csv file with the following columns: start_point_lon, start_point_lat, end_point_lon, end_point_lat.
The output will be a csv file with the following columns: start_point_lon, start_point_lat, end_point_lon, end_point_lat, route_points.
route_points is a list of points (tuple) on the route between start and end points.

If the split option is enabled, the output will be multiple csv files with the same columns for each thread.
"""

import pandas as pd
from lib.GetPointsThread import GeneratePointsThread
from lib.Utils import get_logger
from lib.api.OpenSteetMap import OpenStreetAPI
from lib.ArgsParse import parse_args

def get_split_points(total, num_threads):
    """
    Returns a list of points where to split the data for threading.

    :param total: Total number of data points
    :param num_threads: Number of threads to be created
    :returns: A list of split points of the list to split the data for threading
    """
    step = (total // int(num_threads)) + 1
    split_points_list = [i for i in range(0, total, step)]

    # Make sure all of the instances included (last step may contain more values)
    split_points_list.pop()
    # Ranges are like [start,end) so we do not need to add -1 here.
    split_points_list.append(total)

    return split_points_list

if __name__ == "__main__":
    args = parse_args()
    logger = get_logger("loc2point")

    # Initialize the OpenStreetAPI
    api = OpenStreetAPI(args.base_url)

    # Loading Data file
    logger.info("Loading data file...")
    data_file = pd.read_csv(args.input_file)

    try:
        # Split points of the data to threads
        split_points = get_split_points(len(data_file), args.threads)

        threads_list = []

        # Create new threads
        logger.info("Creating threads...")
        for i in range(len(split_points) - 1):
            threads_list.append(
                GeneratePointsThread(
                    i,
                    data_file,
                    split_points[i],
                    split_points[i + 1],
                    api,
                    args,
                    logger,
                )
            )

        # Start the threads
        logger.info("Starting...")
        for thread in threads_list:
            thread.start()

        # Wait for all threads to finish
        logger.info("Processing...")
        for thread in threads_list:
            thread.join()

        logger.debug("All threads are finished.")
        logger.info("Job is done.")

    except KeyboardInterrupt:
        print("Exiting...")

    if not args.split:
        data_file.to_csv(f"{args.output}.csv", index=False)
