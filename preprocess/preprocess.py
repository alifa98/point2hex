import os
import argparse
import pandas as pd

from lib.traj2h3 import Points2h3
from lib.viz import Seqviz

def main(resolution, plot=False):

    # hyperparameters
    data_path = './data/Archive/'
    export_fname = 'nycTaxi'
    h3_res = resolution  # hex resolution

    # Function that return a list of files to read in a given folder
    def get_files(direc):
        full_files = []
        for root, dirs, files in os.walk(direc):
            for name in files:
                full_files.append(os.path.join(root, name))
                
        return full_files

    full_files = get_files(data_path)  
    print("Reading in the .csv files...")

    # Read datasets from trajectory route points
    data = []
    for index, file_path in enumerate(full_files):
        data.append(pd.read_csv(file_path, encoding='latin1'))

    data = pd.concat(data, ignore_index=True)
    print(f'{export_fname} data loaded, resolution is {h3_res}')

    # Drop columns that won't be used
    data = data.loc[:, ['id', 'vendor_id', 'pickup_datetime', 'route_points']] 
    data.rename(columns={'id': 'trip_id', 'vendor_id': 'taxi_id', 'pickup_datetime':'timestamp'}, inplace=True)
    data.dropna(inplace=True)
    print("preprocessing done")
    print ("Size of data frame: ", data.shape)

    export_fname += "_hex" +str(h3_res) + ".csv"
    nyctaxi_hex_seq = Points2h3(data, h3_res, export_fname)
    traj_seq = nyctaxi_hex_seq.get_hexseq()

    # Plot heatmap of all trajectories or sequence map of one trajectory
    if plot:
        viz_seq = Seqviz(traj_seq['trajectory'].tolist(), 'heatmap')   
        viz_seq = Seqviz(traj_seq['trajectory'][1], 'seq')
        viz_seq.show_map()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--res', type=int, default=6, help='the resolution of hexagons')
    args = parser.parse_args()
    main(args.res, False)
