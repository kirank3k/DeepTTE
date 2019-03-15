
# coding: utf-8

from lshash import LSHash
import numpy as np
import pandas as pd
import json
from joblib import Parallel, delayed
import multiprocessing

class LshProcessing():
    def LshIndex(self):
        nodes = pd.read_csv("D:\Courses\Codes\CN\Porto_Data\nodes.txt",sep= " ", header= None)
        nodes.columns = ["lng", "lat"]
        self.lsh = LSHash(20,nodes.shape[1])
        for i in range(nodes.shape[0]):
            self.lsh.index([nodes.lng[i],nodes.lat[i]])
            if i % 20000 == 0:
                print("i : ",i)

    def LshQuery(self,data):
        discrepency_list = []
        inputs = range(data.shape[0])
        def processInput(i):
#            print("Entered", i)
            polyline_temp = []
            lng = data.lngs[i]
            lat = data.lats[i]
            lats_length = len(lat)
            lngs_length = len(lng)
            if lats_length == lngs_length:
                for j in range(lats_length):
                    pair = list(self.lsh.query([lng[j],lat[j]],num_results = 1)[0][0])
                    pair[0] = round(pair[0],6)
                    pair[1] = round(pair[1],6)
                    polyline_temp.append(pair)
            else:
                discrepency_list.append(i)
            data.polyline[i] = (polyline_temp)
            return data.polyline[i]
        num_cores = multiprocessing.cpu_count()
        print("Cores_count" ,num_cores)
        results = Parallel(n_jobs=num_cores)(delayed(processInput)(i) for i in inputs)
        data["polyline"] =  results
        return data,discrepency_list

def main():
    final_data_osmnx = pd.read_csv("D:\Courses\Codes\CN\Porto_Data\data_final_osmnx.csv",nrows =165837 ,usecols=['lngs','lats'],converters={'lngs': lambda x: json.loads(x),'lats': lambda x: json.loads(x)})
    LshPro = LshProcessing()
    LshPro.LshIndex()
    final_data_osmnx['polyline'] = pd.Series(np.zeros(final_data_osmnx.shape[0]), index=final_data_osmnx.index,dtype= str)
    final_data_osmnx, discrepancy_list = LshPro.LshQuery(final_data_osmnx)
    print("discrepancy_list is " + str(discrepancy_list))
    final_data_osmnx.to_csv("D:\Courses\Codes\CN\Porto_Data\data_final_lsh.csv",index=False)

if __name__=="__main__":
    main()


