import os
import pandas as pd

files_path_list = []
for root, dirs, files in os.walk("data/t-drive/raw/taxi_log_2008_by_id/"):
    for name in files:
        files_path_list.append(os.path.join(root, name))

# Read T-drive datasets: taxi id, date time, longitude, latitude
data_frames_list = []
for file_path in files_path_list:
    data_frames_list.append(pd.read_csv(file_path, header=None, names = ['taxi_id', 'time', 'long', 'lat'], encoding='latin1'))

# concatenate all data frames into one
data_df = pd.concat(data_frames_list, ignore_index=True)
print ("Size of data frame: ", data_df.shape)



# Beijing's Boundry to filter out points outside of Beijing
Min_lat = 37.45000000
Max_lat = 41.05000000
Min_lon = 115.41666667
Max_lon = 117.50000000

data_df = data_df[(Min_lon <= data_df['long']) &
                  (data_df['long'] <= Max_lon)]
data_df = data_df[(Min_lat <= data_df['lat']) &
                  (data_df['lat'] <= Max_lat)]


# Drop duplicates
data_df.drop_duplicates(inplace=True)

# Drop NAs
data_df.dropna(inplace=True, subset=['long', 'lat'])

# Convert to pandas datetime type
data_df.time = pd.to_datetime(data_df.time)

# Creating "date" to use in groupby
data_df['date'] = data_df['time'].dt.date

# create a column of route points column to use in aggregation function
data_df["route_points"] = list(zip(data_df.long, data_df.lat))

# Sort by time ascending bacause we want points to be in the correct order in time (groupby does not change the order)
data_df.sort_values(by=['time'], inplace=True)

# aggregate by "taxi_id" and "date" and create a list of route points
# the aggregating function is a list of tuples of lists in format of (longitude, latitude)
data_df = data_df.groupby(['taxi_id', 'date'], as_index=False)['route_points'].agg(lambda x: list(x))

# create a trip id for each trip
data_df['trip_id'] = data_df.index

data_df.to_csv('data/t-drive/t-drive_raw-aggregated.csv', index=False)