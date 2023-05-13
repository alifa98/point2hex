import argparse

def parse_args():
    """
    Parse command-line arguments for generating route points.

    Returns:
        argparse.Namespace: Parsed arguments.
    """

    # Create an argument parser with the given description
    parser = argparse.ArgumentParser(description='Generate route points')

    # Define the command-line arguments
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
    parser.add_argument('-u', '--base-url',
                        help='Base URL of the routing service [OSRM]', action='store', default="http://127.0.0.1:5000")
    parser.add_argument('-t', '--threads', help='Number of Threads',
                        action='store', default=70)
    parser.add_argument('-s', '--split',
                        help='save output of each thread separately', action='store_true')

    # Parse the command-line arguments and return the parsed values
    return parser.parse_args()
