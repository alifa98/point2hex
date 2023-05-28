import argparse
import threading
import pandas as pd
import requests
from lib.Utils import get_logger

from lib.api.OpenSteetMap import OpenStreetAPI

parser = argparse.ArgumentParser(
    description='Match the route points on the map')

# Define the command-line arguments
parser.add_argument('input_file', help='Input file path')
parser.add_argument('-o', "--output", help='Output File',
                    action='store', default='output.csv')
parser.add_argument(
    '-c', "--column", help='Route Points Column Name', default='route_points')
parser.add_argument('-u', '--base-url',
                    help='Base URL of the Map Matching Service', action='store', default="http://127.0.0.1:5000")
parser.add_argument('-t', '--threads', help='Number of Threads',
                    action='store', default=70)
args = parser.parse_args()


class MatchRoutePointsThread(threading.Thread):
    def __init__(self, thread_id, start_index, end_index, data, api, logger):
        threading.Thread.__init__(self)
        self.id = thread_id
        self.start_index = start_index
        self.end_index = end_index
        self.data = data
        self.api = api
        self.logger = logger

    def run(self):
        with requests.Session() as request_session:
            for index in range(self.start_index, self.end_index):
                try:
                    original_points = eval(self.data.iloc[index][args.column])

                    if len(original_points) < 2:
                        self.logger.warn(
                            f"Thread-{self.id}: route for {index} has less than 2 points. Skipping...")
                        continue

                    map_matched_points = self.send_request(
                        request_session, original_points)
                    if not map_matched_points:
                        self.logger.error(
                            f"Thread-{self.id}: route for {index} is empty. Skipping...")
                        continue
                    self.update_points(index, map_matched_points)
                except Exception as e:
                    self.logger.error(
                        f"Thread-{self.id}: Error while matching route for {index}. Skipping...\n{e}")

    def send_request(self, session, points):
        url = self.api.prepare_matching_url(points)
        response = session.get(url)
        response_json = response.json()
        if response_json['code'] == 'Ok':
            return self.api.parse_matching_response(response_json)
        else:
            raise Exception(f'Map Matching Error, Response: {response_json}')

    def update_points(self, index, points):
        self.data.iloc[index][args.column] = points


def get_split_points(total, num_threads):
    step = (total // int(num_threads)) + 1
    split_points_list = [i for i in range(0, total, step)]

    # make sure all of the instaces included (last step may contain more values)
    split_points_list.pop()
    # rages are like [start,end) so we do not need to add -1 here.
    split_points_list.append(total)

    return split_points_list


api = OpenStreetAPI(args.base_url)
logger = get_logger("map_match")


# Loading Data file
logger.info("Loading data file...")
data_file = pd.read_csv(args.input_file)

# split points of the data to threads
logger.info("Splitting data to threads...")
split_points = get_split_points(len(data_file), args.threads)

threads_list = []

logger.info("Creating threads...")
for i in range(len(split_points) - 1):
    threads_list.append(
        MatchRoutePointsThread(
            i,
            split_points[i],
            split_points[i + 1],
            data_file,
            api,
            logger
        )
    )

logger.info("Starting threads...")
for t in threads_list:
    t.start()

logger.info("Waiting for threads to finish...")
for t in threads_list:
    t.join()
logger.debug("All threads are finished.")

## Saving the output
logger.info("Saving the output...")
data_file.to_csv(args.output, index=False)

logger.info("Job is done.")
