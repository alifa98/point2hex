class API(object):
    def prepare_url(self, start_point, end_point):
        """
        This mehtod prepares a url to send the request
        """
        pass

    def send_requeset(self, url, start_point, end_point):
        """
        this method sends request to the API then returns the response
        """
        pass

    def parse_response(self, response):
        """
        This method parses the output of the sen_request() method and returns list of tuples (list of points)
        """
        pass
        