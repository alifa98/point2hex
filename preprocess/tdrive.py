import os
import argparse
import pandas as pd

from lib.traj2h3 import Points2h3
from lib.viz import Seqviz

def main(resolution, plot=False):

    # hyperparameters
    data_path = './data/release/taxi_log_2008_by_id/'
    export_fname = 'tdrive'
    h3_res = resolution  # hex resolution

    # Beijing's boundry
    Min_lat= 37.45000000
    Max_lat = 41.05000000
    Min_lon = 115.41666667
    Max_lon = 117.50000000

    # Function that return a list of files to read in a given folder
    def get_files(direc):
        full_files = []
        for root, dirs, files in os.walk(direc):
            for name in files:
                full_files.append(os.path.join(root, name))
                
        return full_files

    full_files = get_files(data_path)  # All folders: 700 MB
    print("Reading in the .txt files...")

    # Read T-drive datasets: taxi id, date time, longitude, latitude
    data = []
    for index, file_path in enumerate(full_files):
        data.append(pd.read_csv(file_path, header=None, names = ['taxi_id', 'time', 'long', 'lat'], encoding='latin1'))

    data = pd.concat(data, ignore_index=True)

    print ("Size of data frame: ", data.shape)
    print ("%.1f million rows" % (data.shape[0]/1.0e6))
    print(f'{export_fname} data loaded, resolution is {h3_res}')

    # Drop duplicates and NAs and long/lat value are out of Beijing 
    data.drop_duplicates(inplace=True)
    data.dropna(inplace=True)
    data = data[ (Min_lon <= data['long']) & (data['long'] <= Max_lon) ] 
    data = data[(Min_lat <= data['lat']) & (data['lat'] <= Max_lat)]

    # Convert to pandas datetime type
    data.time = pd.to_datetime(data.time)

    # Create route points column and drop redundant columns
    data['timestamp'] = data['time'].dt.date
    data["route_points"] = list(zip(data.long, data.lat))
    data.reset_index(drop=True)
    data = data.drop(['long', 'lat', 'time'], axis=1)

    # Grouping by taxi id and date, create sequences of route points 
    df = data.groupby(['taxi_id', data['timestamp']], as_index=False)['route_points'].agg(lambda x: list(x))
    df['trip_id'] = df.index

    print ("Size of route_points data frame: ", df.shape)
    print("preprocessing done")

    export_fname += "_hex" +str(h3_res) + ".csv"
    tdrive_hex_seq = Points2h3(df, h3_res, export_fname)
    traj_seq = tdrive_hex_seq.get_hexseq()

    if plot:
        viz_seq = Seqviz(traj_seq['trajectory'].tolist(), 'heatmap')   
        viz_seq = Seqviz(traj_seq['trajectory'][1], 'seq') 
        viz_seq.show_map()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--res', type=int, default=6, help='the resolution of hexagons')
    args = parser.parse_args()
    main(args.res, False)


