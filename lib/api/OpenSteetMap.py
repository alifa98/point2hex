from lib.api.APIInterface import API


class OpenStreetAPI(API):
    def __init__(self, base_url) -> None:
        super().__init__()
        self.base_url = base_url

    def prepare_url(self, start_point, end_point):
        return "{}/route/v1/driving/{},{};{},{}?overview=false&steps=true".format(self.base_url,
                                                                                  start_point[0], start_point[1],
                                                                                  end_point[0], end_point[1])

    def send_requeset(self, session, url, start_point, end_point):
        return session.get(url)

    def parse_response(self, response):
        extracted_steps = None
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

    def prepare_matching_url(self, points):
        request_url = self.base_url + '/match/v1/driving/'
        for point in points:
            request_url += str(point[0]) + ',' + str(point[1]) + ';'
        request_url = request_url[:-1]
        request_url += '?overview=full&geometries=geojson'
        return request_url

    def parse_matching_response(self, response_json):
        # get the first route's geometry coordinates
        if len(response_json['matchings']) == 0:
            return None
        return response_json['matchings'][0]['geometry']['coordinates']
