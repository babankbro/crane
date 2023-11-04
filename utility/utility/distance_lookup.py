import numpy as np
import pandas as pd
import math


class Distance_Lookup:
    def __init__(self, fts_datalookup, order_data):
        self.fts_lat = fts_datalookup["LAT"]
        self.fts_lng = fts_datalookup["LNG"]
        self.fts_ids = np.char.add('FTS_',fts_datalookup["FTS_ID"].astype('str'))
        self.carrier_lats = order_data["LAT"]
        self.carrier_lngs = order_data["LNG"]
        self.carrier_ids = np.char.add("CR_", order_data["CARRIER_ID"].astype('str'))
        self.index_lookup = {}
        self.id_lookup = {}
        self.lats = np.concatenate([self.fts_lat, self.carrier_lats], axis=0)
        self.lngs = np.concatenate([self.fts_lng, self.carrier_lngs], axis=0)
        self.fts_datalookup = fts_datalookup
        self.order_data = order_data
        for i in range(len(self.fts_ids)):
            fts_id = self.fts_ids[i]
            self.index_lookup[fts_id] = i
            self.id_lookup[i] = fts_id
        for i in range(len(self.carrier_ids)):
            carrier_id = self.carrier_ids[i]
            index = i + len(self.fts_ids)
            self.index_lookup[carrier_id] = index
            self.id_lookup[index] = carrier_id
        
        N = len(self.lats)
        DM = np.zeros((N, N))
        for i in range(N):
            x1 = self.lats[i]
            y1 = self.lngs[i]
            for j in range(N):
                if i == j:
                    DM[i, j] = 0
                    continue
                x2 = self.lats[j]
                y2 = self.lngs[j]
                dx = x1 - x2
                dy = y1 - y2
                DM[i, j] = round(math.sqrt(dx*dx + dy*dy)*100, 2)
        self.DM = DM
                
    def get_fts_distance(self, findex, cindex):
        fts_id = self.fts_datalookup["FTS_ID"][findex]
        carrier_id = self.order_data["CARRIER_ID"][cindex]
        indexi = self.index_lookup['FTS_' + str(fts_id)]
        indexj = self.index_lookup['CR_' + str(carrier_id)]
        return self.DM[indexi, indexj]
        
    
    def get_carrier_distance(self, index1, index2):
        carrier_id1 = self.order_data["CARRIER_ID"][index1]
        carrier_id2 = self.order_data["CARRIER_ID"][index2]
        indexi = self.index_lookup['CR_' + str(carrier_id1)]
        indexj = self.index_lookup['CR_' + str(carrier_id2)]
        return self.DM[indexi, indexj]
        