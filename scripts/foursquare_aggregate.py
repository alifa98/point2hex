# This is a script to calculate the route between the check-in points of a user in one day in the Foursquare dataset.
import pandas as pd

# INPUT_FILE = "data/foursquare-nyc/TSMC2014_NYC_raw.csv"
# OUTPUT_FILE = "data/foursquare-nyc/TSMC2014_NYC_aggregated_check-ins.csv"

INPUT_FILE = "data/foursquare-tky/TSMC2014_TKY_raw.csv"
OUTPUT_FILE = "data/foursquare-tky/TSMC2014_TKY_aggregated_check-ins.csv"


# read csv file
data_df = pd.read_csv(INPUT_FILE)

# Drop duplicates
data_df.drop_duplicates(inplace=True)

# Drop NAs
data_df.dropna(inplace=True, subset=['longitude', 'latitude'])

# Convert to pandas datetime type + add the offset from UTC (its in minutes)
data_df["datatime"] = pd.to_datetime(pd.to_datetime(data_df.utcTimestamp) + pd.to_timedelta(data_df.timezoneOffset, unit='m'))

# Creating day "date" to use in groupby
data_df['date'] = data_df['datatime'].dt.date

# create the check-in points column to use in aggregation function
data_df["check_ins"] = list(zip(data_df.longitude, data_df.latitude))

# Sort by time ascending bacause we want points to be in the correct order in time (groupby does not change the order)
data_df.sort_values(by=['datatime'], inplace=True)


# aggregate by "user_id" and "date" and create a list of route points
# the aggregating function is a list of tuples of lists in format of (longitude, latitude)
data_df = data_df.groupby(['userId', 'date'], as_index=False)['check_ins'].agg(lambda x: list(x))

# drop the rows that have only one check-in point
data_df = data_df[data_df['check_ins'].map(len) > 1]


# create a trip id for each trip
data_df['trip_id'] = data_df.index

# save the dataframe to a csv file
data_df.to_csv(OUTPUT_FILE, index=False)






