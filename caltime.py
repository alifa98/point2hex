import h3
import ast
import argparse
import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

def main(input_fname_ho, output_path, resoluton, n_threads):

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

    # Multithreading for DataFrame
    def parallel_apply(df, func, n_threads=4):
        # Split DataFrame
        df_split = np.array_split(df, n_threads)
        
        # Initialize ThreadPoolExecutor and apply function in parallel
        with ThreadPoolExecutor() as executor:
            df = pd.concat(executor.map(func, df_split))
        
        return df
    
    # Compute time steps for each hexagonal cell
    def caltime(route_points, higher_order_trajectory):
        points_list = ast.literal_eval(route_points)

        # Split the sequence into a list
        sequence_list = higher_order_trajectory.split(" ")
        
        # Get corresponding hexagons for all points
        raw_hex = []
        for lon, lat in points_list:
            hex_cell = h3.latlng_to_cell(lat, lon, int(resoluton)) 
            raw_hex.append(hex_cell)

        # Initialize an empty list to store the final result
        result = []

        # Initialize variables to keep track of the current element and count
        current_element = None
        current_count = 0

        # Iterate through the sequence list and populate the result list
        for element in sequence_list:
            # Count occurrences of the element in raw_data
            count = sum(1 for value in raw_hex if value == element)
            
            if element == current_element:
                # Increment the count of the existing element
                current_count += count
            else:
                # Save the previous element-count pair to the result if it's not the initial element
                if current_element is not None:
                    result.append([current_element, current_count if current_count > 0 else 1])
                
                # Update the current element and count
                current_element = element
                current_count = count

        # Add the last element-count pair to the result
        result.append([current_element, current_count if current_count > 0 else 1])

        return result

    # Wrapper function to apply caltime
    def apply_caltime(df_chunk):
        df_chunk['count'] = df_chunk.apply(lambda row: caltime(row['route_points'], row['higher_order_trajectory']), axis=1)
        return df_chunk

    merged_table = parallel_apply(merged_table, apply_caltime, n_threads=n_threads)
    merged_table.to_csv(output_path + "output_res" +resoluton + ".csv", index=False)


if __name__ == '__main__':

    # Set up command line argument parsing
    parser = argparse.ArgumentParser(
        description='Calculate staytime for each hexagon of a trip')

    # Define the command-line arguments
    parser.add_argument('input_dir', help='Input files directory')
    parser.add_argument('-o', "--output", help='Output directory path (output file name is output_resX.csv)',
                        action='store', default='./output/')
    parser.add_argument('-r', '--resoluton', type=str, default="7",
                        help='The list of resolutions for generating hexagons')
    parser.add_argument('-t', '--threads',
                    help='Number of threads', action='store', default=70)
    args = parser.parse_args()

    main(args.input_dir, args.output, args.resoluton, args.threads)


