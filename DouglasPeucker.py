import numpy as np
from rdp import rdp
import numpy
import pandas as pd
from sklearn.metrics import mean_squared_error
import math

def rmse(pre, post):
    # calculate root mean square error with an input of 2 dataframes with columns 'latitude', 'longitude'
    lat_mse = mean_squared_error(pre['latitude'],post['latitude'])
    lon_mse = mean_squared_error(pre['longitude'],post['longitude'])

    lat_rmse = math.sqrt(lat_mse)
    lon_rmse = math.sqrt(lon_mse)
    added_rmse = lon_rmse + lat_rmse
    return added_rmse


def calculateRDP(df):
    # takes a input a data frame,for each trip that it has is compresses it via rdp an saves an copy of the compressed
    # with the remaining values filled with the last value, this happens in order to be able to compare it to the original with rmse
    # a copy of the compressed is saved as well to be able to compare the compression ratio
    # df columns: trip_id,(that indicates the id of the trip), latitude , longitude
    lat_lon = pd.DataFrame(columns=('latitude', 'longitude'))
    for trip_id in df.trip_id.unique():
        trip = df[df["trip_id"] == trip_id]
        trip = trip.reset_index()
        trip = trip.drop('index', axis=1)
        compressed = pd.DataFrame(rdp(trip[["latitude", "longitude"]], epsilon=0.0001),
                                  columns=('latitude', 'longitude'))
        lat_lon = lat_lon.append(compressed)
        # print(len(trip)-len(compressed)) #!!!!!!
        if len(trip) > len(compressed):
            for i in range(len(trip) - len(compressed)):
                compressed.loc[len(compressed) + i] = compressed.iloc[len(compressed) - 1]
                counter = counter + 1
        rmse_score = rmse_score + rmse(trip[["latitude", "longitude"]], compressed[["latitude", "longitude"]])
        print(progress)
        progress = progress + 1
        del compressed

    print("saving to csv")
    lat_lon.to_csv(r'Path of your choice\DouglasPeucker_epsilon=0.0001.csv', index=False, header=True)
    print("that many points were subtracted: " + str(counter))
    print("added rmse is: " + str(rmse_score))


traj = pd.read_csv(r'Path of your choice\preprossesed.csv')
counter = 0
rmse_score = 0
progress = 0






