# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 10:21:06 2025

@author: michael.tu
"""

#%%
import pandas as pd
from geopy.distance import geodesic
import geopandas as gpd
from shapely.geometry import Point
from shapely import wkt
import os
import numpy as np

stations = pd.read_csv(r"\\owg.ds.corp\serverfarm\KnowledgeBase\Health\0-Training\2024\New Hire Orientation\Work\MT\P Projects\2nd Ave Extension\MTA_Subway_Stations.csv")
stations['geometry'] = stations['geometry'].apply(wkt.loads)
#stations = stations
#%%
geo_stations = gpd.GeoDataFrame(stations,crs = 'EPSG:4326',geometry = 'geometry')
geo_stations.plot()
other_m = geo_stations[(geo_stations['Station ID'].isin([396, 397, 398, 399, 223, 7, 400]))]
second_ave = geo_stations[geo_stations['Station ID'].isin([475,476,477])]

#%%
ues_repeat_sales = pd.read_excel(r"\\owg.ds.corp\serverfarm\KnowledgeBase\Health\0-Training\2024\New Hire Orientation\Work\MT\P Projects\2nd Ave Extension\repeat_sales_ues_cleaned_w_appreciation_coords.xlsx")
ues_repeat_sales = gpd.GeoDataFrame(ues_repeat_sales,
                                    geometry = gpd.points_from_xy(ues_repeat_sales['longitude'],ues_repeat_sales['latitude']), crs="EPSG:4326")

#%%
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm

# Define the colors for your ranges
colors = ['#b30000',
          '#ff0000',
          '#ff8080',   
          '#FFFFFF',  
          '#99ffbb', 
          '#00e600', 
          '#008000'
          
          ]  

# Create a colormap
cat_cmap = ListedColormap(colors)

# Define the boundaries for your categories
# -inf to -5, -4 to -2, -1, 0, 1, 2 to 4, 5 to inf 
cat_boundaries = [0, .75,1, 1.25, 1.5, 1.75,2,100]

# Create a norm for the colormap
cat_norm = BoundaryNorm(cat_boundaries, cat_cmap.N, clip=True)

#%% interactive map
import folium
root = r"\\owg.ds.corp\serverfarm\KnowledgeBase\Health\0-Training\2024\New Hire Orientation\Work\MT\P Projects\2nd Ave Extension"
os.chdir(root)
ues_repeat_sales
cat_labels= ['< .75', '.75 - 1', '1 - 1.25', '1.25 - 1.5', '1.5 - 1.75', '1.75 - 2', '2+']
#the second ave subway
second_ave_subway = second_ave.explore(color = 'purple',
                                       tiles = 'CartoDB positron',
                                       marker_kwds = {'radius':5,
                                                      'icon':folium.Icon(icon = 'train')})

other_subway = other_m.explore(color = 'blue',
                                       tiles = 'CartoDB positron',
                                       marker_kwds = {'radius':5,
                                                      'icon':folium.Icon(icon = 'train')},
                                       m = second_ave_subway)

ues_repeat_sales['appr_bin'] = pd.cut(ues_repeat_sales['appr_3'],bins = cat_boundaries,labels = cat_labels)
ues_repeat_sales.explore(column = 'appr_bin',
                         tiles = "CartoDB positron",
                         cmap = cat_cmap,
                         categorical = True,
                         m = other_subway).save('test.html')
#%% getting closest subway station both overall and in other
from geopy.distance import geodesic

#closest second ave
closest_second = pd.merge(second_ave[['Stop Name','geometry']].to_crs('EPSG:3857'),ues_repeat_sales[['block_lot_num','sale_date_1','geometry']].to_crs('EPSG:3857'),
              suffixes = ['_1','_2'],how = 'cross')

closest_second['distance'] = closest_second.geometry_1.distance(closest_second.geometry_2)

closest_second = closest_second.sort_values(by = 'distance')
closest_second['distance'] = closest_second['distance'] / 1609.34
closest_second = closest_second.drop_duplicates(subset = ['block_lot_num','sale_date_1']).rename(columns = {'Stop Name':'closest_second',
                                                                                                            'distance':'distance_second'})

#closest other
closest_other = pd.merge(other_m[['Stop Name','geometry']].to_crs('EPSG:3857'),ues_repeat_sales[['block_lot_num','sale_date_1','geometry']].to_crs('EPSG:3857'),
              suffixes = ['_1','_2'],how = 'cross')

closest_other['distance'] = closest_other.geometry_1.distance(closest_other.geometry_2)
closest_other['distance'] = closest_other['distance'] / 1609.34

closest_other = closest_other.sort_values(by = 'distance')
closest_other = closest_other.drop_duplicates(subset = ['block_lot_num','sale_date_1']).rename(columns = {'Stop Name':'closest_other',
                                                                                                           'distance':'distance_other'})
#merging
closest_subways = pd.merge(closest_other[['closest_other','distance_other','block_lot_num','sale_date_1']],
                           closest_second[['closest_second','distance_second','block_lot_num','sale_date_1']], on = ['block_lot_num','sale_date_1'],
                           how = 'inner')

#%% merging
ues_repeat_sales_closest_subway = pd.merge(ues_repeat_sales,closest_subways,on = ['block_lot_num','sale_date_1'],
                                           how = 'left')

#flags for closest
ues_repeat_sales_closest_subway['72nd'] = np.where(ues_repeat_sales_closest_subway['closest_second']=='72 St',1,0)
ues_repeat_sales_closest_subway['86th'] = np.where(ues_repeat_sales_closest_subway['closest_second']=='86 St',1,0)
ues_repeat_sales_closest_subway['96th'] = np.where(ues_repeat_sales_closest_subway['closest_second']=='96 St',1,0)

#whether or not new station would be the closest
ues_repeat_sales_closest_subway['new_closest'] = np.where(ues_repeat_sales_closest_subway['distance_other'] > ues_repeat_sales_closest_subway['distance_second'],1,0)
ues_repeat_sales_closest_subway['dist_x_new_closest'] = ues_repeat_sales_closest_subway['distance_second'] * ues_repeat_sales_closest_subway['new_closest']
ues_repeat_sales_closest_subway['log_distance_other'] = np.log(ues_repeat_sales_closest_subway['distance_other'])
ues_repeat_sales_closest_subway['log_distance_second'] = np.log(ues_repeat_sales_closest_subway['distance_second'])

#%% plotting
import matplotlib.pyplot as plt
plt.scatter(ues_repeat_sales_closest_subway['distance_second'],ues_repeat_sales_closest_subway['appr_3'])

#%% regression time 
import statsmodels.api as sm


x = ues_repeat_sales_closest_subway[['log_distance_other','log_distance_second','new_closest']]
y = ues_repeat_sales_closest_subway['appr_3']

x = sm.add_constant(x)

lr = sm.OLS(y,x).fit()
print(lr.summary())
