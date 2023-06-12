
import json
import pandas as pd
import threading
import requests
import logging

# INPUT_FILE = "data/foursquare-nyc/TSMC2014_NYC_aggregated_check-ins.csv"
# OUTPUT_FILE = "data/foursquare-nyc/TSMC2014_NYC_routed.csv"

NUMB_THREADS = 70

INPUT_FILE = "data/foursquare-tky/TSMC2014_TKY_aggregated_check-ins.csv"
OUTPUT_FILE = "data/foursquare-tky/TSMC2014_TKY_routed.csv"

logger = logging.getLogger("foursquare_route")

# read csv file
data_df = pd.read_csv(INPUT_FILE)


class RoutingThread(threading.Thread):

    def __init__(self, thread_id, start_index, end_index, data_df):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.start_index = start_index
        self.end_index = end_index
        self.data_df = data_df
        self.url = "http://127.0.0.1:5000/route/v1/driving/"
    
    def run(self):
        with requests.Session() as request_session:
            for index in range(self.start_index, self.end_index):
                try:
                    original_points = eval(self.data_df.iloc[index]['check_ins'])
                    route_points = self._send_request(
                        request_session, original_points)
                    if not route_points:
                        logger.error(
                            f"Thread-{self.thread_id}: Route for {index} is empty. Skipping...")
                        continue
                    self._update_points(index, route_points)
                except Exception as e:
                    logger.error(
                        f"Thread-{self.thread_id}: Error while routing route for {index}. Skipping...\n{e}")
    
    def _send_request(self, session, original_points):
        """
        Returns list of tuples as a list of points of the route
        """
        coordinates_str = ";".join([f"{lon},{lat}" for lon, lat in original_points])
        request_url = f"{self.url}{coordinates_str}?geometries=geojson"

        response = session.get(request_url)
        if response.status_code == 200:
            data = json.loads(response.text)
            if 'routes' in data:
                route = data['routes'][0]
                if 'geometry' in route:
                    geometry = route['geometry']
                    return geometry['coordinates']
                
        return None
                    
    def _update_points(self, index, route_points):
        self.data_df.at[index, 'route_points'] = str(route_points)

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
    if split_points_list[-1] != total:

        # Ranges are like [start,end) so we do not need to add -1 here.
        split_points_list.append(total)

    return split_points_list


split_points = get_split_points(len(data_df), NUMB_THREADS)

threads_list = []

# Create threads and append them to the list
logger.info("Creating threads...")
for i in range(len(split_points) - 1):
    threads_list.append(
        RoutingThread(
            i,
            split_points[i],
            split_points[i + 1],
            data_df
        )
    )

# Start the threads
print("Starting threads...")
for thread in threads_list:
    thread.start()

# Wait for all threads to finish
logger.info("Waiting for threads to finish...")
for thread in threads_list:
    thread.join()
logger.debug("All threads are finished.")

# Saving the output
data_df.to_csv(OUTPUT_FILE, index=False)

logger.info("Job is done.")