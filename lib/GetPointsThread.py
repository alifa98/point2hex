import threading
import requests
import logging

class GetRoutePointsTask(threading.Thread):
    def __init__(self,id, trips, start_index, end_index, sem, args):
        threading.Thread.__init__(self)
        self.id = id
        self.trips = trips
        self.start_index = start_index
        self.end_index = end_index
        self.args = args
        self.sem = sem

    def run(self):
        for index in range(self.start_index, self.end_index):
            start_point = (self.trips.iloc[index][self.args.start_column_longitude],
                           self.trips.iloc[index][self.args.start_column_latitude])
            end_point = (self.trips.iloc[index][self.args.end_column_longitude],
                         self.trips.iloc[index][self.args.end_column_latitude])
            way_points = self.send_request(start_point, end_point)
            self.update_trip(index, way_points)
            logging.info("route for {} retrived.".format(index))

        if self.args.split:
            self.trips[self.start_index:self.end_index].to_csv(f"{self.args.output}-{self.id}.csv", index=False)

    def send_request(self, start_point, end_point):

        url = "{}/route/v1/driving/{},{};{},{}?overview=false&steps=true".format(self.args.base_url,
                                                                                 start_point[0], start_point[1], end_point[0], end_point[1])
        response = None
        try:
            self.sem.acquire()
            response = requests.get(url)
        finally:
            self.sem.release()

        if response.status_code == 200:
            route = response.json()
            if route['code'] == 'Ok':
                route = route['routes'][0]['legs']
                extracted_steps = []
                for leg in route:
                    for step in leg['steps']:
                        extracted_steps.extend((item['location'][0], item['location'][1])
                                               for item in step['intersections'])  # longitude, latitude
                return extracted_steps
        logging.error("Error response from OSRM: {}".format(response.text))
        raise Exception("Unable to get route from {} to {}".format(
            start_point, end_point))

    def update_trip(self, index, points):
        self.trips.at[index, self.args.output_column] = points


