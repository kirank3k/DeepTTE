# -*- coding: utf-8 -*-
"""
Created on Sat Mar  2 02:07:37 2019

@author: Rajath Nandan
"""

import numpy as np
import pandas as pd
import json
import math
import matplotlib.pyplot as plt
import osmnx as ox

class Osmnx():
    def __init__(self,data):
        self.data = data
#To find the min, max for lats & lngs in portos data
    def MinMaxCoordinates(self):
        min_lat = 100
        max_lat = -100
        min_lng = 190
        max_lng = -190
        for i in range(self.data.shape[0]):
            try:
                min_lat_temp = np.min(self.data.lats[i])
                max_lat_temp = np.max(self.data.lats[i])
                min_lng_temp = np.min(self.data.lngs[i])
                max_lng_temp = np.max(self.data.lngs[i])
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
            if(i%20000==0):
                print(i)
        print("min_lat = {}, max_lat = {}, min_lng = {}, max_lng = {}".format(min_lat,max_lat,min_lng,max_lng))
        return [min_lat, max_lat, min_lng, max_lng]
    #min_lat = 38.693646, max_lat = 42.069915, min_lng = -9.385479, max_lng = -6.724395

    #To find the suitable coordinate range to comply with API & computational limitations
    def GetSuitableCoordinateRange(self,lat_width,lng_width, min_lat, max_lat, min_lng, max_lng):
        totallatBuckets = int(math.floor((max_lat - min_lat) / lat_width) + 1)
        totallngBuckets = int(math.floor((max_lng - min_lng) / lng_width) + 1)

        latBucketFrequency = [0] * totallatBuckets
        lngBucketFrequency = [0] * totallngBuckets
        row_count = 0
        for i in range(len(self.data)):
            for j in range(len(self.data.lats[i])):
                lat = self.data.lats[i][j]
                lng = self.data.lngs[i][j]
                latBucketIndex = int(math.floor((lat - min_lat) / lat_width))
                latBucketFrequency[latBucketIndex] += 1
                lngBucketIndex = int(math.floor((lng - min_lng) / lng_width))
                lngBucketFrequency[lngBucketIndex] += 1
            if(row_count%10000==0):
                print(row_count)
            row_count +=1
        #We have frequencies, Find buckets with highest frequency
        min_suitable_lat = min_lat + lat_width * latBucketFrequency.index(max(latBucketFrequency))
        max_suitable_lat = min_suitable_lat + lat_width

        min_suitable_lng = min_lng + lng_width * lngBucketFrequency.index(max(lngBucketFrequency))
        max_suitable_lng = min_suitable_lng + lng_width

        print(" min_suitable_lat = {}, max_suitable_lat = {}, min_suitable_lng = {}, max_suitable_lng = {}".format(min_suitable_lat, max_suitable_lat, min_suitable_lng, max_suitable_lng))

        return [max_suitable_lat,min_suitable_lat,max_suitable_lng,min_suitable_lng]

    #to trim the data to the trips which lie is suitable coordinate range
    def TrimData(self,max_suitable_lat,min_suitable_lat,max_suitable_lng,min_suitable_lng):
        trim_index = []
        for i in range(self.data.shape[0]):
            try:
                min_lat_temp = np.min(self.data.lats[i])
                max_lat_temp = np.max(self.data.lats[i])
                min_lng_temp = np.min(self.data.lngs[i])
                max_lng_temp = np.max(self.data.lngs[i])
            except ValueError:  #raised if data.lats[i] or data.lngs[i] is empty.
                pass
            if(min_suitable_lat>min_lat_temp):
                trim_index.append(i)
            elif(max_suitable_lat<max_lat_temp):
                trim_index.append(i)
            elif(min_suitable_lng>min_lng_temp):
                trim_index.append(i)
            elif(max_suitable_lng<max_lng_temp):
                trim_index.append(i)
            if(i%20000==0):
                print(i)
        return trim_index

    #to generate OSMNX files from area that can be generated using coordinates obtained above
    def OsmnxApi(self,max_suitable_lat,min_suitable_lat,max_suitable_lng,min_suitable_lng):
        ox.config(log_file=True, log_console=True, use_cache=True)
        G = ox.graph_from_bbox(north=max_suitable_lat, south=min_suitable_lat, east=max_suitable_lng, west=min_suitable_lng,  network_type='drive', simplify=False, infrastructure='way["highway"]')
        print("coordinates obtained")
    #    G = ox.simplify_graph(G,strict=False) #Read about strict and non-strict mode
        nodes = ox.graph_to_gdfs(G, edges=False)
        edges = ox.graph_to_gdfs(G, nodes=False)
        extract_nodes=nodes[['x','y']]
        extract_edges=edges[['geometry']]
        np.savetxt('D:\\Courses\\Codes\\CN\\Porto_Data\\nodes.txt', extract_nodes.values, fmt='%f')
        print("OSMNX Node files are generated")
        np.savetxt('D:\\Courses\\Codes\\CN\\Porto_Data\\edges.txt', extract_edges.values, fmt='%s')
        print("OSMNX Edge files are generated")


def main():
    # loading formatted data for obtaining the min & max of lats, lngs
    data = pd.read_csv("D:\\Courses\\Codes\\CN\\Porto_Data\\Cleaned_Portodata_final.csv",usecols=['lats','lngs'], converters={'lats': lambda x: json.loads(x),'lngs': lambda z: json.loads(z)})
    print("Formatted porto data loaded")
    lat_width = 0.55 #Width of lat required ~ 0.1 to 0.2
    lng_width = 0.55 #Width of lng required ~ 0.1 to 0.2
    Osmnx_instance = Osmnx(data)
    min_lat, max_lat, min_lng, max_lng = Osmnx_instance.MinMaxCoordinates()
    max_suitable_lat,min_suitable_lat,max_suitable_lng,min_suitable_lng = Osmnx_instance.GetSuitableCoordinateRange(lat_width,lng_width, min_lat, max_lat, min_lng, max_lng)
    trim_index = Osmnx_instance.TrimData(max_suitable_lat,min_suitable_lat,max_suitable_lng,min_suitable_lng)
    Osmnx_instance.OsmnxApi(max_suitable_lat,min_suitable_lat,max_suitable_lng,min_suitable_lng)
    s_trim_index = pd.Series(trim_index,name="trim_index")
    data_trim_index = pd.DataFrame(s_trim_index)
    data.drop(data.index[data_trim_index], inplace=True)
    data.to_csv('D:\Courses\Codes\CN\Porto_Data\data_final_osmnx.csv',index=False)

if __name__=="__main__":
    main()
