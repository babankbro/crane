import requests as req
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta, datetime
import json
import math
from db_api import *
from lookup_data import *
from distance_lookup import *

import math

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def save_data_lookup(fname, data_lookup):
    save_file = open(fname, "w")  
    rate_lookup = data_lookup["CRANE_RATE"].crane_rate_df.to_json()
    datas = {
        "FTS_DATA":data_lookup["FTS_DATA"],
        "CRANE_RATE": rate_lookup,
        "ORDER_DATA":  data_lookup["ORDER_DATA"],
    }
    json.dump(datas, save_file, indent = 4,  cls=NpEncoder) 
    save_file.close()  
    
def load_data_lookup(fname):
    f = open(fname)
    data = json.load(f)
    fts_datalookup = data["FTS_DATA"]
    order_datalookup = data["ORDER_DATA"]
    fts_datalookup['FTS_ID'] = np.array(fts_datalookup['FTS_ID'])
    order_datalookup['CARRIER_ID'] = np.array(order_datalookup['CARRIER_ID'])
    #print(fts_datalookup)
    DM = Distance_Lookup(fts_datalookup, order_datalookup)
    json_obj = json.loads(data["CRANE_RATE"])
    df_rate = pd.DataFrame(json_obj)
    print(df_rate)
    return { 
        "FTS_DATA": fts_datalookup,
        "ORDER_DATA":  order_datalookup,
        "DISTANCE_MATRIX": DM,
        "CRANE_RATE": RATE_LOOKUP(df_rate),
    }


def create_data_lookup():
    fts_datalookup = create_fts_data()
    crane_rate_datalookup = create_crane_rate_data()
    order_data = create_order_data()
    DM = Distance_Lookup(fts_datalookup, order_data)
    
    return {
        "FTS_DATA":fts_datalookup,
        "CRANE_RATE": crane_rate_datalookup,
        "ORDER_DATA": order_data,
        "DISTANCE_MATRIX": DM,
    }
    
    
def print_fts():
    fts_lookup = create_fts_data()
    for key in fts_lookup:
        print(fts_lookup[key])
        
def print_order():
    order_json = get_all_orders()
    for row in order_json:
        print(row)

if __name__ == "__main__":
    
    #data_lookup = create_data_lookup()
    #DM_lookup = data_lookup["DISTANCE_MATRIX"]
    
    #save_data_lookup('/root/crane/dataset/data1.json', data_lookup)
    #print(data_lookup["CRANE_RATE"].crane_rate_df)
    
    data_lookup = load_data_lookup('/root/crane/dataset/data1.json')
    DM_lookup = data_lookup["DISTANCE_MATRIX"]
    
    print(DM_lookup.DM.shape)
    print(DM_lookup.get_carrier_distance(10, 12))
    print("Test utility")
    print(data_lookup['CRANE_RATE'].crane_rate_df)