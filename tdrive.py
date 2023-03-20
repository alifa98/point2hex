import os
import math
import argparse
import pandas as pd

from traj2h3 import Points2h3

parser = argparse.ArgumentParser()
parser.add_argument("--res", type=int, default=7)
args = parser.parse_args()
h3_res = args.res

# hyperparameters
data_path = './data/release/taxi_log_2008_by_id/'
export_fname = 'tdrive'
h3_res = args.res  # hex resolution

# Read T-drive datasets: taxi id, date time, longitude, latitude
# function that return a list of files to read in a given folder
def get_files(direc):
    full_files = []
    for root, dirs, files in os.walk(direc):
        for name in files:
            full_files.append(os.path.join(root, name))
            
    return full_files

full_files = get_files(data_path)  # All folders: 700 MB
print("Reading in the .txt files...")

data = []
for index, file_path in enumerate(full_files):
    data.append(pd.read_csv(file_path, header=None, names = ['taxi_id', 'time', 'long', 'lat'], encoding='latin1'))

data = pd.concat(data, ignore_index=True)

print ("Size of data frame: ", data.shape)
print ("%.1f million rows" % (data.shape[0]/1.0e6))

# Drop duplicates and NAs and long/lat value are out of Beijing 
data.drop_duplicates(inplace=True)
data.dropna(inplace=True)
data = data[(115 <= data['long'].map(math.floor)) & (data['long'].map(math.floor) <= 118)]
data = data[(39 <= data['lat'].map(math.floor)) & (data['lat'].map(math.floor) <= 42)]

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
tdrive_hex_seq = Points2h3(df, h3_res, False, export_fname)
tdrive_hex_seq.get_hexseq()

