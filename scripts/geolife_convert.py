import pandas as pd

# Loading data
data_df = pd.read_csv('data/geolife/geolife_raw.csv')


# Beijing's Boundry to filter out points outside of Beijing
Min_lat = 37.45000000
Max_lat = 41.05000000
Min_lon = 115.41666667
Max_lon = 117.50000000

data_df = data_df[(Min_lon <= data_df['Longitude']) &
                  (data_df['Longitude'] <= Max_lon)]
data_df = data_df[(Min_lat <= data_df['Latitude']) &
                  (data_df['Latitude'] <= Max_lat)]


# Drop duplicates
data_df.drop_duplicates(inplace=True)

# Drop NAs
data_df.dropna(inplace=True, subset=['Longitude', 'Latitude'])

# Convert to pandas datetime type
data_df.Date_Time = pd.to_datetime(data_df.Date_Time)

# Creating day "date" to use in groupby
data_df['date'] = data_df['Date_Time'].dt.date

# create a column of route points to use in aggregation function
data_df["route_points"] = list(zip(data_df.Longitude, data_df.Latitude))

# Sort by time ascending bacause we want points to be in the correct order in time (groupby does not change the order)
data_df.sort_values(by=['Date_Time'], inplace=True)

# aggregate by "Id_user" and "date" and create a list of route points
# the aggregating function is a list of tuples of lists in format of (longitude, latitude)
data_df = data_df.groupby(['Id_user', 'date'], as_index=False)['route_points'].agg(lambda x: list(x))

# create a trip id for each trip
data_df['trip_id'] = data_df.index

# save the dataframe to a csv file
data_df.to_csv('data/geolife/geolife_aggregated.csv', index=False)