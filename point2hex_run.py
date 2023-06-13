import os
import argparse
import pandas as pd
from lib.traj2h3 import Points2h3


def main(resolutions_list, input_dir, output_dir, column_name):

    # Function that return a list of files to read in a given folder
    def get_files(direc):
        full_files = []
        for root, dirs, files in os.walk(direc):
            for name in files:
                full_files.append(os.path.join(root, name))

        return full_files

    files_path_list = get_files(input_dir)
    print("Reading in the .csv files...")

    # Read datasets from trajectory route points
    data_list = []
    for file_path in files_path_list:
        data_list.append(pd.read_csv(file_path, encoding='latin1'))

    dataframe = pd.concat(data_list, ignore_index=True)

    # Drop columns that won't be used
    dataframe.dropna(inplace=True, subset=[column_name])

    print("Size of data frame: ", dataframe.shape)

    dataset_processor = Points2h3(dataframe, output_dir, column_name)
    dataset_processor.pre_process()

    for res in resolutions_list:
        dataset_processor.get_hexseq(res)


if __name__ == '__main__':

    # Set up command line argument parsing
    parser = argparse.ArgumentParser(
        description='Generate hexagon sequence from trajectory data')

    # Define the command-line arguments
    parser.add_argument('input_dir', help='Input files directory')
    parser.add_argument('-o', "--output", help='Output directory path (output file name is output_resX.csv)',
                        action='store', default='./')
    parser.add_argument('-r', '--resoluton', type=str, default="6",
                        help='The list of resolutions for generating hexagons')
    parser.add_argument(
        '-c', "--column", help='Route points column name', default='route_points')
    args = parser.parse_args()

    resolutions_list = [int(res.strip())
                        for res in args.resoluton.strip().split(",")]

    main(resolutions_list, args.input_dir, args.output, args.column)
