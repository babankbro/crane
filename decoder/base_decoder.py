import sys
from crane_configuration import *
from ship_assign import *
from crane_decoder import *
sys.path.insert(0, "./utility")

from crane_utility import *
from output_converter import *
import numpy as np
import pandas as pd

class BaseDecoder:
    def __init__(self, data_lookup):
        self.data_lookup = data_lookup
        self.WSHIP = 0.5
        self.WFTS = 0.5
        self.NSHIP = len(data_lookup['ORDER_DATA']["LAT"])
        self.NFTS = len(data_lookup['FTS_DATA']["LAT"])
        
        self.arrival_hours = np.array(data_lookup['ORDER_DATA']['ARRIVAL_TIME_HOUR'])
        self.due_hours = np.array(data_lookup['ORDER_DATA']['DUE_TIME_HOUR'])
        due_hours = self.due_hours
        arrival_hours = self.arrival_hours
        
        self.MIN_TIME = min(self.arrival_hours)
        self.MAX_TIME = max(self.due_hours)
        
        
        df = pd.DataFrame(data_lookup['ORDER_DATA'])
        fts_rate_lookups = data_lookup['CRANE_RATE'].lookup_fts_ids
        self.NFTS = len(fts_rate_lookups)
        print("MIN-MAX", self.MIN_TIME, self.MAX_TIME, self.NFTS)
        self.D = self.NSHIP*self.NFTS + self.NSHIP
        self.WEIGHT_CRANE_SHIPs = []
        self.SHIP_WEIGHTs = (due_hours-self.MIN_TIME)/(np.max(due_hours)-self.MIN_TIME) 
        for i in range(self.NSHIP):
            self.WEIGHT_CRANE_SHIPs.append(0.5)
            
        self.ships = []
        for i in range(len(df)):
            ship = Ship(df.iloc[i])
            self.ships.append(ship)
            #print(ship)
        
        self.ftses = []
        for key in fts_rate_lookups:
            fts_rate = fts_rate_lookups[key]
            #fts_rate.set_display_rate('ถ่านหิน', 'import')
            self.ftses.append(fts_rate)
        self.DM_lookup = self.data_lookup["DISTANCE_MATRIX"]
        
        self.MAX_FTS = int(np.max(self.data_lookup["ORDER_DATA"]["MAX_FTS"]))
    
    def init_fts_infos(self):
        SETUP_TIMEs = self.data_lookup['FTS_DATA']["SETUP_TIME"] 
        IDs = self.data_lookup['FTS_DATA']["FTS_ID"] 
        NAMEs = self.data_lookup['FTS_DATA']["NAME"] 
        SPEEDs = self.data_lookup['FTS_DATA']["SPEED"] 
        NCRANE = self.NFTS
        fts_infos = []
        for i in range(self.NFTS):
            setup_time = SETUP_TIMEs[i]
            fts_info = { "fts_id": i, 
                        "fts_db_id": IDs[i],
                        "fts_name": NAMEs[i]  ,
                        'speed': SPEEDs[i], 
                        "order_ids" : [],
                        "ids":[], "end_times":[], "start_times":[], "demands":[], "process_times":[],
                        "fts_setup_time":setup_time/60,
                        "crane_setup_times": [],
                         "distances":[], 
                         "travel_times":[], 
                         "consumption_rates":[],
                         "operation_rates":[],
                         "crane_infos": [],
                         'fts':self.ftses[i]}
            fts_infos.append(fts_info)
        return fts_infos

    def init_ship_infos(self):
        NSHIP = self.NSHIP 
        ship_infos = []
        ORDER_DATA = self.data_lookup['ORDER_DATA']
        for ship_id in range(NSHIP):
            ship_info = {"ship_id": ship_id, 
                         "order_id": ORDER_DATA['ORDER_ID'][ship_id],
                         "ship_db_id": ORDER_DATA['CARRIER_ID'][ship_id],
                         "ship_name": ORDER_DATA['CARRIER'][ship_id],
                         "open_time": ORDER_DATA['ARRIVAL_TIME_HOUR'][ship_id], 
                         "due_time": ORDER_DATA['DUE_TIME_HOUR'][ship_id], 
                         "cargo_type":ORDER_DATA['CARGO'][ship_id], 
                         "penalty_rate":ORDER_DATA['PENALTY_RATE'][ship_id],
                         "reward_rate":ORDER_DATA['REWARD_RATE'][ship_id],
                        "demand":    ORDER_DATA['DEMAND'][ship_id], 
                        "categroy_name": 'export' if  ORDER_DATA['CATEGORY'][ship_id] else 'import', 
                        "maxFTS":  ORDER_DATA['MAX_FTS'][ship_id],
                        "fts_crane_ids":[], 
                        "fts_crane_demands":[], 
                        "fts_crane_enter_times":[],
                        "fts_crane_exit_times":[],  
                        "fts_crane_operation_times":[]}
            #print(ship_info)
            ship_infos.append(ship_info)
        return ship_infos
    
    def manual_assign(self, primitive_ship_infos):
        fts_infos = self.init_fts_infos()
        ship_infos = self.init_ship_infos()

        if self.NSHIP != len(primitive_ship_infos):
            raise ValueError("Number ship order not equal database.") 


        for i in range(len(primitive_ship_infos)):
            p_ship_info = primitive_ship_infos[i]
            order_id = p_ship_info['order_id']

            to_assign_ftes = p_ship_info["FTS"]

            ship_index =  next((index for index in range(self.NSHIP) if ship_infos[index]['order_id'] == order_id), -1)
            if  ship_index == -1:
                raise ValueError("Shoud found order_info.") 

            ship_info = ship_infos[ship_index]
            ship_id = ship_index

            ship = self.ships[ship_index]
            fts_ids = []
            for to_fts in to_assign_ftes:
                fts_id = to_fts["fts_id"]
                fts_index =  next((index for index in range(self.NFTS) if fts_infos[index]['fts_db_id'] == fts_id), None)
                fts_ids.append(fts_index)

    
            arrival_times = []
            distances = []
            travel_times = []
            isOverArrive = False
            fts_start_times = []
            fts_input = []
            for finx in fts_ids:
                fts_info = fts_infos[finx]
                fts = self.ftses[finx]
                distance, t_time, a_time, s_time = self.get_result_info(finx,  ship_index, fts_infos)
                fts_input.append(fts)
                fts_start_times.append(s_time)
                arrival_times.append(a_time)
                distances.append(distance)
                travel_times.append(t_time)

            print(s_time)
            temp_cranes = []
            due_time, fts_results = groups_assign(fts_input, fts_start_times, ship ) 
            tcost = 0  
            for v in range(len(fts_results)): 
                
                process_time = fts_results[v]['operation_time']
                conveted_fts_results = convert_result(fts_results[v])
                max_due_date = 0
                consumption_rate_fts = conveted_fts_results["avg_consumption_rate"] 
                process_rate_fts = conveted_fts_results["avg_operation_rate"] 
                for cfr in conveted_fts_results["crane_infos"]:
                    if len(cfr['finish_times']) == 0:
                        continue
                    max_due_date = max(max_due_date, max(cfr['finish_times']))
                
                fts_setup_time = fts_infos[fts_ids[v]]['fts_setup_time']
                process_time = max_due_date
                due_time = max_due_date + s_time + fts_setup_time
                delta = ship.closed_time - due_time
                tcost = consumption_rate_fts*conveted_fts_results["total_loads"] 
                
                if process_time < 0:
                    print("ERRRRRRRRRRRRRRRRRRRRRRRRR")
                
                #print("type crane", type(fts_results2[i]))
                temp_cranes.append({"fts_id":fts_ids[v] , "arrive_time": round(arrival_times[v], 2), 
                        "start_time":round(fts_start_times[v],2), "travel_time":round(travel_times[v],2), 
                        "consumption_rate":round(consumption_rate_fts,2), 
                        "distance":round(distances[v],2),"process_rate":process_rate_fts,
                        "process_time":round(process_time,4), "end_time":round(due_time,2),
                        "crane_infos": fts_results[v],
                        } )
                fts_delta_infos = temp_cranes
                isFound = False
                 
                if len(fts_delta_infos) > 0:
                    for fts_id in ship_info["fts_crane_ids"]:
                        fts_info = fts_infos[fts_id]
                        index = fts_info['order_ids'].index(order_id)
                        fts_info['ids'].pop(index)
                        fts_info['order_ids'].pop(index)
                        fts_info['start_times'].pop(index)
                        fts_info['process_times'].pop(index)
                        fts_info['end_times'].pop(index)
                        fts_info['demands'].pop(index)
                        fts_info['distances'].pop(index)
                        fts_info['travel_times'].pop(index)
                        fts_info['operation_rates'].pop(index)
                        fts_info['consumption_rates'].pop(index)
                        fts_info['crane_infos'].pop(index)
                    
                    ship_info["fts_crane_ids"].clear()
                    ship_info["fts_crane_demands"].clear()
                    ship_info["fts_crane_enter_times"].clear()
                    ship_info["fts_crane_exit_times"].clear()
                    ship_info["fts_crane_operation_times"].clear()
                
                for fts_delta_info in fts_delta_infos:
                    cid = fts_delta_info["fts_id"]
                    fts_info = fts_infos[cid]
                    converted_fts_infos = convert_result(fts_delta_info['crane_infos'])
                    #print(fts_delta_info['process_rate'], fts_delta_info['process_time'])
                    crane_demand = round(fts_delta_info['process_time']*fts_delta_info['process_rate'])
                    total_loads = converted_fts_infos['total_loads']
                    fts_info['ids'].append(ship_id)
                    fts_info['order_ids'].append(order_id)
                    fts_info['start_times'].append(fts_delta_info['start_time'])
                    fts_info['process_times'].append(fts_delta_info['process_time'])
                    fts_info['end_times'].append(fts_delta_info['end_time'])
                    fts_info['demands'].append(total_loads)
                    fts_info['distances'].append(fts_delta_info['distance'])
                    fts_info['travel_times'].append(fts_delta_info['travel_time'])
                    fts_info['consumption_rates'].append(converted_fts_infos['avg_consumption_rate'])
                    fts_info['operation_rates'].append(converted_fts_infos['avg_operation_rate'])
                    fts_info['crane_infos'].append(converted_fts_infos)
                    
                    if len(fts_info['demands']) != len(fts_info['consumption_rates']):
                        print("EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
                        print(fts_info['demands'], fts_info['consumption_rates'])
                    
                    ship_info["fts_crane_ids"].append(cid)
                    ship_info["fts_crane_demands"].append(crane_demand)
                    ship_info["fts_crane_enter_times"].append(fts_delta_info['start_time'])
                    ship_info["fts_crane_exit_times"].append(fts_delta_info['end_time'])
                    ship_info["fts_crane_operation_times"].append(fts_delta_info['process_time'])
                    
                
                #break
            #break
                if isFound:
                    break
        for v in range(self.NSHIP):
            ship_id = v
            if len(ship_infos[ship_id]["fts_crane_exit_times"]) == 0:
                continue
            #print(ship_infos[ship_id])
            exit_time = max(ship_infos[ship_id]["fts_crane_exit_times"])
            due_time = ship_infos[ship_id]["due_time"]
            ship_infos[ship_id]["delta_time"] = due_time-exit_time
        return fts_infos, ship_infos





    