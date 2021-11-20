import pandas as pd
import numpy as np
from shapely.geometry import Point
import geopandas as gpd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, MinMaxScaler, scale
import matplotlib.pyplot as plt
import helper
import time


def doPCA(df, nComp=4, name=None):
    # we get the transpose of a matrix because pca doesn't work sidewayes
    df_tran = df.T
    mean_df_T = np.mean(df_tran, axis=0)
    pca = PCA(n_components=nComp)
    pca.fit(df_tran)

    pca_data = pca.transform(df_tran)
    df_ex_var = np.round(pca.explained_variance_ratio_ * 100, decimals=1)
    labels = ['PC' + str(x) for x in range(1, len(df_ex_var) + 1)]
    # df of the principal components
    pca_df = pd.DataFrame(pca_data, columns=[labels])

    plt.bar(x=range(1, len(df_ex_var) + 1), height=df_ex_var, tick_label=labels)
    plt.ylabel('Percentage of Explained Variance')
    plt.xlabel('Principal Component')
    plt.title('Scree Plot of ' + str(name))
    plt.savefig(r'D:/unipi/THESIS/' + str(name) + 'scree.png')
    plt.show()
    # create a table with explained and cumulative variances
    explained_variance = pca.explained_variance_ratio_
    explained_variance = np.insert(explained_variance, 0, 0)
    cumulative_variance = np.cumsum(np.round(explained_variance, decimals=3))

    pc_df = pd.DataFrame(['PC' + str(x) for x in range(len(df_ex_var) + 1)], columns=['PC'])
    explained_variance_df = pd.DataFrame(explained_variance, columns=['Explained Variance'])
    cumulative_variance_df = pd.DataFrame(cumulative_variance, columns=['Cumulative Variance'])

    all_variance_df = pd.concat([pc_df, explained_variance_df, cumulative_variance_df], axis=1)
    print(all_variance_df)

    components = pd.DataFrame(pca.components_)
    Xhat = np.dot(pca.transform(df_tran)[:, :nComp], pca.components_[:nComp, :])
    Xhat += mean_df_T
    after_pca = pd.DataFrame(Xhat)
    print('Saving DataFrames to CSV')
    # saving vectors , eigenvalues, and the means of the pca
    after_pca.T.to_csv(r'Path of your choice/' + str(name) + '_' + str(nComp) + '.csv', index=False, header=True)
    pca_df.to_csv(r'Path of your choice/' + str(name) + '_' + str(nComp) + '_vectors.csv', index=False, header=True)
    components.to_csv(r'Path of your choice/' + str(name) + '_' + str(nComp) + '_components.csv', index=False, header=True)
    all_variance_df.to_csv(r'Path of your choice/' + str(name) + '_' + str(nComp) + '_variance.csv', index=False, header=True)
    # save mean to csv
    f = open(r'Path of your choice/'+str(name)+'_'+str(nComp)+'_mean.csv','w+')
    for i in range(len(mean_df_T)):
        f.write(str(mean_df_T[i])+'\n')
    f.close()


print('Loading dataframes of latitude longitude...')

# example of usage of the algorithm
lat40 = pd.read_csv(r'Path of your choice/new_lat40.csv')
lon40 = pd.read_csv(r'Path of your choice/new_lon40.csv')

start = time.time()
print('Doing pca for 40 rows...')
doPCA(lon40, 3, 'lon40')
doPCA(lat40, 3, 'lat40')
end = time.time()
print(end-start)

lat50 = pd.read_csv(r'Path of your choice/new_lat50.csv')
lon50 = pd.read_csv(r'Path of your choice/new_lon50.csv')

print('Doing pca for 50 rows...')
doPCA(lon50, 3, 'lon50')
doPCA(lat50, 3, 'lat50')
