import argparse

def parse_args_default_with_config(config):
    parser = argparse.ArgumentParser(description='Generate route points')

    # loc 2 point
    parser.add_argument('input_file', help='Input file path')

    parser.add_argument('-o', "--output", help='Output file',
                        action='store', default='output.csv')
    parser.add_argument('-slon', '--start-column-longitude', help='Start point column name (longitude)',
                        action='store', default='start_point_lon')
    parser.add_argument('-slat', '--start-column-latitude', help='Start point column name (latitude)',
                        action='store', default='start_point_lat')
    parser.add_argument('-elon', '--end-column-longitude', help='End point column name (longitude)',
                        action='store', default='end_point_lon')
    parser.add_argument('-elat', '--end-column-latitude', help='End point column name (latitude)',
                        action='store', default='end_point_lat')
    parser.add_argument('-or', '--output-route', help='Route column name in the output file',
                        action='store', default='route_points')
    parser.add_argument('-ps', '--point-save-off',
                        help='points will not be saved as a column', action='store_true')
    parser.add_argument('-u', '--base-url',
                        help='Base URL of the routing service [OSRM]', action='store', default=config("default_routing_api_base_url"))
    parser.add_argument('-t', '--threads', help='Number of Threads',
                        action='store', default=config('default_concurrent_requests'))
    parser.add_argument('-cr', '--concurrent-requests',
                        help='number of concurrent requests to the OSRM API', action='store', default=10)
    parser.add_argument('-mt', '--max-try', help='Max retries',
                        action='store', default=config('default_max_retries'))
    parser.add_argument('-d', '--delay', help='Retry delay (ms)',
                        action='store', default=config('default_retry_delay'))
    parser.add_argument('-T', '--timeout',
                        help='Timeout for each request (ms)', action='store', default=config('default_timeout'))
    parser.add_argument('-S', '--split',
                        help='Output of each thread separately', action='store_true')

    # points 2 Hexagons
    parser.add_argument('-r', '--resolution',
                        help='Resolution of the hexagon grid', default=9)
    parser.add_argument('-ox', '--output-hexagone',
                        help='Hexagone sequence column name in the output file', default='hex_sequence')

    return parser.parse_args()