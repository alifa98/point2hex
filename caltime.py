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
    result = pd.merge(df_raw, df_ho, how='right', left_on='trip_id', right_on='trip_id')
    print("merge done")
    
    # Compute staytime percentage of each cell
    def calculate_percentage(route_points, higher_order_trajectory):
        converted_list = ast.literal_eval(route_points)
        higher_order_cells = set(higher_order_trajectory.split(" "))
        cell_counter = Counter()
 
        for lon, lat in converted_list:
            hex_cell = h3.latlng_to_cell(lat, lon, int(resoluton)) 
            if hex_cell in higher_order_cells:
                cell_counter[hex_cell] += 1
                
        total_points = sum(cell_counter.values())
        
        if total_points == 0:
            return {}
        
        percentage_dict = {}
        for cell, count in cell_counter.items():
            percentage_dict[cell] = (count / total_points) * 100
            
        return percentage_dict

    result['percentage'] = result.apply(lambda row: calculate_percentage(row['route_points'], row['higher_order_trajectory']), axis=1)
    result.to_csv(output_path + "output_res" +resoluton + ".csv", index=False)

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
    args = parser.parse_args()

    main(args.input_dir, args.output, args.resoluton)


