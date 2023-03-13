import logging
import pandas as pd
import requests
from tqdm import tqdm


def send_get_route_request(base_url, start_point, end_point):
    url = "{}/route/v1/driving/{},{};{},{}?overview=false&steps=true".format(base_url,
                                                                             start_point[0], start_point[1], end_point[0], end_point[1])
    
    response = requests.get(url)
    if response.status_code == 200:
        route = response.json()
        # print(route)
        if route['code'] == 'Ok':
            # get the route
            route = route['routes'][0]['legs']
            extracted_steps = []
            for leg in route:
                for step in leg['steps']:
                    extracted_steps.extend((item['location'][0], item['location'][1])
                                           for item in step['intersections'])  # longitude, latitude
            return extracted_steps
    
    logging.error("Error response from OSRM: {}".format(response.text))
    raise Exception("Unable to get route from {} to {}".format(start_point, end_point))


# trips = pd.read_csv("data/nyc-taxi-trip-duration/train.csv")

# trips['route_points'] = pd.Series(dtype=object)
# print(trips.columns)
# trips['pickup_datetime'] = pd.to_datetime(trips['pickup_datetime'])
# trips['dropoff_datetime'] = pd.to_datetime(trips['dropoff_datetime'])

# for i in tqdm(range(len(trips))):
#     route_points = []
#     route_points.append(
#         (trips.iloc[i]['pickup_longitude'], trips.iloc[i]['pickup_latitude']))
#     route_points.extend(get_route((trips.iloc[i]['pickup_longitude'], trips.iloc[i]['pickup_latitude']), (
#         trips.iloc[i]['dropoff_longitude'], trips.iloc[i]['dropoff_latitude'])))
#     route_points.append(
#         (trips.iloc[i]['dropoff_longitude'], trips.iloc[i]['dropoff_latitude']))
#     trips.at[i, 'route_points'] = route_points
#     print(route_points)
#     if i == 3:
#         break

# trips.to_csv("data/nyc-taxi-trip-duration/train_with_route_points.csv")
