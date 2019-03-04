# -*- coding: utf-8 -*-
"""
Created on Mon Feb  4 01:38:51 2019

@author: Kiran
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

#files = os.listdir('D:\PGDBA\IIT KGP\Class_Courses\Complex Networks\Project\geolifetrajectories\Data')
#%%
def getListOfFiles(dirName):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
    return allFiles

dirName = 'D:\Courses\Codes\CN\Geolife Data\Data';

#%%
# Get the list of all files in directory tree at given path
listOfFiles = getListOfFiles(dirName)

# to prepare a datafram with paths of all the plt files
FileNames = pd.DataFrame(listOfFiles,columns = ['FilePath'])
FileNames_Plt_Path = FileNames['FilePath'].apply(lambda x: x if x[-3:] == 'plt' else float('nan'))
FileNames_Plt_Path = pd.DataFrame(FileNames_Plt_Path,)
count_nan = len(FileNames_Plt_Path) - FileNames_Plt_Path.count()
FileNames_Plt_Path = FileNames_Plt_Path.dropna()
#FileNames_Plt_Path.to_csv('D:\PGDBA\IIT KGP\Class_Courses\Complex Networks\Project\geolifetrajectories\plt_paths.csv',index_label=['Index'])


# to prepare a datafram with paths of all the text files
FileNames_txt_Path = FileNames['FilePath'].apply(lambda x: x if x[-3:] == 'txt' else float('nan'))
FileNames_txt_Path = pd.DataFrame(FileNames_txt_Path)
count_nan = len(FileNames_txt_Path) - FileNames_txt_Path.count()
FileNames_txt_Path = FileNames_txt_Path.dropna()
#FileNames_txt_Path.to_csv('D:\PGDBA\IIT KGP\Class_Courses\Complex Networks\Project\geolifetrajectories\label_paths.csv',index_label=['Index'])

#%% data loader
conv_Date =  lambda x: datetime.strptime(x.decode("utf-8"), '%Y-%m-%d')
conv_Time =  lambda x: datetime.strptime(x.decode("utf-8"), '%H:%M:%S')

final_data = pd.DataFrame(np.genfromtxt(FileNames_Plt_Path['FilePath'][0],skip_header=6, delimiter=",",converters={5: conv_Date,6: conv_Time}))
j=0
for i in FileNames_Plt_Path['FilePath'][1:] :
	j+=1
	if(j%100==0):
		print("iteration number {}".format(i))
	file_data = pd.DataFrame(np.genfromtxt(i,skip_header=6, delimiter=",",converters={5: conv_Date,6: conv_Time}))
	final_data = pd.concat((final_data,file_data), axis = 0)

#final_data_exam = final_data.iloc[:200,:]
#final_data_exam.to_csv('D:\Courses\Codes\CN\geolife.csv')
final_data.to_csv('D:\Courses\Codes\CN\geolife.csv')

#%% loading data from csv
final_data = pd.read_csv("geolife.csv")
final_data.head(5)
len_final_data = final_data.shape[0]

#%% generate the file list for trajectory folders which have labels

#FileNames_txt_Path.info()
#FileNames_txt_Path.head(5)
listOfFiles_label = list()
for i in FileNames_txt_Path.iloc[:,0]:
	i = i[:-10] + "Trajectory"
	listOfFiles_label = listOfFiles_label +  getListOfFiles(i)

#%% check how many trips are available in the data set with the help of labels data &
# the minimum time for the trajectory is 20 min
listOfFiles_label1 = list()
k = 0
for i in FileNames_txt_Path.iloc[:,0]:
	tables = pd.read_csv(i,sep="	", parse_dates = ["Start Time", "End Time"])
	tables.info()
	tables_taxi = tables[(tables['Transportation Mode']=='taxi') & ((tables['End Time'] - tables['Start Time']) > pd.Timedelta('0 days 00:20:00'))]
	tables_car = tables[(tables['Transportation Mode']=='car') & ((tables['End Time'] - tables['Start Time']) > pd.Timedelta('0 days 00:20:00'))]
	if(k==0):
		tables_final = pd.concat((tables_car,tables_taxi))
	else:
		tables_final = pd.concat((tables_final,pd.concat((tables_car,tables_taxi))))
	k+=1

#	tables_final = tables_final[tables_final['End Time'] - tables_final['Start Time']!= pd.Timedelta('0 days 23:59:59')]
#%% finding the trip lengths from the table which has trips whose minimum trip length
# is more than 20 min


trip_length = tables['End Time'] - tables['Start Time']
trip_length.describe()
trip_length_final = (tables_final['End Time'] - tables_final['Start Time']).seconds
trip_length_final.quantile(0.95)
trip_length_final.describe()

#	tables_taxi.loc['file_name'] = type(tables_taxi.iloc[:,0].values.str.strip('-: '))
#%%
trip_length_final.reset_index(drop=True, inplace=True)
trip_length_final_seconds = [x.seconds/60 for x in trip_length_final]
plt.hist(trip_length_final_seconds, bins = 1000)
plt.xlabel("minutes")
plt.title("histogram of trip duration in minutes & t>20 min")
#plt.scatter(np.arange(len(trip_length_final_seconds)),trip_length_final_seconds)




#%%
FileNames_label = pd.DataFrame(listOfFiles_label,columns = ['FilePath'])
FileNames_Plt_Path_label = FileNames_label['FilePath'].apply(lambda x: x if x[-3:] == 'plt' else float('nan'))
FileNames_Plt_Path_label = pd.DataFrame(FileNames_Plt_Path_label,)
FileNames_Plt_Path_label = FileNames_Plt_Path_label.dropna()

#%%
columns_list =['lat','lon','arbit','altitude','nds','date','time']
final_data_label = pd.read_csv(FileNames_Plt_Path_label['FilePath'][0],names= columns_list,skiprows=range(0,6), parse_dates=[['date','time']], delimiter=",")
j=0
for i in FileNames_Plt_Path_label['FilePath'][1:] :
	j+=1
	if(j%100==0):
		print("iteration number {}".format(i))
	file_data = pd.read_csv(i,names= columns_list,skiprows=range(0,6), parse_dates=[['date','time']], delimiter=",")
	final_data_label = pd.concat((final_data_label,file_data), axis = 0, sort=False)

final_data_label.to_csv('D:\Courses\Codes\CN\geolife_label.csv')


#%% heat map using google maps API (not working - API limitations)
#import gmplot
#gmap = gmplot.GoogleMapPlotter.from_geocode("Beijing,China")
#for i in range(len_final_data):
#	lat_list = final_data.iloc[i,1].values[:,0]
#	lat_list = final_data.iloc[i,1].values[:,0]
#
## heatmap plot heating Type
## points on the Google map
#gmap.heatmap( lat_list, long_list )
#gmap.draw("D:\\Courses\\Codes\\CN\\map14.html")

#%% for generating heat maps using cmaps
import copy
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import LogNorm

#plt.plot(final_data.iloc[i,1].values[:,0],final_data.iloc[i,1].values[:,0])

center=[39.984702,
116.318417]
radius=200
histogram_range = [
       [center[0] - radius, center[0] + radius],
       [center[1] - radius, center[1] + radius]
   ]

cmap = copy.copy(plt.cm.jet)
cmap.set_bad((0,0,0))

fig = plt.figure(figsize=(5,5))
plt.hist2d(final_data['f0'], final_data['f1'], bins=1000, norm=LogNorm(),
              cmap=cmap, range=histogram_range)

#%% for generating heat maps using geopy
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="specify_your_app_name_here")
for i in range(len(final_data)):
    lat_lon = str(final_data['f0'].iloc[i]) + ',' + str(final_data['f1'].iloc[i])
    location = geolocator.reverse(i)
    final_data['address'].iloc[i] = location.address

