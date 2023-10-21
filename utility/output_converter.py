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

class OutputConverter:
    def __init__(self, data_lookup) -> None:
        self.data_lookup= data_lookup
    

    def create_json_fts_info(self, sid, fts_crane_info):
        FTS_DATA = self.data_lookup['FTS_DATA']
        fts_index = fts_crane_info['fts_id']
        ORDER_DATA = self.data_lookup['ORDER_DATA']
        
        result_json = []
        temp = dict(temp_solution_schedule_json)
        temp['solution_id'] = sid
        temp['FTS_id'] = fts_crane_info['fts_db_id'] 
        temp['carrier_id'] = 0
        temp['lat'] = FTS_DATA['LAT'][fts_index]
        temp['lng'] = FTS_DATA['LNG'][fts_index]
        temp['operation_time'] = None
        temp['Setup_time'] = None
        temp['travel_Distance'] = None
        temp['travel_time'] = None
        temp['operation_rate'] = None
        temp['consumption_rate'] = None
        
        hours_to_add = timedelta(hours=0)
        if len(fts_crane_info["start_times"]) > 0:
            hours_to_add = timedelta(hours=fts_crane_info["start_times"][0])
        
        exit_time = BASE_DATE_TIME + hours_to_add
        temp['arrivaltime'] = exit_time.strftime('%Y-%m-%d %H:%M:%S')
        temp['exittime'] = exit_time.strftime('%Y-%m-%d %H:%M:%S')
        result_json.append(temp)
        ID_LIST = list(ORDER_DATA['CARRIER_ID'])
        for inx in range(len(fts_crane_info["ids"])):
            cid = fts_crane_info["ids"][inx]
            cr_id = ORDER_DATA['CARRIER_ID'][cid]
            idx_cr = ID_LIST.index(cr_id)
            
            
            temp = dict(temp_solution_schedule_json)
            temp['solution_id'] = sid
            temp['FTS_id'] = fts_crane_info['fts_db_id'] 
            #print("cr_id", cr_id)
            temp['carrier_id'] = int(cr_id)
            temp['lat'] = ORDER_DATA['LAT'][idx_cr]
            temp['lng'] = ORDER_DATA['LNG'][idx_cr]
            temp['operation_time'] = fts_crane_info["process_times"][inx]
            temp['Setup_time'] = fts_crane_info["fts_setup_time"]
            temp['travel_Distance'] = fts_crane_info["distances"][inx]
            temp['travel_time'] = fts_crane_info["travel_times"][inx]
            temp['operation_rate'] = fts_crane_info["operation_rates"][inx]
            temp['consumption_rate'] = fts_crane_info["consumption_rates"][inx]
            
            start_hours_to_add = timedelta(hours=fts_crane_info["start_times"][inx])
            end_hours_to_add = timedelta(hours=fts_crane_info["end_times"][inx])
            
            enter_time = BASE_DATE_TIME + start_hours_to_add
            exit_time = BASE_DATE_TIME + end_hours_to_add
            temp['arrivaltime'] =enter_time.strftime('%Y-%m-%d %H:%M:%S')
            temp['exittime'] = exit_time.strftime('%Y-%m-%d %H:%M:%S')
            
            result_json.append(temp)
        
        return result_json

    def create_solution_schedule(self, sid, fts_crane_infos):
        result_json = []
        for fc_info  in fts_crane_infos:
            fts_jsons = self.create_json_fts_info(sid, fc_info)
            #print(fc_info)
            result_json.extend(fts_jsons)
        print(fc_info)
        return result_json


if __name__ == "__main__":
    #data_lookup = create_data_lookup()
    data_lookup = load_data_lookup('./dataset/data2.json')
    print(data_lookup['ORDER_DATA'])
    converter = OutputConverter(data_lookup)
    
    decoder = Decoder(data_lookup)
    
    
    
    f = open('./dataset/solution1.json')
    solution_infos = json.load(f)
    fts_crane_infos = solution_infos["fts_infos"]
    result = converter.create_solution_schedule(1, fts_crane_infos)
    json_string = json.dumps(result, indent=2)
    df = pd.read_json(json_string)
    print(df)