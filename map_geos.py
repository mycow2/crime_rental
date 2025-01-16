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
#%%
from geopy.distance import geodesic

df = pd.merge(second_ave[['Stop Name','geometry']],ues_repeat_sales[['block_lot_num','sale_date_1','geometry']],
              suffixes = ['_1','_2'],how = 'cross')

df['distance'] = df.geometry_1.distance(df.geometry_2)

df = df.sort_values(by = 'distance')
df = df.drop_duplicates(subset = ['block_lot_num','sale_date_1'])

