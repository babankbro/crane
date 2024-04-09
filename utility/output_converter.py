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

"""solution_carrier_order
   s_id order_id start_time finish_time penalty_cost reward
"""

"""solution_schedule
    solution_id	 FTS_id	 order_id, carrier_id	 lat lng	
    arrivaltime	exittime	operation_time	Setup_time	travel_Distance	travel_time	
    operation_rate	consumption_rate	
"""
"""solution_crane_schedule
    solution_id	
    carrier_id	
    start_time	due_time	operation_time	Setup_time	
    travel_Distance	
    travel_time	operation_rate
    consumption_rate
    crane_id	
    bulk	
    load_cargo
"""
""" crane_solution
    solution_id	
    FTS_id	
    crane_id	
    total_cost	
    total_consumption_cost	
    total_wage_cost	
    penality_cost	
    total_reward	
    total_late_time	
    total_early_time	
    total_operation_consumption_cost
    total_operation_time
    total_preparation_crane_time	
    date
"""

temp_ship_solution_json = {

   "s_id": 0,  "order_id":0,
   "start_time":'2023-01-01 00:00:00',
   "finish_time":'2023-01-01 00:00:00',
   "penalty_cost":0, "reward":0,
   "total_cost":0, "total_consumption_cost":0, "total_wage_cost":0,

}

temp_crane_solution_json = {
                               "solution_id": 2, "FTS_id": 0, 
                               "crane_id": 0,
                               "total_cost": 0, 
                               "total_consumption_cost":0, "total_wage_cost": 0, 
                               "penality_cost": 0, "total_reward": 0, 
                               "total_late_time": 0, "total_early_time":0,
                               "total_operation_consumption_cost":0, 
                               "total_operation_time": 0, 
                               "total_preparation_crane_time":0, 
                               'date':'2023-01-01'
}

temp_solution_schedule_json = { 
                               "solution_id": 2, "FTS_id": 0, "carrier_id": 0, 
                               'lat': 0, 'lng': 0, "arrivaltime": '2023-01-01 00:00:00',
                               "exittime": '2023-01-01 00:00:00', 
                               "operation_time":1440, "Setup_time": 150, 
                               "travel_Distance": 0, "travel_time": 0, 

                               "operation_rate": 700, "consumption_rate":0,
                               "cargo_id":0}


temp_solution_crane_schedule_json = { 
                               "solution_id": 2,  "order_id": 0,  "carrier_id": 0, 
                                "start_time": '2023-01-01 00:00:00',
                               "due_time": '2023-01-01 00:00:00', 
                               "operation_time":0, "Setup_time": 0, 
                               "travel_Distance": 0, "travel_time": 0, 
                               "operation_rate": 700, "consumption_rate":0,
                               "consumption_rate":0, 
                               "crane_id": 0, 
                               "bulk":0, 'load_cargo':0, 'cargo_id': 0}

class OutputConverter:
    def __init__(self, data_lookup) -> None:
        self.data_lookup= data_lookup
    
    def create_json_ship_info(self, sid, ship_info, df):
        

        temp = dict(temp_ship_solution_json)
        temp['s_id'] = sid
        temp['order_id'] = ship_info['order_id']
        if ship_info['delta_time'] < 0:
            temp['penalty_cost'] =  abs(ship_info['delta_time']) * ship_info['penalty_rate']
        else:
            temp['reward'] =  ship_info['delta_time'] * ship_info['reward_rate']
        #temp['reward']  = np.max(ship_info["fts_crane_operation_times"])
        temp['total_consumption_cost'] = sum(df['consumption_liter'])*35
        temp['total_wage_cost'] = sum(df['premium_wage'])
        temp['total_cost'] = temp['total_consumption_cost'] + temp['penalty_cost'] + temp['total_wage_cost']
        return temp

    def create_json_fts_info(self, sid, fts_crane_info):
        FTS_DATA = self.data_lookup['FTS_DATA']
        fts_setup_time = fts_crane_info['fts_setup_time']
        fts_index = fts_crane_info['fts_id']
        
        ORDER_DATA = self.data_lookup['ORDER_DATA']
        MIN_DATE_TIME = ORDER_DATA['MIN_DATE_TIME']
        result_json = []
        temp = dict(temp_solution_schedule_json)
        temp['solution_id'] = sid
        temp['FTS_id'] = fts_crane_info['fts_db_id'] 
        temp['order_id'] = 0
        temp['carrier_id'] = 0
        temp['lat'] = FTS_DATA['LAT'][fts_index]
        temp['lng'] = FTS_DATA['LNG'][fts_index]
        temp['operation_time'] = None
        temp['Setup_time'] = None
        temp['travel_Distance'] = None
        temp['travel_time'] = None
        temp['operation_rate'] = None
        temp['consumption_rate'] = None
        temp['cargo_id'] = 0
        carrier_id_lookup = {}
        hours_to_add = timedelta(hours=0)
        if len(fts_crane_info["start_times"]) > 0:
            hours_to_add = timedelta(hours=fts_crane_info["start_times"][0])
        
        #print(MIN_DATE_TIME)
        format_string = "%Y-%m-%d %H:%M:%S" 
        MIN_DATE_TIME = datetime.strptime(MIN_DATE_TIME, format_string)
        #print(MIN_DATE_TIME)
        exit_time = MIN_DATE_TIME + hours_to_add 
        temp['arrivaltime'] = exit_time.strftime(format_string)
        temp['exittime'] = exit_time.strftime(format_string)
        result_json.append(temp)
        ID_LIST = list(ORDER_DATA['CARRIER_ID'])
        for inx in range(len(fts_crane_info["ids"])):
            cid = fts_crane_info["ids"][inx]
            cr_id = ORDER_DATA['CARRIER_ID'][cid]
            idx_cr = ID_LIST.index(cr_id)
            fts_setup_time = fts_crane_info['fts_setup_time']
            temp['cargo_id'] = ORDER_DATA['CARGO_ID'][cid]
            
            temp = dict(temp_solution_schedule_json)
            temp['solution_id'] = sid
            temp['FTS_id'] = fts_crane_info['fts_db_id'] 
            #print("cr_id", cr_id)
            temp['carrier_id'] = int(cr_id)
            temp['order_id'] = fts_crane_info["order_ids"][inx]
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
            temp['cargo_id'] = ORDER_DATA['CARGO_ID'][cid]
            enter_time = MIN_DATE_TIME + start_hours_to_add
            exit_time = MIN_DATE_TIME + end_hours_to_add
            temp['arrivaltime'] =enter_time.strftime('%Y-%m-%d %H:%M:%S')
            temp['exittime'] = exit_time.strftime('%Y-%m-%d %H:%M:%S')
            
           
            
            result_json.append(temp)
        
        return result_json

    def create_solution_schedule(self, sid, fts_crane_infos):
        result_json = []
        for fc_info  in fts_crane_infos:
            if fc_info['fts_id']==1:
                print(fc_info['fts_name'])
                print("##############################")
            fts_jsons = self.create_json_fts_info(sid, fc_info)
            if fc_info['fts_id']==1:
                print("##############################")
            #print(fc_info)
            result_json.extend(fts_jsons)
        #print(fc_info)
        return result_json
    
    def create_ship_solution_schedule(self, sid, ship_infos, df_crane_info, data_lookup):
        result_json = []
        lookup_order_id = {}
        cargo_df = pd.DataFrame(data_lookup['CARGO']).dropna()
        df_crane_info = pd.merge(df_crane_info, cargo_df, on='cargo_id', how='left')
        df_crane_info['consumption_liter'] = df_crane_info["load_cargo"] * df_crane_info['consumption_rate']
        df_crane_info['premium_wage'] = df_crane_info["load_cargo"] * df_crane_info['premium_rate']
        
        for i in range(len(ship_infos)):
            df = df_crane_info[df_crane_info['carrier_id'] == ship_infos[i]['ship_db_id']]
            if i == 0:
                print(ship_infos[i])
                print(df)
            ship_jsons = self.create_json_ship_info(sid, ship_infos[i], df)
            if ship_jsons['order_id'] in lookup_order_id:
                ship_jsons_a = lookup_order_id[ship_jsons['order_id']]
                ship_jsons_a['penalty_cost'] = max(ship_jsons_a['penalty_cost'], ship_jsons['penalty_cost'])
                ship_jsons_a['reward'] = min(ship_jsons_a['reward'], ship_jsons['reward'])
                continue 
            lookup_order_id[ship_jsons['order_id']] = ship_jsons
            result_json.append(ship_jsons)
        return result_json

    def create_json_crane_info(self, sid, fts_info):
        #print("---------------------------------")
        #print(fts_info['fts'].name)
        ORDER_DATA = self.data_lookup['ORDER_DATA']
        CRANE_RATE = self.data_lookup['CRANE_RATE']
        format_string = "%Y-%m-%d %H:%M:%S" 
        MIN_DATE_TIME = ORDER_DATA['MIN_DATE_TIME']
        MIN_DATE_TIME = datetime.strptime(MIN_DATE_TIME, format_string)
    
        #print(fts_info)
        #print('demands', fts_info['demands'])
        #print('consumption_rates', fts_info['consumption_rates'])
        #print('operation_rates', fts_info['operation_rates'])
        #print('crane_setup_times', fts_info['crane_setup_times'])
        #print(type(fts_info['crane_infos']))
        #print(fts_info['crane_infos'])
        result_json = []
        for si in range(len(fts_info['ids'])):
            crane_ship_info = fts_info['crane_infos'][si]
            start_ship_time = fts_info['start_times'][si]
            fts_setup_time = fts_info['fts_setup_time']
            
            crane_bulks = crane_ship_info['crane_infos']
            order_id = fts_info['order_ids'][si]
           
            
            for cindx, cbulk in enumerate(crane_bulks):
                #print("cbulk ==========", cbulk)
                operation_rate = cbulk["operation_rate"]
                consumption_rate = cbulk["consumption_rate"]
                crane_index = cbulk['crane_index']
                ship = cbulk['ship']
                #order_id = cbulk['order_id']
                #print(cbulk["operation_times"])
                for ibluck, bulk in enumerate(cbulk['bulks']):
                    temp = dict(temp_solution_crane_schedule_json)
                    
                    
                    """
                    solution_id	
                    order_id 
                    carrier_id	
                    start_time	due_time	operation_time	Setup_time	
                    travel_Distance	
                    travel_time	operation_rate
                    consumption_rate
                    crane_id	
                    bulk	
                    load_cargo
                    cargo_id
                    """
                    #print(cbulk)
                    start_hours_to_add = timedelta(hours=start_ship_time + fts_setup_time+\
                                                   cbulk["offset_start_times"][ibluck])
                    end_hours_to_add = timedelta(hours=start_ship_time + fts_setup_time+\
                                                 cbulk["finish_times"][ibluck])
                
                    #if len(fts_crane_info["start_times"]) > 0:
                        #hours_to_add = timedelta(hours=fts_crane_info["start_times"][0])
                    enter_time = MIN_DATE_TIME + start_hours_to_add
                    exit_time = MIN_DATE_TIME + end_hours_to_add
                    temp['solution_id'] = sid
                    temp['order_id']  = order_id
                    temp['carrier_id'] = cbulk['ship'].id
                    temp['start_time'] =enter_time.strftime('%Y-%m-%d %H:%M:%S')
                    temp['due_time'] = exit_time.strftime('%Y-%m-%d %H:%M:%S')
                    temp['operation_time'] = cbulk["operation_times"][ibluck]
                    temp['Setup_time'] = 0
                    temp['travel_time'] = 0
                    temp['travel_Distance'] = 0
                    temp['operation_rate'] = operation_rate
                    temp['consumption_rate'] = consumption_rate
                    temp['crane_id'] = fts_info['fts'].crane_ids[crane_index]
                    temp['bulk'] = cbulk["bulks"][ibluck] + 1
                    temp['load_cargo'] = cbulk["loads"][ibluck]
                    temp['cargo_id'] = ship.cargo_id
                    #print(temp)
                    result_json.append(temp)
                    #temp['start_time'] = 
                    #temp['lng'] = FTS_DATA['LNG'][fts_index]
                    #temp['operation_time'] = None
                    #temp['Setup_time'] = None
                    #temp['travel_Distance'] = None
                    #temp['travel_time'] = None
                    #temp['operation_rate'] = None
                    #temp['consumption_rate'] = None
                    #print(temp)
                    #break
                
            #continue
            #print(crane_info)
               
        return result_json
    
    def create_crane_solution_schedule(self, sid, fts_crane_infos):
        result_json = []
        for fc_info  in fts_crane_infos:
            fts_jsons = self.create_json_crane_info(sid, fc_info)
            #print(fc_info)
            result_json.extend(fts_jsons)
        #print(fc_info)
        return result_json
    
    def create_json_crane_cost(self, sid, fts_info, ship_infos):
        print("---------------------------------")
        print(fts_info['fts'].name)
        #print(fts_info)
        fts = fts_info['fts']
        fts_id = fts_info["fts_id"]
        result_json = []
        #fts = fts_info['fts']
        for i in range(len(fts.cranes)):
            temp = dict(temp_crane_solution_json)
            temp['solution_id'] = sid
            temp['FTS_id'] = fts_info['fts'].id
            temp['crane_id'] = fts_info['fts'].crane_ids[i]
            temp['total_operation_time'] = 0
            temp['total_operation_consumption_cost'] = 0
            temp['total_late_time'] = 0
            temp['total_early_time'] = 0
            temp['penality_cost'] =  0
            temp['total_reward'] =  0
            temp['date'] = '2023-01-01'
            #temp['fixed_wage_cost'] = 
            temp['premium_wage_cost'] = 0
         
            result_json.append(temp)
        
        for si in range(len(fts_info['ids'])):
            crane_ship_info = fts_info['crane_infos'][si]
            start_ship_time = fts_info['start_times'][si]
            start_ship_time = fts_info['start_times'][si]
            order_id = fts_info['ids'][si]
            ship = ship_infos[order_id]
            
            ship_due_time = ship["due_time"]
            #print("ship =============",ship)
            crane_index = ship["fts_crane_ids"].index(fts_id)
            
            reward_rate = ship['reward_rate']
            penalty_rate = ship['penalty_rate']
            crane_bulks = crane_ship_info['crane_infos']
            exit_time = ship["fts_crane_exit_times"][crane_index]
            #fts_crane_ids #fts_crane_exit_times
            for cindx, cbulk in enumerate(crane_bulks):
                #print(cbulk)
                
                operation_rate = cbulk["operation_rate"]
                consumption_rate = cbulk["consumption_rate"]
                crane_index = cbulk['crane_index']
                ship = cbulk['ship']
                if len(cbulk["loads"]) == 0:
                    continue
                #print(ship)
                
                """ 
                    solution_id	
                    FTS_id	/
                    crane_id	/
                    total_cost	-
                    total_consumption_cost -
                    total_wage_cost	-
                    penality_cost - 	
                    total_reward -	
                    total_late_time	-
                    total_early_time -	
                    total_operation_consumption_cost /
                    total_operation_time /
                    total_preparation_crane_time/	
                    date
                """
                
                temp = result_json[crane_index]
                temp['total_operation_time'] += sum(cbulk['operation_times'])
                temp['total_operation_consumption_cost'] += round(sum(cbulk['loads'])*cbulk['consumption_rate'], 2)
                temp['total_preparation_crane_time'] += len(cbulk['loads'])*fts_info['fts'].setup_time_cranes[crane_index]
                temp['premium_wage_cost'] += round(sum(cbulk['loads'])*fts_info['fts'].premium_rates[crane_index] ,2)
                exit_time = cbulk["finish_times"][-1]
                #print("cbulk =====================", cbulk)
                delta_time = ship_due_time - exit_time
                if delta_time > 0:
                    temp['total_early_time'] = delta_time
                    temp['total_reward'] = temp['total_early_time']*reward_rate
                else:
                    temp['total_late_time'] = -delta_time
                    temp['penality_cost'] =  temp['total_late_time']*penalty_rate
                
                
                
                
        for i in range(len(fts.cranes)):
            temp = result_json[i]
            temp['total_wage_cost'] = temp['premium_wage_cost'] + fts_info['fts'].wage_month_costs[i] 
            temp['total_consumption_cost'] = round(temp['total_operation_consumption_cost'], 2)
            temp['total_cost'] = round(temp['total_wage_cost'] + temp['total_consumption_cost'] + temp['penality_cost'] , 2)
            temp.pop("premium_wage_cost")
            if "penalty_cost" in temp:
                temp.pop('penalty_cost')
            
        return result_json
    
    def create_crane_solution(self, sid, fts_crane_infos, ship_infos):
        result_json = []
        for fc_info  in fts_crane_infos:
            fts_jsons = self.create_json_crane_cost(sid, fc_info, ship_infos)
            #print(fts_jsons)
            result_json.extend(fts_jsons)
            #break
        #print(fc_info)
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