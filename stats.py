import psycopg2.extras
import pandas as pd
import geopandas as gpd
import numpy as np
from haversine import haversine
from shapely.geometry import Point,Polygon
import time
import matplotlib.pyplot as plt
from matplotlib import style


def calculate_velocity(gdf):
    # Return given dataframe with an extra velocity column that
    # is calculated using the distance covered in a given amount of time.
    # if there is only one point in the trajectory its velocity will be the one measured from the speedometer
    if len(gdf) == 1:
        return gdf

    # create columns for current and next location. Drop the last columns that contains the nan value
    gdf.loc[:, 'current_loc'] = gdf.geom.apply(lambda x: (x.x, x.y))
    gdf.loc[:, 'next_loc'] = gdf.geom.shift(-1)
    gdf.loc[:, 'dt'] = gdf.timestamp.diff(-1).abs()
    gdf = gdf.iloc[:-1]
    gdf.next_loc = gdf.next_loc.apply(lambda x: (x.x, x.y))

    # get the distance traveled in n-miles and multiply by the rate given (3600/secs for knots)
    gdf.loc[:, 'velocity'] = gdf[['current_loc', 'next_loc']].apply(lambda x: haversine(x[0], x[1]), axis=1).multiply(3600 / gdf.dt)
    gdf.drop(['current_loc', 'next_loc', 'dt'], axis=1, inplace=True)
    gdf = gdf.loc[gdf['trip_id'] != 0]
    gdf.dropna(subset=['trip_id', 'geom'], inplace=True)

    return gdf


def calculate_acceleration(gdf):
    # Return given dataframe with an extra acceleration column that
    # is calculated using the rate of change of velocity over time.
    # if there is only one point in the trajectory its acceleration will be zero (i.e. constant speed)
    if len(gdf) == 1:
        gdf.loc[:, 'acceleration'] = 0
        return gdf

    gdf.loc[:, 'acceleration'] = gdf.velocity.diff(-1).divide(gdf.timestamp.diff(-1).abs())
    gdf = gdf.loc[gdf['trip_id'] != 0]
    gdf.dropna(subset=['trip_id', 'geom'], inplace=True)
    gdf.dropna()

    return gdf


def filterTrips(df, min=10, max=480):
    # Filtering the trips to exclude too small or too long trips
    ps = df.groupby(['trip_id']).count()
    ps = ps.reset_index()
    ps = ps[(ps['longitude'] > min) & (ps['longitude'] < max)]
    df = df[df.trip_id.isin(ps.trip_id)]
    df = df.reset_index()
    df = df.drop('index', axis=1)
    return df



print('Connecting with DB...')
con = psycopg2.connect(database="Name of your DB",
                          user="postgres",
                          password="Password",
                          host="localhost",
                          port="5432")
con.autocommit = True
print('Connected')


sql = 'Select * from trip_tuples'
traj_gdf = gpd.GeoDataFrame.from_postgis(sql, con, geom_col="geom")
print('Table fetched')

start = time.time()
calc_velocity = traj_gdf.copy().groupby('trip_id', group_keys=False).apply(lambda gdf: calculate_velocity(gdf))['velocity']
end = time.time()
print(end-start)
traj_gdf.loc[:, 'velocity'] = calc_velocity
print('Velocity calculated ')

start = time.time()
traj_gdf = traj_gdf.groupby('trip_id', group_keys=False).apply(lambda gdf: calculate_acceleration(gdf))
end = time.time()
print(end-start)
print('Acceleration calculated ')

print(traj_gdf)

traj_gdf = traj_gdf[traj_gdf.velocity < 160]
traj_gdf = traj_gdf[traj_gdf.acceleration < 4]
traj_gdf = traj_gdf[traj_gdf.acceleration > -4]

filtered = filterTrips(traj_gdf, 20, 500)
# creating plot for velocity
bins_vel = [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200]
plt.hist(filtered.velocity, bins=bins_vel, edgecolor='black')
plt.title(r'Vessel speed distribution', fontsize=8, y=1)
plt.xlabel(r'speed klm/h', fontsize=8)
plt.ylabel(r'#records', fontsize=8)
plt.axvline(filtered["velocity"].mean(), color='red')
plt.tight_layout()
plt.show()

# creating plot for acceleration
bins_acc = [-4, -3, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 3, 4]
plt.hist(filtered.acceleration, bins=bins_acc, edgecolor='black')
plt.title(r'Vessel acceleration distribution', fontsize=8)
plt.xlabel(r'acceleration (klm/s^2)', fontsize=8)
plt.ylabel(r'#records', fontsize=8)
plt.axvline(filtered["acceleration"].mean(), color='red')
plt.tight_layout()
plt.show()

print(filtered)
filtered.drop(['geom'], axis=1).to_csv(r'Path of your choice/preprossesed.csv', index=False, header=True)