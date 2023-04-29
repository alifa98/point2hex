import argparse
import zipfile
import pandas as pd

from lib.traj2h3 import Points2h3
from lib.viz import Seqviz

def main(resolution, plot=False):

    # hyperparameters
    input_path = 'data/geolife.csv.zip'
    input_fname = "geolife.csv"
    export_fname = 'geolife'
    h3_res = resolution # hex resolution

    # Beijing's boundry
    Min_lat= 37.45000000
    Max_lat = 41.05000000
    Min_lon = 115.41666667
    Max_lon = 117.50000000

    # Loading data
    zip_file = zipfile.ZipFile(input_path)

    # Converting Files To Pandas Dataframe
    data = pd.read_csv(zip_file.open(input_fname))
    print(data.shape)
    print(f'{export_fname} data loaded, resolution is {h3_res}')

    # Drop duplicates and NAs and long/lat value are out of Beijing 
    data.drop_duplicates(inplace=True)
    data.dropna(inplace=True)
    data = data[ (Min_lon <= data['Longitude']) & (data['Longitude'] <= Max_lon) ] 
    data = data[(Min_lat <= data['Latitude']) & (data['Latitude'] <= Max_lat)]

    # Convert to pandas datetime type
    data.Date_Time = pd.to_datetime(data.Date_Time)

    # Create route points column and drop redundant columns
    data['timestamp'] = data['Date_Time'].dt.date
    data["route_points"] = list(zip(data.Longitude, data.Latitude))
    data.reset_index(drop=True)
    data = data.drop(['Longitude', 'Latitude', 'Date_Time', 'Altitude', 'Id_perc', 'Label'], axis=1)
    data.rename(columns={'Id_user': 'user_id'}, inplace=True)

    # Grouping by taxi id and date, create sequences of route points 
    df = data.groupby(['user_id', data['timestamp']], as_index=False)['route_points'].agg(lambda x: list(x))
    df['trip_id'] = df.index

    print ("Size of route_points data frame: ", df.shape)
    print("preprocessing done")

    export_fname += "_hex" +str(h3_res) + ".csv"
    geolife_hex_seq = Points2h3(df, h3_res, export_fname)
    traj_seq = geolife_hex_seq.get_hexseq()
    print("*"*100)

    if plot:
        viz_seq = Seqviz(traj_seq['trajectory'].tolist(), 'heatmap')   
        viz_seq = Seqviz(traj_seq['trajectory'][1], 'seq') 
        viz_seq.show_map()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--res', type=int, default=6, help='the resolution of hexagons')
    args = parser.parse_args()
    main(args.res, False)

#credit: https://medium.com/analytics-vidhya/data-mining-of-geolife-dataset-560594728538
