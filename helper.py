import psycopg2
import numpy as np
import os
import configparser
import pandas as pd
from sklearn.cluster import DBSCAN, KMeans, OPTICS
from sklearn.neighbors import NearestCentroid
import geopandas as gpd
import contextily as ctx
from shapely.geometry import Point
import matplotlib.pyplot as plt


def map_plot(df1, df2 = None, title=None, fontsize=25, color=[None, None], figsize = (15,15), attribution="", **kwargs):

	# Plot one or two dataframes on top of eachother.
	# TODO - Add support for N Dataframes and more parameters, other that figsize.

	df1.crs = {'init': 'epsg:4326'}
	#ax = df1.to_crs('EPSG:3763').plot(figsize=figsize)
	ax = df1.to_crs('EPSG:3763').plot(figsize=figsize, color=color[0], **kwargs)
	if title is not None:
		ax.set_title(title, fontsize=fontsize)
	if df2 is not None:
		df2.crs = {'init': 'epsg:4326'}
		df2.to_crs(epsg=3763).plot(figsize=figsize, color=color[1], ax=ax, **kwargs)
	#ctx.add_basemap(ax)
	ctx.add_basemap(ax, crs=3763, url=ctx.providers.OpenStreetMap.Mapnik)
	ax.margins(0)
	ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
	plt.savefig(r'Path of your choice/' + str(title) + '.png')
	plt.show()

