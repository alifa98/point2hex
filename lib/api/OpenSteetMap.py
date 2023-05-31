from lib.api.APIInterface import API


class OpenStreetAPI(API):
    """
    A class used to interact with the OpenStreetMap API.

    ...

    Attributes
    ----------
    base_url : str
        The base URL of the API.

    Methods
    -------
    prepare_url(start_point, end_point)
        Prepares the URL for the routing API request.
    send_request(session, url, start_point, end_point)
        Sends a GET request to the provided routing URL.
    parse_response(response)
        Parses the response from the routing API request.
    prepare_matching_url(points)
        Prepares the URL for the map matching request.
    parse_matching_response(response_json)
        Parses the response from the map matching request.
    """

    def __init__(self, base_url):
        """
        Constructs the necessary attributes for the OpenStreetAPI object.

        Parameters
        ----------
        base_url : str
            The base URL of the API.
        """
        super().__init__()
        self.base_url = base_url

    def prepare_routing_url(self, start_point, end_point):
        """
        Prepares the URL for the API request.

        Parameters
        ----------
        start_point : tuple
            The longitude and latitude of the start point.
        end_point : tuple
            The longitude and latitude of the end point.
        """
        return "{}/route/v1/driving/{},{};{},{}?overview=false&steps=true".format(self.base_url,
                                                                                  start_point[0], start_point[1],
                                                                                  end_point[0], end_point[1])

    def send_request(self, session, url, start_point, end_point):
        """
        Sends a GET request to the provided URL.

        Parameters
        ----------
        session : requests.Session
            The session in which to send the request.
        url : str
            The URL to which to send the request.
        start_point : tuple
            The longitude and latitude of the start point.
        end_point : tuple
            The longitude and latitude of the end point.
        """
        return session.get(url)

    def parse_routing_response(self, response):
        """
        Parses the response from the API request.

        Parameters
        ----------
        response : requests.Response
            The response from the API request.

        Returns
        -------
        list
            The extracted steps from the response, if the response is valid. Otherwise, None.
        """
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
        """
        Prepares the URL for the map matching request.

        Parameters
        ----------
        points : list
            The list of points for which to get the map matching.

        Returns
        -------
        str
            The URL for the map matching request.
        """
        request_url = self.base_url + '/match/v1/driving/'
        for point in points:
            request_url += str(point[0]) + ',' + str(point[1]) + ';'
        request_url = request_url[:-1]
        request_url += '?overview=full&geometries=geojson'
        return request_url

    def parse_matching_response(self, response_json):
        """
        Parses the response from the map matching request.

        Parameters
        ----------
        response_json : dict
            The JSON response from the map matching request.

        Returns
        -------
        list
            The coordinates of the first route's geometry from the map matching response, 
            if there are any matchings. Otherwise, None.
        """
        # get the first route's geometry coordinates
        if len(response_json['matchings']) == 0:
            return None
            
        return response_json['matchings']
