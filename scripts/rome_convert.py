import argparse
import zipfile
import pandas as pd


# Loading data
data_df = pd.read_csv('data/rome/taxi_february.txt', header=None,names= ["taxi_id", "time", "position"], sep=";")

#convert the position to long and lat columns (format is POINT(long lat))
data_df['long'] = data_df['position'].apply(lambda x: float(x.strip()[6:-1].split()[1]))
data_df['lat'] = data_df['position'].apply(lambda x: float(x.strip()[6:-1].split()[0]))

# Rome's Boundry to filter out points outside of Beijing
Min_lat = 41.76
Max_lat = 42.05
Min_lon = 12.372598
Max_lon = 12.622537

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

# Creating day "date" to use in groupby
data_df['date'] = data_df['time'].dt.date

# create a column of route points column to use in aggregation function
data_df["route_points"] = list(zip(data_df.long, data_df.lat))

# Sort by time ascending bacause we want points to be in the correct order in time (groupby does not change the order)
data_df.sort_values(by=['time'], inplace=True)

# aggregate by "Id_user" and "date" and create a list of route points
# the aggregating function is a list of tuples of lists in format of (longitude, latitude)
data_df = data_df.groupby(['taxi_id', 'date'], as_index=False)['route_points'].agg(lambda x: list(x))

# create a trip id for each trip
data_df['trip_id'] = data_df.index

# save the dataframe to a csv file
data_df.to_csv('data/rome/rome_taxi_aggregated.csv', index=False)