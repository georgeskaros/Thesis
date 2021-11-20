import psycopg2.extras
import pandas as pd
import geopandas as gpd
import helper
from shapely.geometry import Point


def plot_clusters(cut_column, min_samples, eps, cut):
    # plots in separate images all the clusters
    # fetches the data and the labels and joins them
    sql1 = 'select * from ' + cut_column + '_' + min_samples + '_' + eps
    labels = pd.read_sql(sql1, con)

    sql2 = 'select * from before_pca_' + str(cut)
    df2 = pd.read_sql(sql2, con)

    df2['geom'] = df2[['longitude', 'latitude']].apply(lambda x: Point(x[0], x[1]), axis=1)
    gdf = gpd.GeoDataFrame(df2, geometry='geom', crs='EPSG:4326')

    joinData = pd.concat([gdf, labels['labels']], axis=1, sort=False)
    # for each of the labels prints the cluster
    for i in range(-1, joinData.labels.max().astype(int) + 1, 1):
        tempDF = joinData.loc[joinData.iloc[:, 6] == i].copy()
        print('Plotting clusters of , cluster id ' + str(i))
        helper.map_plot(tempDF, figsize=(12, 8), fontsize=1, title=cut_column + '_' + min_samples + '_' + eps + '_' + str(i))


print('Connecting with DB...')
con = psycopg2.connect(database="Name of your DB",
                          user="postgres",
                          password="Password",
                          host="localhost",
                          port="5432")
con.autocommit = True
print('Connected')

plot_clusters('full_lon40_db', '20', '3_e08', 40)
plot_clusters('full_lat40_db', '20', '725_e12', 40)




