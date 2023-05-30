import threading
import requests
from lib.Utils import get_hex_seq_from_route_points


class GeneratePointsThread(threading.Thread):
    def __init__(self, id, trips, start_index, end_index, api, args, logger):
        threading.Thread.__init__(self)
        self.id = id
        self.trips = trips
        self.start_index = start_index
        self.end_index = end_index
        self.api = api
        self.args = args
        self.logger = logger

    def run(self):
        with requests.Session() as request_session:
            for index in range(self.start_index, self.end_index):
                start_point = (
                    self.trips.iloc[index][self.args.start_column_longitude],
                    self.trips.iloc[index][self.args.start_column_latitude],
                )

                end_point = (
                    self.trips.iloc[index][self.args.end_column_longitude],
                    self.trips.iloc[index][self.args.end_column_latitude],
                )

                route_points = self.send_request(
                    request_session, start_point, end_point
                )
                if not route_points:
                    self.logger.error(
                        f"Thread-{self.id}: route for {index} is empty. Skipping..."
                    )
                    continue
                self.logger.debug(f"Thread-{self.id}: route for {index} retrived.")

                self.update_trip(index, route_points)
                self.logger.debug(
                    f"Thread-{self.id}- route for {index} is saved in memory now"
                )

            if self.args.split:
                self.save_thread_dataframe()
                self.logger.info(
                    f"Thread-{self.id}- Saved its frame in the output file on Disk."
                )

    def send_request(self, session, start_point, end_point):
        """
        Returns list of tuples as a list of points of the route
        """
        url = self.api.prepare_url(start_point, end_point)
        response = None
        try:
            response = self.api.send_request(session, url, start_point, end_point)
        except Exception as e:
            self.logger.error(f"Error in getting route form {start_point} to {end_point}.")
            self.logger.error(e)

        try:
            route_points_list = self.api.parse_response(response)
        except Exception as e:
            self.logger.error(f"Error in parsing response for {start_point} to {end_point}, Response: {response}")
            self.logger.error(e)

        return route_points_list

    def update_trip(self, index, points):
        self.trips.at[index, self.args.output_route] = points

    def save_thread_dataframe(self):
        self.trips[self.start_index : self.end_index].to_csv(
            f"{self.args.output}-{self.id}.csv", index=False
        )
