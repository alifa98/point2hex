import os
import wget
import zipfile
import pandas as pd

from traj2h3 import Points2h3
from viz import Seqviz

# hyperparameters
url = 'https://archive.ics.uci.edu/ml/machine-learning-databases/00339/train.csv.zip'
download_dst = 'data/'
input_path = 'data/train.csv.zip'
input_fname = "train.csv"
export_fname = 'porto'
h3_res = 9  # hex resolution

# Check if data directory exits
if not os.path.exists("./data/"):
    os.makedirs('./data/') 

# Download porto taxi dataset
filename = wget.download(url, out=download_dst)

# Loading data
# Unzipfile
zip_file = zipfile.ZipFile(input_path)

# Converting Files To Pandas Dataframe
df = pd.read_csv(zip_file.open(input_fname))
print(df.info())
print("data loaded")

# Drop columns that won't be used
df = df.drop(["DAY_TYPE", "CALL_TYPE", "ORIGIN_CALL", "ORIGIN_STAND", "DAY_TYPE", "MISSING_DATA"], axis=1)
df.rename(columns={'TRIP_ID': 'trip_id', 'TAXI_ID': 'taxi_id', 'POLYLINE':'route_points', 'TIMESTAMP':'timestamp'}, inplace=True)
print("preprocessing done")

export_fname += "_hex" +str(h3_res) + ".csv"
porto_hex_seq = Points2h3(df, h3_res, True, export_fname)
traj_seq = porto_hex_seq.get_hexseq()

# Plot heatmap of all trajectories or sequence map of one trajectory
viz_seq = Seqviz(traj_seq['trajectory'].tolist(), 'heatmap')   
# viz_seq = Seqviz(traj_seq['trajectory'][1], 'seq')
viz_seq.show_map()


