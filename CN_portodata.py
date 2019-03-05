# -*- coding: utf-8 -*-
"""
Created on Thu Feb 28 15:34:41 2019

@author: Rajath Nandan
"""
# libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
from datetime import datetime
from pygc import great_distance
#%% Proto data pre-processing
data = pd.read_csv("train.csv",converters={'POLYLINE': lambda x: json.loads(x)})
data.TAXI_ID = data.TAXI_ID.astype("int32")
data.TIMESTAMP = data.TIMESTAMP.astype("int32")
weekID = np.zeros(data.shape[0])
timeID = np.zeros(data.shape[0])
dateID = np.zeros(data.shape[0])
time_gap = np.full(data.shape[0],15, dtype="int")
#%% Proto data pre-processing - all processing related to timestamp i.e., weekID, timeID, dateID
for i in range(data.shape[0]):
    data_timestamp_datetime = datetime.fromtimestamp(data.TIMESTAMP[i])
    dateID[i] = data_timestamp_datetime.day
    weekID[i] = data_timestamp_datetime.weekday()
    timeID[i] = data_timestamp_datetime.hour * 60 + data_timestamp_datetime.minute
    if(i%10000==0):
        print(i)

#%% Proto data pre-processing - all processing related to the lat long values i.e., lat, longs, dist, dist_gap, time
lat, lon, distgap, dist_tot, time_tot = [], [], [], [], []
j = 0
for d in data.POLYLINE:
    j+=1
    lat_temp, lon_temp, dist_temp = [], [], []
    distance = 0
    for i in range(len(d)):
        lat_temp.append(d[i][1])
        lon_temp.append(d[i][0])
        if i > 0:
            dist = great_distance(start_latitude=lat_temp[i-1], start_longitude=lon_temp[i-1], end_latitude=lat_temp[i], end_longitude=lon_temp[i])['distance'].item(0)
            dist_temp.append(dist)
            distance += dist
    lat.append(lat_temp)
    lon.append(lon_temp)
    distgap.append(dist_temp)
    dist_tot.append(distance/1000)
    time_tot.append((len(d) - 1) * 15/60)
    if(j%1000==0):
        print(j)
#%% converting numpy arrays to series for making a dataframe & converting to required data formats
#format time_gap = 15, dist, lats, driverID, dateID, weekID, timeID, time, lngs, dist_gap
s_lats = pd.Series(lat,name = 'lats')
s_lngs = pd.Series(lon,name = 'lngs')
s_dist_gap = pd.Series(distgap,name = 'dist_gap')
s_dist = pd.Series(dist_tot,name = 'dist')
s_time = pd.Series(time_tot,name = 'time')
s_weekID = pd.Series(weekID, name="weekID")
s_timeID = pd.Series(timeID, name="timeID")
s_time_gap = pd.Series(time_gap, name="time_gap")
s_dateID = pd.Series(dateID, name="dateID")
data_final = pd.concat([s_time_gap, s_dist, s_lats, data.iloc[:,4], s_weekID, s_timeID, s_dateID, s_time, s_lngs, s_dist_gap], axis=1, sort=False)
data_final.rename(columns={'TAXI_ID':'driverID'}, inplace=True)
data_final.to_json(path_or_buf='D:\Courses\Codes\CN\Porto_Data\data.txt',orient="records")
#%% store the dataset in csv format for further analysis
data_final.to_csv('D:\Courses\Codes\CN\Porto_Data\portodata.csv',index=False)