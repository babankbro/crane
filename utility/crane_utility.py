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
    
    data_lookup = create_data_lookup()
    DM_lookup = data_lookup["DISTANCE_MATRIX"]
    
    print(DM_lookup.DM.shape)
    print(DM_lookup.get_carrier_distance(10, 12))
    print("Test utility")