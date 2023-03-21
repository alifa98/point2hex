import argparse
import zipfile
import pandas as pd
from traj2h3 import Points2h3

parser = argparse.ArgumentParser()
parser.add_argument("--res", type=int, default=7)
args = parser.parse_args()

# hyperparameters
input_path = 'data/taxi_february.txt.zip'
input_fname = "taxi_february.txt"
export_fname = 'roma'
h3_res = args.res # hex resolution

# Roma's boundry
Min_lat= 41.793710
Max_lat = 41.991390
Min_lon = 12.372598
Max_lon = 12.622537

# Loading data
zip_file = zipfile.ZipFile(input_path)

# Converting Files To Pandas Dataframe
data = pd.read_csv(zip_file.open(input_fname), sep=";", header = None)
data.columns = ["taxi_id", "time", "position"]
print(data.shape)
print("data loaded")

# Convert to pandas datetime type
data.time = pd.to_datetime(data.time)

def get_long(row):
    points = row[6:-1].split()
    long = float(points[1])
    return long

def get_lat(row):
    points = row[6:-1].split()
    lat = float(points[0])
    return lat

data['long'] = data['position'].apply(lambda x: get_long(x))
data['lat'] = data['position'].apply(lambda x: get_lat(x))

# Drop duplicates and NAs and long/lat value are out of Beijing 
data.drop_duplicates(inplace=True)
data.dropna(inplace=True)
data = data[ (Min_lon <= data['long']) & (data['long'] <= Max_lon) ] 
data = data[(Min_lat <= data['lat']) & (data['lat'] <= Max_lat)]

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
print("*"*100)
