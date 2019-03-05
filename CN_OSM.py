# -*- coding: utf-8 -*-
"""
Created on Sat Mar  2 02:07:37 2019

@author: Rajath Nandan
"""

import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
import osmnx as ox

#%% To find the min, max for lats & lngs in portos data
data = pd.read_csv("portodata.csv",converters={'lats': lambda x: json.loads(x),'lngs': lambda z: json.loads(z)})
min_lat = 100
max_lat = -100
min_lng = 190
max_lng = -190
for i in range(data.shape[0]):
    try:
        min_lat_temp = np.min(data.lats[i])
        max_lat_temp = np.max(data.lats[i])
        min_lng_temp = np.min(data.lngs[i])
        max_lng_temp = np.max(data.lngs[i])
    except ValueError:  #raised if data.lats[i] or data.lngs[i] is empty.
        pass
    if(min_lat>min_lat_temp):
        min_lat = min_lat_temp
    if(max_lat<max_lat_temp):
        max_lat = max_lat_temp
    if(min_lng>min_lng_temp):
        min_lng = min_lng_temp
    if(max_lng<max_lng_temp):
        max_lng = max_lng_temp
print("min_lat = {}, max_lat = {}, min_lng = {}, max_lng = {}".format(min_lat,max_lat,min_lng,max_lng))
#min_lat = 31.992111, max_lat = 51.037119, min_lng = -36.913779, max_lng = 52.900803
#%% to generate OSMNX files from area that can be generated using coordinates obtained above
ox.config(log_file=True, log_console=True, use_cache=True)
G = ox.graph_from_bbox(north=max_lat,south=min_lat,east=max_lng,west=min_lng, network_type='drive',sinplify=False,infrastructure='way["highway"]')










#%%


G=ox.graph_from_bbox(41.9123147,41.7623147,12.6046319,12.4546319,network_type='drive',simplify=False,infrastructure='way["highway"]') #Check variations in paper
fig1,ax = ox.plot_graph(G,dpi=1000,node_color='g',edge_color='b')
G = ox.simplify_graph(G,strict=False) #Read about strict and non-strict mode
nodes = ox.graph_to_gdfs(G, edges=False)
edges = ox.graph_to_gdfs(G, nodes=False)
extract=nodes[['x','y']]
extract_edges=edges[['geometry']]
fig, ax = ox.plot_graph(G,dpi=1000,node_color='r',edge_color='b')
np.savetxt(r'/home/soumi/osmnx/rome_nodes3.txt', extract.values, fmt='%f')
np.savetxt(r'/home/soumi/osmnx/rome_edges3.txt', extract_edges.values, fmt='%s')