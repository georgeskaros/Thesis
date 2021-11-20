import psycopg2
import psycopg2.extras
import pandas as pd
import ast
import os
from sklearn.metrics import mean_squared_error
import math
import time


def extend_polyline(table_name):
    # create the expanded trips from poly trips and inserts them to a data base
    print('Fetching main table...')
    traj_sql = "SELECT * FROM " + str(table_name) + " ;"
    traj_df = pd.read_sql(traj_sql, con)
    cursor = con.cursor()
    cursor.execute('DELETE FROM TRIP_TUPLES')
    for trip in range(len(traj_df)):
        trip_id = traj_df.iloc[trip]['trip_id']
        poly = ast.literal_eval(traj_df.iloc[trip]['polyline'])
        print(trip)
        for tpl in range(len(poly)):
            times = traj_df.iloc[trip]['timestamp'] + (15 * tpl)
            lon = poly[tpl][0]
            lat = poly[tpl][1]
            cmd = "insert into trip_tuples(trip_id, timestamp, longitude, latitude) VALUES (" + trip_id + " , " + str(
                times) + " , " + str(lon) + " , " + str(lat) + ")"
            cursor.execute(cmd)


def reconstructToDB(lat, lon, N):
    # reconstructs a table from 2 segmented tables lat and lon with segment length N
    cursor = con.cursor()
    sql = "DROP TABLE IF EXISTS AFTER_PCA_" + str(N) + ";" \
          " CREATE TABLE AFTER_PCA_" + str(N) + " (ID numeric, LATITUDE numeric(16,8), LONGITUDE numeric(16,8));"
    cursor.execute(sql)
    id = 0
    for col in range(len(lat.columns)):
        print(col)
        for row in range(len(lat)):
            temp_lon = lon.iloc[row][col]
            temp_lat = lat.iloc[row][col]

            cmd = "insert into after_pca_" + str(N) + "(id, longitude, latitude) VALUES (" + str(id) + " , " + str(
                temp_lon) + " , " + str(temp_lat) + " )"
            # print(cmd)
            cursor.execute(cmd)
            id = id + 1

    print(len(lat.columns), len(lon))


def rmse(pre, post):
    # calculates root mean square error for a dataframe with columns named latitude and longitude
    lat_mse = mean_squared_error(pre['latitude'], post['latitude'])
    lon_mse = mean_squared_error(pre['longitude'], post['longitude'])
    # after calculating separately the rmse for each column and adds them together
    lat_rmse = math.sqrt(lat_mse)
    lon_rmse = math.sqrt(lon_mse)
    added_rmse = lon_rmse + lat_rmse
    print(added_rmse)
    return added_rmse


def add_labels(N, lbl, text):
    # inserts the labels of clustering to a database table
    cursor = con.cursor()
    sql = "DROP TABLE IF EXISTS " + text + " ;" \
          " CREATE TABLE " + text + "  (id numeric, labels numeric);"
    cursor.execute(sql)
    id = 0
    for label in range(len(lbl)):
        for cut in range(N):
            tmplbl = lbl.iloc[label,0]
            cmd = 'insert into ' + text + ' (id , labels) values(' + str(id) + ' , ' + str(tmplbl) + ');'
            cursor.execute(cmd)
            id = id + 1


def find_rmse(N):
    # calculating rmse from 2 tables of a db with the same segmentation length 
    # inserts them to a db
    sql_prePCA = "SELECT * FROM BEFORE_PCA_" + str(N) + ";"
    sql_postPCA = "SELECT * FROM AFTER_PCA_" + str(N) + ";"
    prePCA = pd.read_sql(sql_prePCA, con)
    postPCA = pd.read_sql(sql_postPCA, con)
    print(prePCA)
    score = rmse(prePCA, postPCA)
    cursor = con.cursor()
    rmsesql = "insert into rmse(id, rmse) VALUES (" + str(N) +"_all" + " , " + str(score) + ") "
    cursor.execute(rmsesql)


print('Connecting with DB...')
con = psycopg2.connect(database="Name of your DB",
                          user="postgres",
                          password="Password",
                          host="localhost",
                          port="5432")
con.autocommit = True
print('Connected')


dblon = pd.read_csv(r'Path of your choice/full_lon40_samples_20_eps_3e-08_DBSCAN_labels.csv')
dblat = pd.read_csv(r'Path of your choice/full_lat40_samples_20_eps_7.25e-10_DBSCAN_labels.csv')

start = time.time()
add_labels(40, dblon, 'full_lon40_db_20_3_e08')
end = time.time()
print(end-start)

start = time.time()
add_labels(40, dblat, 'full_lat40_db_20_725_e12')
end = time.time()
print(end-start)




