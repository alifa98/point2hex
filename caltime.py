import h3
import ast
import argparse
import pandas as pd
from collections import Counter

def main(input_fname_ho, output_path, resoluton):

    # Read porto
    input_fname_raw = "data/train.csv"

    # Converting Files To Pandas Dataframe
    df_raw = pd.read_csv(input_fname_raw)
    df_ho = pd.read_csv(input_fname_ho)

    # Drop columns that won't be used
    df_raw = df_raw.drop(["DAY_TYPE", "CALL_TYPE", "ORIGIN_CALL", "ORIGIN_STAND", "DAY_TYPE", "MISSING_DATA", "TAXI_ID", "TIMESTAMP"], axis=1)
    df_raw.rename(columns={'TRIP_ID': 'trip_id', 'POLYLINE':'route_points'}, inplace=True)
    df_ho = df_ho.drop(["CALL_TYPE", "ORIGIN_CALL", "ORIGIN_STAND", "DAY_TYPE", "MISSING_DATA"], axis=1)
    df_ho.rename(columns={'TRIP_ID': 'trip_id', 'TAXI_ID': 'taxi_id', 'TIMESTAMP':'timestamp'}, inplace=True)
    print("preprocess done")

    # Merge two tables
    merged_table = pd.merge(df_raw, df_ho, how='right', left_on='trip_id', right_on='trip_id')
    print("merge done")
    
    # Compute time step of each cell
    def caltime(route_points, higher_order_trajectory):
        converted_list = ast.literal_eval(route_points)
        
        # Count corresponding hexagons in the raw rount points
        cell_counter = Counter()
        for lon, lat in converted_list:
            hex_cell = h3.latlng_to_cell(lat, lon, int(resoluton)) 
            cell_counter[hex_cell] += 1

        # Initialize an empty list to store the final result
        hex_count = []

        # Split the sequence into a list and iterate through it
        for element in higher_order_trajectory.split(" "):
            count = cell_counter.get(element, 0)  # Get the count from cell_counter or default to 0
            hex_count.append([element, count if count > 0 else 1])  # Use value 1 if the element is not found in cell_counter
        
        return hex_count

    merged_table['count'] = merged_table.apply(lambda row: caltime(row['route_points'], row['higher_order_trajectory']), axis=1)
    merged_table.to_csv(output_path + "output_res" +resoluton + ".csv", index=False)

if __name__ == '__main__':

    # Set up command line argument parsing
    parser = argparse.ArgumentParser(
        description='Calculate staytime for each hexagon of a trip')

    # Define the command-line arguments
    parser.add_argument('input_dir', help='Input files directory') # Read ho file
    parser.add_argument('-o', "--output", help='Output directory path (output file name is output_resX.csv)',
                        action='store', default='./output/')
    parser.add_argument('-r', '--resoluton', type=str, default="7",
                        help='The list of resolutions for generating hexagons')
    args = parser.parse_args()

    main(args.input_dir, args.output, args.resoluton)


