import argparse
import logging
import os
import sys
from lib.ConfigLoader import ConfigLoader
import pandas as pd
import threading
from lib.GetPointsThread import GetRoutePointsTask

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


config = ConfigLoader(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), os.sep+'config.json'))

parser = argparse.ArgumentParser(description='Generate route points')

# loc 2 point
parser.add_argument('input_file', help='Input file path')

parser.add_argument('-o', "--output", help='Output file',
                    action='store', default='output.csv')
parser.add_argument('-slon', '--start-column-longitude', help='Start point column name (longitude)',
                    action='store', default='start_point_lon')
parser.add_argument('-slat', '--start-column-latitude', help='Start point column name (latitude)',
                    action='store', default='start_point_lat')
parser.add_argument('-elon', '--end-column-longitude', help='End point column name (longitude)',
                    action='store', default='end_point_lon')
parser.add_argument('-elat', '--end-column-latitude', help='End point column name (latitude)',
                    action='store', default='end_point_lat')
parser.add_argument('-oc', '--output-column', help='Route column name in the output file',
                    action='store', default='route_points')
parser.add_argument('-ps', '--point-save-off',
                    help='points will not be saved as a column', action='store_false')
parser.add_argument('-u', '--base-url',
                    help='Base URL of the routing service [OSRM]', action='store', default=config("default_routing_api_base_url"))
parser.add_argument('-t', '--threads', help='Number of Threads',
                    action='store', default=config('default_concurrent_requests'))
parser.add_argument('-cr', '--concurrent-requests',
                    help='number of concurrent requests to the OSRM API', action='store', default=10)
parser.add_argument('-mt', '--max-try', help='Max retries',
                    action='store', default=config('default_max_retries'))
parser.add_argument('-d', '--delay', help='Retry delay (ms)',
                    action='store', default=config('default_retry_delay'))
parser.add_argument('-T', '--timeout',
                    help='Timeout for each request (ms)', action='store', default=config('default_timeout'))
parser.add_argument('-S', '--split',
                    help='Output of each thread separately', action='store_true')
# points 2 Hexagons
parser.add_argument('-r', '--resolution',
                    help='Resolution of the hexagon grid', default=9)
parser.add_argument('-ox', '--hexagon-serquence',
                    help='Hexagon sequence', default='hex_sequence')

args = parser.parse_args()


def get_split_points(total, num_threads):
    step = (total // int(num_threads))+1
    split_points_list = [i for i in range(0, total, step)]

    # make sure all of the instaces included (last step may contain more values)
    split_points_list.pop()
    split_points_list.append(total) ## rages are like [start,end) so we do not need to add -1 here.

    return split_points_list


data_file = pd.read_csv(args.input_file)
data_file[args.output_column] = pd.Series(dtype=object)
try:
    sem = threading.Semaphore(value=int(args.concurrent_requests))

    # with tqdm(total=len(data_file)) as pbar:

    split_points = get_split_points(len(data_file), args.threads)

    threads_list = []
    # Create new threads
    for i in range(len(split_points)-1):

        threads_list.append(GetRoutePointsTask(i,
            data_file, split_points[i], split_points[i+1], sem, args))

    logging.info("Starting...")
    # Starting the threads
    for t in threads_list:
        t.start()

    logging.info("Processing...")
    # waiting for threads
    for t in threads_list:
        t.join()

    logging.info("Task Finished")

except KeyboardInterrupt:
    print("Exiting...")


if not args.split:
    data_file.to_csv(f"{args.output}.csv", index=False)
