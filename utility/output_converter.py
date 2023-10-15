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
import sys
sys.path.insert(0, "./decoder")
from crane_utility import *
from decoder import *

"""
    solution_id	 FTS_id	 carrier_id	 latlng	
    arrivaltime	exittime	operation_time	Setup_time	travel_Distance	travel_time	
    operation_rate	consumption_rate	
"""

temp_solution_schedule_json = { 
                               "solution_id": 2, "FTS_id": 0, "carrier_id": 0, 
                               'lat': 0, 'lng': 0, "arrivaltime": '2023-01-01 00:00:00',
                               "exittime": '2023-01-01 00:00:00', 
                               "operation_time":1440, "Setup_time": 150, 
                               "travel_Distance": 0, "travel_time": 0, 
                               "operation_rate": 700, "consumption_rate":0 }

def creaet_solution_schedule(fts_crane_infos):
    pass


if __name__ == "__main__":
    #data_lookup = create_data_lookup()
    data_lookup = load_data_lookup('./dataset/data2.json')
    decoder = Decoder(data_lookup)
    
    f = open('./dataset/solution1.json')
    solution_infos = json.load(f)
    fts_crane_infos = solution_infos["fts_infos"]
    for fts_crane_info in fts_crane_infos:
        print(fts_crane_info)