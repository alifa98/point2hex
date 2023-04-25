import threading
import requests
import logging
from lib.Utils import get_hex_seq_from_route_points


class GeneratePointsThread(threading.Thread):
    def __init__(self, id, trips, start_index, end_index, sem, api, args):
        threading.Thread.__init__(self)
        self.id = id
        self.trips = trips
        self.start_index = start_index
        self.end_index = end_index
        self.sem = sem
        self.api = api
        self.args = args

    def run(self):
        with requests.Session() as request_session:

            for index in range(self.start_index, self.end_index):

                start_point = (self.trips.iloc[index][self.args.start_column_longitude],
                               self.trips.iloc[index][self.args.start_column_latitude])

                end_point = (self.trips.iloc[index][self.args.end_column_longitude],
                             self.trips.iloc[index][self.args.end_column_latitude])

                route_points = self.send_request(
                    request_session, start_point, end_point)
                logging.debug(f"Thread-{self.id}: route for {index} retrived.")

                hex_sequence = None
                if not self.args.hex_save_off:
                    hex_sequence = get_hex_seq_from_route_points(route_points)

                logging.debug(
                    f"Thread-{self.id}- route for {index}- Points: {route_points}")

                if not self.args.hex_save_off:
                    logging.debug(
                        f"Thread-{self.id}- route for {index}- hexs: {hex_sequence}")

                self.update_trip(index, route_points, hex_sequence)
                logging.debug(
                    f"Thread-{self.id}- route for {index} is saved in memory now")

            if self.args.split:
                self.save_thread_dataframe()
                logging.info(
                    f"Thread-{self.id}- Saved its frame in the output file on Disk.")

    def send_request(self, session, start_point, end_point):
        """
        Returns list of tuples as a list of points of the route
        """
        url = self.api.prepare_url(start_point, end_point)
        response = None
        try:
            self.sem.acquire()
            response = self.api.send_requeset(
                session, url, start_point, end_point)
        except Exception as e:
            logging.error(
                f"Error in getting route form {start_point} to {end_point}.")
            logging.error(e)
        finally:
            self.sem.release()

        route_points_list = self.api.parse_response(response)
        if not route_points_list:
            logging.error(
                f"Error in getting route form {start_point} to {end_point}. Empty response.")

        return route_points_list

    def update_trip(self, index, points, hexs):

        if not self.args.point_save_off:
            self.trips.at[index, self.args.output_route] = points

        if not self.args.hex_save_off:
            self.trips.at[index, self.args.output_hexagone] = hexs

    def save_thread_dataframe(self):
        self.trips[self.start_index:self.end_index].to_csv(
            f"{self.args.output}-{self.id}.csv", index=False)
