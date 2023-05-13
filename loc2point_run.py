# You can run this file to generate points from locations.
# this file uses OSRM API to generate routes between locations and then
# generate points on the route.

# the input file should be a csv file with the following columns:
# start_point_lon, start_point_lat, end_point_lon, end_point_lat
# the output file will be a csv file with the following columns:
# start_point_lon, start_point_lat, end_point_lon, end_point_lat, route_points
# route_points is a list of points (tuple) on the route between start and end points.
# if the split option is enabled, the output file will be multiple csv files with the same columns for each thread.

import pandas as pd
from lib.GetPointsThread import GeneratePointsThread
from lib.Utils import get_logger
from lib.api.OpenSteetMap import OpenStreetAPI
from lib.ArgsParse import parse_args


def get_split_points(total, num_threads):
    step = (total // int(num_threads)) + 1
    split_points_list = [i for i in range(0, total, step)]

    # make sure all of the instaces included (last step may contain more values)
    split_points_list.pop()
    # rages are like [start,end) so we do not need to add -1 here.
    split_points_list.append(total)

    return split_points_list


if __name__ == "__main__":
    args = parse_args()
    logger = get_logger("loc2point")

    # the API that we want to use
    api = OpenStreetAPI(args.base_url)

    # Loading Data file
    logger.info("Loading data file...")
    data_file = pd.read_csv(args.input_file)

    try:
        # split points of the data to threads
        split_points = get_split_points(len(data_file), args.threads)

        threads_list = []

        logger.info("Creating threads...")
        # Create new threads
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

        # Starting the threads
        logger.info("Starting...")
        for t in threads_list:
            t.start()

        # waiting for threads
        logger.info("Processing...")
        for t in threads_list:
            t.join()

        logger.debug("All threads are finished.")
        logger.info("Job is done.")

    except KeyboardInterrupt:
        print("Exiting...")

    if not args.split:
        data_file.to_csv(f"{args.output}.csv", index=False)
