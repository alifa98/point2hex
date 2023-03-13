import argparse
import os
from lib.ConfigLoader import ConfigLoader
from lib.LocationToPoint import send_get_route_request
import asyncio
import pandas as pd
import time

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
parser.add_argument('-t', '--threads', help='Concurrent requests',
                    action='store', default=config('default_concurrent_requests'))
parser.add_argument('-mt', '--max-try', help='Max retries',
                    action='store', default=config('default_max_retries'))
parser.add_argument('-d', '--delay', help='Retry delay (ms)',
                    action='store', default=config('default_retry_delay'))
parser.add_argument('-T', '--timeout',
                    help='Timeout for each request (ms)', action='store', default=config('default_timeout'))

# points 2 Hexagons
parser.add_argument('-r', '--resolution',
                    help='Resolution of the hexagon grid', default=9)
parser.add_argument('-ox', '--hexagon-serquence',
                    help='Hexagon serquence', default='hex_sequence')

args = parser.parse_args()

limit = asyncio.Semaphore(int(args.threads))

async def get_route_and_set_task(trips, index, start_point, end_point):
    async with limit:
        trips.at[index, args.output_column] = send_get_route_request(args.base_url, start_point, end_point)
        print("Route for trip {} is ready".format(index))

async def get_all_routes(trips):
    tasks = []
    for i in range(len(trips)):
        start_point = (trips.iloc[i][args.start_column_longitude], trips.iloc[i][args.start_column_latitude])
        end_point = (trips.iloc[i][args.end_column_longitude], trips.iloc[i][args.end_column_latitude])
        task = asyncio.ensure_future(get_route_and_set_task(trips, i, start_point, end_point))
        tasks.append(task)
    await asyncio.gather(*tasks, return_exceptions=True)


data_file = pd.read_csv(args.input_file)
data_file[args.output_column] = pd.Series(dtype=object)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
    asyncio.get_event_loop().run_until_complete(get_all_routes(data_file))
except KeyboardInterrupt:
    print("Exiting...")

start_time = time.time()

duration = time.time() - start_time

data_file.to_csv(args.output, index=False)
