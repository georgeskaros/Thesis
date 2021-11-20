Spectral Decomposition and Sparse Models for Big Data and Robust Data Analytics

Python 3.8 and ProsgreSQL 12.8 used in this analysis.
Code Files 

_________________________________________________________________________________________
data_base.py
In this python file the connection with the DB is established and has the code for:
>the initial expansion of the polyline 
>reconstruction of the tables after pca 
>add to the db the clustering labels  
>finding the rmse of the tables 
_________________
stats.py
In this file:
>Velocity and acceleration are calculated and plotted as histograms.
>Trips are filtered for speed acceleration that are abnormal 
_________________
segmentation.py
In this file:
>segmentation of the data set is done 
>the first instance of each trip is stored so it can be recreated after the analysis 
>a filtering of the trips for too long and too short trips is done 
_________________
pca.py 
In this file:
>performs pca to the dataset provided and save it to separate csv as variance vectors components and the mean value of each column 
_________________
clustering.py 
In this file:
>clusters the compressed data using dbscan 
>Has a function to calculate distances of points with knn in order to help us determine the correct esp value for dbscan 
_________________
helper.py 
>Plots some data points to a map 
_________________
plots.py
>Plots in different images all the clusters presented in the labels that the algorithm used 
_________________



