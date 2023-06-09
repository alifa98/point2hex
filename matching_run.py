import argparse
from io import StringIO
import threading
import pandas as pd
import requests
from lib.Utils import get_logger

from lib.api.OpenSteetMap import OpenStreetAPI

# Set up command line argument parsing
parser = argparse.ArgumentParser(
    description='Match the route points on the map')

# Define the command-line arguments
parser.add_argument('input_file', help='Input file path')
parser.add_argument('-o', "--output", help='Output file name or if the --steam is passed the output folder name',
                    action='store', default='output.csv')
parser.add_argument(
    '-c', "--column", help='Route points column name', default='route_points')
parser.add_argument('-u', '--base-url', help='Base URL of the Map Matching Service',
                    action='store', default="http://127.0.0.1:5000")
parser.add_argument('-t', '--threads',
                    help='Number of threads', action='store', default=70)
parser.add_argument('-s', '--stream',
                    help='Stream the output of each thread to a file in the output folder (for large datasets).', action='store_true')
args = parser.parse_args()

if args.stream:
    import os
    # Create the output folder if it does not exist
    os.makedirs(args.output, exist_ok=True)


class MatchRoutePointsThread(threading.Thread):
    # Thread class to match route points

    def __init__(self, thread_id, start_index, end_index, data, api, logger):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.start_index = start_index
        self.end_index = end_index
        self.data = data
        self.api = api
        self.logger = logger
        if args.stream:
            self.output_file_path = f"{args.output}/output-{thread_id}.csv"
            self.output_file = open(self.output_file_path, "w")

    def run(self):
        """
        Run the thread to match route points.
        """
        self._write_headers_for_steaming_file()
        with requests.Session() as request_session:
            for index in range(self.start_index, self.end_index):
                try:
                    original_points = eval(self.data.iloc[index][args.column])

                    if len(original_points) < 2:
                        self.logger.warning(
                            f"Thread-{self.thread_id}: Route for {index} has less than 2 points. Skipping...")
                        continue

                    matching_segments = self._send_request(
                        request_session, original_points)
                    if not matching_segments:
                        self.logger.error(
                            f"Thread-{self.thread_id}: Route for {index} is empty. Skipping...")
                        continue
                    elif len(matching_segments) > 1:
                        # Route between the last point of the previous segment and the first point of the next segment
                        self.logger.info(
                            f"Thread-{self.thread_id}: Matching for {index} has more than one segment. Routing between segments...")
                        map_matched_points = []
                        for i in range(len(matching_segments) - 1):

                            # Add the segment points to the map_matched_points
                            map_matched_points += matching_segments[i]['geometry']['coordinates']

                            # Get the route points between the last point of the previous segment and the first point of the next segment
                            start_point = matching_segments[i]['geometry']['coordinates'][-1]
                            end_point = matching_segments[i +
                                                          1]['geometry']['coordinates'][0]

                            # Send the request to the routing API
                            routing_url = self.api.prepare_routing_url(
                                start_point, end_point)
                            routing_response = self.api.send_request(
                                request_session, routing_url, start_point, end_point)
                            route_points_list = self.api.parse_routing_response(
                                routing_response)

                            if not route_points_list:
                                self.logger.error(
                                    f"Thread-{self.thread_id}: Route between segments for {index} is empty. Just connecting two segments ...")
                                self.logger.debug(
                                    f"Thread-{self.thread_id}: Debug info: {start_point}, {end_point}")
                                self.logger.debug(
                                    f"Thread-{self.thread_id}: Debug info: {routing_url}")
                                self.logger.debug(
                                    f"Thread-{self.thread_id}: Debug info: {routing_response}")
                                map_matched_points += [start_point, end_point]

                            # Add the route points to the map_matched_points (converting from list of tuples to list of lists)
                            map_matched_points += [list(ele)
                                                   for ele in route_points_list]

                        # Add the last segment points to the map_matched_points
                        map_matched_points += matching_segments[-1]['geometry']['coordinates']

                    else:
                        map_matched_points = matching_segments[0]['geometry']['coordinates']

                    self._update_points(index, map_matched_points)
                except Exception as e:
                    self.logger.error(
                        f"Thread-{self.thread_id}: Error while matching route for {index}. Skipping...\n{e}")

        # Close the output file if it is a stream
        if args.stream:
            self.output_file.close()

    def _send_request(self, session, points):
        """
        Send a request to the Map Matching API.
        """
        url = self.api.prepare_matching_url(points)
        response = session.get(url)
        response_json = response.json()
        if response_json['code'] == 'Ok':
            # return matchings list
            return self.api.parse_matching_response(response_json)
        else:
            raise Exception(f'Map Matching Error, Response: {response_json}')

    def _update_points(self, index, points):
        """
        Update the points in the original dataset.
        """
        if args.stream:
            row = self.data.iloc[index]
            row = row.to_frame().T
            row.at[0, args.column] = points
            with StringIO() as string_io:
                row.to_csv(string_io, header=False, index=False)
                string_io.seek(0)
                self.output_file.write(string_io.getvalue())
                # flush the buffer once in a while
            if index %100 == 0:
                self.output_file.flush()
        else:
            self.data.at[index, args.column] = points

    def _write_headers_for_steaming_file(self):
        """
        Write the headers of the csv file for streaming.
        The headers are the same as the original file.
        """
        if args.stream:
            # list of headers
            headers = list(self.data.columns.values)
            # write headers to the file as a csv row, so we can read it later, each value is quoted
            self.output_file.write(
                ",".join(f'"{header}"' for header in headers) + "\n")


def get_split_points(total, num_threads):
    """
    Returns a list of points where to split the data for threading.
    """
    step = (total // int(num_threads)) + 1
    split_points_list = [i for i in range(0, total, step)]

    # Make sure all of the instances included (last step may contain more values)
    if split_points_list[-1] != total:

        # Ranges are like [start,end) so we do not need to add -1 here.
        split_points_list.append(total)

    return split_points_list


# Initialize the OpenStreetAPI and logger
api = OpenStreetAPI(args.base_url)
logger = get_logger("map_match")

# Loading Data file
logger.info("Loading data file...")
data_file = pd.read_csv(args.input_file)

# Split points of the data to threads
logger.info("Splitting data to threads...")
split_points = get_split_points(len(data_file), args.threads)

threads_list = []

# Create threads and append them to the list
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

# Start the threads
logger.info("Starting threads...")
for thread in threads_list:
    thread.start()

# Wait for all threads to finish
logger.info("Waiting for threads to finish...")
for thread in threads_list:
    thread.join()
logger.debug("All threads are finished.")

# Saving the output
logger.info("Saving the output...")
if not args.stream:
    data_file.to_csv(args.output, index=False)

logger.info("Job is done.")
