import os
import argparse
import pandas as pd
from lib.traj2h3 import Points2h3

def main(resolution, data_path, export_fname, column_name):

    # hyperparameters
    data_path = data_path
    export_fname = export_fname
    h3_res = resolution  # hex resolution

    # Function that return a list of files to read in a given folder
    def get_files(direc):
        full_files = []
        for root, dirs, files in os.walk(direc):
            for name in files:
                full_files.append(os.path.join(root, name))
                
        return full_files

    files_path_list = get_files(data_path)  
    print("Reading in the .csv files...")

    # Read datasets from trajectory route points
    data_list = []
    for index, file_path in enumerate(files_path_list):
        data_list.append(pd.read_csv(file_path, encoding='latin1'))

    dataframe = pd.concat(data_list, ignore_index=True)
    print(f'data loaded, resolution is {h3_res}')

    # Drop columns that won't be used
    dataframe.dropna(inplace=True, subset=[column_name])
    print("preprocessing is done")
    print ("Size of data frame: ", dataframe.shape)

    dataset_processor = Points2h3(dataframe, h3_res, export_fname, column_name)
    dataset_processor.get_hexseq()


if __name__ == '__main__':

    # Set up command line argument parsing
    parser = argparse.ArgumentParser(
        description='Generate hexagon sequence from trajectory data')

    # Define the command-line arguments
    parser.add_argument('input_dir', help='Input files directory')
    parser.add_argument('-o', "--output", help='Output file path',
                    action='store', default='output.csv')
    parser.add_argument('-r','--resoluton', type=int, default=6, help='The resolution of hexagons')
    parser.add_argument(
    '-c', "--column", help='Route points column name', default='route_points')
    args = parser.parse_args()


    main(args.resoluton, args.input_dir, args.output, args.column)
