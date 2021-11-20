import math
import psycopg2
import psycopg2.extras
import pandas as pd
import ast
import os
import time

def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier


def createSegWithFilter(df, N=10):
    # creates segments for all the trips of the dataset with a fixed step
    # initializing the DataFrames
    lon = pd.DataFrame()
    lat = pd.DataFrame()
    # create table
    sql = "DROP TABLE IF EXISTS BEFORE_PCA_" + str(N) + ";"\
          " CREATE TABLE BEFORE_PCA_" + str(N) + " (ID numeric, TRIP_ID numeric, TIMESTAMP numeric, LATITUDE numeric(16,8), LONGITUDE numeric(16,8));"
    cursor.execute(sql)
    # indicator to name the columns
    columns = 0
    id = 0
    for trip_id in df.trip_id.unique():
        # selecting trip
        trip = df[df["trip_id"] == trip_id]
        trip = trip.reset_index()
        trip = trip.drop('index', axis=1)
        counter = 0
        rest = len(trip) % N

        if rest >= (N/2):
            # have to fill the gap
            end_points = len(trip) + (N - rest)
        else:
            # gap is too big to fill so we discard the rest of the mod
            end_points = len(trip) - rest
        print(columns)
        # make segments depending on the cut
        for j in range(end_points):
            # add the lat, lon to the appropriate data frame
            lat.at[counter, columns] = trip.iloc[j, 3]
            lon.at[counter, columns] = trip.iloc[j, 2]
            temp_trip_id = trip.iloc[j, 0]
            temp_time = trip.iloc[j, 1]
            # inserting into table so i can be able to reconstruct it
            insert = "insert into before_pca_" + str(N) + "(id, trip_id, timestamp, latitude, longitude) VALUES (" + str(id) + " , " + str(temp_trip_id) + " , " + str(temp_time) + " , " + str(trip.iloc[j, 3]) + " , " + str(trip.iloc[j, 2]) + ")"
            cursor.execute(insert)
            counter = counter + 1
            id = id + 1
            # change column it it reached the end
            if counter == N:
                counter = 0
                columns = columns + 1
            if (j + 1 == len(trip)) & (rest != 0):
                remain = N - rest
                for end in range(remain):
                    lat.at[counter, columns] = trip.iloc[j, 3]
                    lon.at[counter, columns] = trip.iloc[j, 2]
                    insert = "insert into before_pca_" + str(N) + "(id, trip_id, timestamp, latitude, longitude) VALUES (" + str(id) + " , " + str(temp_trip_id) + " , " + str(temp_time) + " , " + str(trip.iloc[j, 3]) + " , " + str(trip.iloc[j, 2]) + ")"
                    cursor.execute(insert)
                    counter = counter + 1
                    id = id + 1
                columns = columns + 1
                break

    lon.to_csv(r'Path of your choice/new_lon'+str(N)+'.csv', index=False, header=True)
    lat.to_csv(r'Path of your choice/new_lat'+str(N)+'.csv', index=False, header=True)
    print(lon, lat)


def filterTrips(df, min=10, max=480):
    # Filtering the trips to exclude too small or too long trips
    ps = df.groupby(['trip_id']).count()
    ps = ps.reset_index()
    ps = ps[(ps['longitude'] > min) & (ps['longitude'] < max)]
    df = df[df.trip_id.isin(ps.trip_id)]
    df = df.reset_index()
    df = df.drop('index', axis=1)
    return df


def first_of_trip(df):
    # keeps the firts instance of each trip to have the standard values
    first_of_trip = pd.DataFrame()
    for tr in df.TRIP_ID.unique():
        all_trip = df[df['TRIP_ID'] == tr]
        time = all_trip['TIMESTAMP'].min()
        temp = all_trip[all_trip['TIMESTAMP'] == time]
        temp = temp.dropna(subset=['TRIP_ID', 'CALL_TYPE', 'TAXI_ID','TIMESTAMP','LONGITUDE','LATITUDE'])
        #temp['COUNT'] = int(round_up(len(all_trip), -1))
        temp['COUNT'] = len(all_trip)
        first_of_trip = first_of_trip.append(temp)
    first_of_trip = first_of_trip.reset_index().drop('index', axis=1)
    first_of_trip.to_csv(r'Path of your choice/first_of_trip.csv', index=False, header=True)
    return first_of_trip


print('Connecting with DB...')
con = psycopg2.connect(database="Name of your DB",
                          user="postgres",
                          password="Password",
                          host="localhost",
                          port="5432")
con.autocommit = True
print('Connected')
print('Fetching main table...')
cursor = con.cursor()

traj_sql = "SELECT * FROM preprocessed;"
traj_df = pd.read_sql(traj_sql, con)
print(traj_df)
filtered = filterTrips(traj_df, 20, 480)

start = time.time()
createSegWithFilter(filtered, 50)
end = time.time()
print(end-start)



