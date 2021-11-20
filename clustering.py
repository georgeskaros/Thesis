import time
import pandas as pd
import geopandas as gpd
import numpy as np
import psycopg2.extras
from sklearn import preprocessing
from sklearn.cluster import DBSCAN, KMeans, OPTICS
from sklearn.neighbors import NearestNeighbors
from sklearn.neighbors import NearestCentroid
from matplotlib import pyplot as plt
import helper
from shapely.geometry import Point


def do_dbscan(data, name, eps=0.003, min_samples=40, scale=False):
    # performs clustering using dbscan to the transposed table , has option to scale the data
    if scale:
        X = preprocessing.scale(data)
    else:
        X = data
    print("Starting dbscan for " + name)
    db = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine').fit(X)
    set(db.labels_)
    print(db.labels_.T)
    print(f'We have {len(np.unique(db.labels_))} : {np.unique(db.labels_)} clusters ')
    labels = pd.DataFrame(db.labels_.T)
    labels.to_csv(r'Path of your choice' + str(name) + '_samples_' + str(min_samples) + '_eps_' + str(eps) + '_DBSCAN_labels.csv', index=False, header=True)


def find_distance(X):
    # calculating the distance between neighbors to find the average
    # used to find the esp for DBSCAN
    neigh = NearestNeighbors(n_neighbors=2, metric='cosine')
    nbrs = neigh.fit(X)
    distances, indices = nbrs.kneighbors(X)

    # plotting distances
    distances = np.sort(distances, axis=0)
    distances = distances[:, 1]
    plt.plot(distances)
    plt.ylabel('distance')
    plt.xlabel('number of points')
    plt.title('Distance of two vehicles')
    plt.show()


lon40 = pd.read_csv(r'Path of your choice/new_lon40.csv')
lat40 = pd.read_csv(r'Path of your choice/new_lat40.csv')

lon40_T = lon40.T
lat40_T = lat40.T

print(lat40_T, lon40_T)
find_distance(lat40_T)
find_distance(lon40_T)

start = time.time()
do_dbscan(lat40_T, 'full_lat40', eps=0.000000000725, min_samples=20)
do_dbscan(lon40_T, 'full_lon40', eps=0.00000003, min_samples=20)
end = time.time()
print('time of original')
print(end - start)



