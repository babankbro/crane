import sys
from crane_configuration import *
from ship_assign import *
from crane_decoder import *
sys.path.insert(0, "./utility")

from crane_utility import *
import numpy as np
import pandas as pd

class DecoderV2:
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
        print("MIN-MAX", self.MIN_TIME, self.MAX_TIME)
        
        df = pd.DataFrame(data_lookup['ORDER_DATA'])
        fts_rate_lookups = data_lookup['CRANE_RATE'].lookup_fts_ids
        
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
    
    
    def get_result_info(self, findex,  ship_index, fts_crane_infos):
        ship = self.ships[ship_index]
        fts_crane_info = fts_crane_infos[findex]
        if len(fts_crane_info['ids']) == 0:
            last_point_time = -100
            distance = self.DM_lookup.get_fts_distance(findex, ship_index)
        else:
            last_ship_id = fts_crane_info['ids'][-1]
            last_point_time = fts_crane_info["end_times"][-1]
            distance = self.DM_lookup.get_carrier_distance(last_ship_id, ship_index)
        t_time =  distance/fts_crane_info['speed']
        a_time = last_point_time + t_time
        s_time = a_time if a_time > ship.open_time else ship.open_time
        return distance, t_time, a_time, s_time
    
    
    def assign_fts_ship(self, ship_index, fts_codes, fts_crane_infos, isDebug=False):
        ship = self.ships[ship_index]
        best_cranes = []
        min_due_date = 10000000
        #print(f"{ship.name} {ship.open_time} - {ship.closed_time}")
        minDelta = -1000000000000000000000000
        temp_best_cranes = []
        i = 0
        while i < len(fts_codes):
            #print("decode ================", i)
            ii = i
            i+=1
            findex = fts_codes[ii]
            fts = self.ftses[findex]
            distance, t_time, a_time, s_time = self.get_result_info(findex,  ship_index, fts_crane_infos)
            
            if a_time > ship.closed_time:
                continue
            fts_input = [fts]
            start_times = [s_time]
            due_time, fts_results = groups_assign(fts_input, start_times, ship )   
            
            conveted_fts_results = convert_result(fts_results[0])
            max_due_date = 0
            #print(conveted_fts_results)
            for cfr in conveted_fts_results["crane_infos"]:
                if len(cfr['finish_times']) == 0:
                    continue
                max_due_date = max(max_due_date, max(cfr['finish_times']))
            
            process_time = max_due_date
            due_time = max_due_date + s_time
            delta = ship.closed_time - due_time
            
            if process_time < 0:
                print("ERRRRRRRRRRRRRRRRRRRRRRRRR")
            
            consumption_rate_fts = -1
            process_rate_fts = -1
            
            #if process_time > 0:
                #print("Errror", due_time, s_time)
            
            
            temp_best_cranes = [{"fts_id":findex , "arrive_time": round(a_time, 2), 
                                "start_time":round(s_time,2), "travel_time":round(t_time,2), 
                                "consumption_rate":round(consumption_rate_fts,2), 
                                "distance":round(distance,2),"process_rate":process_rate_fts,
                                "process_time":round(process_time,4), "end_time":round(due_time,2),
                                "crane_infos": fts_results[0],
                                } ]
            
            if delta > 0  :
                #if ship_index == 15:
                #print(ship_index, ship, "delta===================================",delta)
                break
            test = [ #7, #5, 9, 10
                    ]
                    
            if ship.id in test:
                print(findex, f"======================== {ship.id}",delta)
            
            if minDelta < delta:
                minDelta = delta
                best_cranes = temp_best_cranes 
            
                
            j = 1
            isFound = False
            temp_best_cranes = []
            while j < len(fts_codes): 
                jj = j
                j+=1
                k = jj

                if ii == k:
                    #print(i, k)
                    continue
                
                findex2 = fts_codes[k]
                distance2, t_time2, a_time2, s_time2 = self.get_result_info(findex2,  ship_index, fts_crane_infos)
                
                if ship.id in test:
                    print(i, k, findex, findex2)
                
                fts2 = self.ftses[findex2]
                fts_input = [fts, fts2]
                start_times = [s_time, s_time2]
                distances = [distance, distance2]
                travel_times = [t_time, t_time2]
                arrival_times = [a_time, a_time2]
                fts_indexs = [findex, findex2]
                #print("fts_input", len(fts_input))
                due_time2, fts_results2 = groups_assign(fts_input, start_times, ship )   
                isNewStart = ((len(fts_crane_infos[findex]['ids']) == 0) and 
                             (len(fts_crane_infos[findex2]['ids']) == 0))
                
                temp_cranes = []
                for v in range(len(fts_results2)):
                    consumption_rate_fts = -1
                    process_rate_fts = -1
                    process_time = -1
                    #print(fts_results2[i]['steps'])
                    #print(fts_results2[i]['fts_name'])
                    #for step in fts_results2[i]['steps']:
                        #for crane in step[1]:
                            #print(crane)
                    process_time = fts_results2[v]['operation_time']
                    
                    
                    conveted_fts_results = convert_result(fts_results2[v])
                    max_due_date = 0
                    #print(conveted_fts_results)
                    for cfr in conveted_fts_results["crane_infos"]:
                        if len(cfr['finish_times']) == 0:
                            continue
                        max_due_date = max(max_due_date, max(cfr['finish_times']))
                    
                    process_time = max_due_date
                    due_time = max_due_date + s_time
                    delta = ship.closed_time - due_time
                    
                    if process_time < 0:
                        print("ERRRRRRRRRRRRRRRRRRRRRRRRR")
                    
                    
                    #print("type crane", type(fts_results2[i]))
                    temp_cranes.append({"fts_id":fts_indexs[v] , "arrive_time": round(arrival_times[v], 2), 
                            "start_time":round(start_times[v],2), "travel_time":round(travel_times[v],2), 
                            "consumption_rate":round(consumption_rate_fts,2), 
                            "distance":round(distances[v],2),"process_rate":process_rate_fts,
                            "process_time":round(process_time,4), "end_time":round(due_time,2),
                            "crane_infos": fts_results2[v],
                            } )
                
                #if isNewStart:
                    #print("Exist ===========================")
                    #return temp_cranes
                
                if start_times[0] >= ship.closed_time and start_times[1] >= ship.closed_time:
                    isFound = True
                    #print(start_times, ship.closed_time)
                    continue
                
                delta = ship.closed_time - due_time2
                
                if ship.id in test:
                    print(findex, findex2, "L2======================== {ship.id}",delta, due_time2, ship.closed_time)
                if minDelta < delta:
                    minDelta = delta
                    best_cranes = temp_cranes
                    #best_cranes = temp_best_cranes
                    
            #print("")
                
            #if isFound:
                #break
            
            
        
        if len(best_cranes) == 0:
            return temp_best_cranes
        
        
        return best_cranes
    
    
    def get_ship_codes(self, xs):
        codes = []
        for i in range(self.NSHIP):
            k =  i*self.NFTS
            #w = self.WEIGHT_CRANE_SHIPs[i] 
            #cs = np.argsort(xs[i*self.NFTS:(i+1)*self.NFTS]*self.WFTS+  (1-self.WFTS)*w)
            cs = np.argsort(xs[k:k+self.NFTS])
            codes.append(cs)
        return codes

    def init_fts_infos(self):
        SETUP_TIMEs = self.data_lookup['FTS_DATA']["SETUP_TIME"] 
        IDs = self.data_lookup['FTS_DATA']["FTS_ID"] 
        NAMEs = self.data_lookup['FTS_DATA']["NAME"] 
        SPEEDs = self.data_lookup['FTS_DATA']["SPEED"] 
        NCRANE = self.NFTS
        fts_infos = []
        for i in range(self.NFTS):
            setup_time = SETUP_TIMEs[i]
            fts_info = {  "fts_id": i, 
                          "fts_db_id": IDs[i],
                           "fts_name": NAMEs[i]  ,
                           'speed': SPEEDs[i], 
                          "ids":[], "end_times":[], "start_times":[], "demands":[], "process_times":[],
                          "fts_setup_time":setup_time/60,
                          "crane_setup_times": [],
                         "distances":[], 
                         "travel_times":[], 
                         "consumption_rates":[],
                         "operation_rates":[],
                         "crane_infos": [],
                         'fts':self.ftses[i]}
            #print(crane_info)
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
                        "fts_crane_ids":[], 
                        "fts_crane_demands":[], 
                        "fts_crane_enter_times":[],
                        "fts_crane_exit_times":[],  
                        "fts_crane_operation_times":[]}
            #print(ship_info)
            ship_infos.append(ship_info)
        return ship_infos
    
    def decode(self, xs, isDebug=False):
        #ARRIVAL_TIME_HOUR
        
        #ship_ids = np.argsort(xs[:self.NSHIP]*self.WSHIP + (1-self.WSHIP)*self.SHIP_WEIGHTs)
        ship_order_ids = np.argsort(self.data_lookup['ORDER_DATA']['DUE_TIME_HOUR'])
        fts_codes = self.get_ship_codes(xs[self.NSHIP:])
        fts_crane_infos = self.init_fts_infos()
        #print(ship_order_ids)
        #print(crane_infos)
        
        
        ship_infos = self.init_ship_infos()
        #for ship in ship_infos:
            #print(ship)
        if isDebug:
            i = 0
            for fts in fts_crane_infos:
                continue
                #print(fts)
                #print(self.ftses[i])
                #i+=1
            #print("------------------------------")
            #print(ship_order_ids)
            for i in range(self.NSHIP):
                continue
                #ship_info = ship_infos[i]
                #print(ship_info)
                #print(self.ships[i])
        
        
        for i in range(self.NSHIP):
            ship_id = ship_order_ids[i]
            ship_info = ship_infos[ship_id]
            fts_code = fts_codes[ship_id]
            #print(ship_id, fts_code)

            fts_delta_infos = self.assign_fts_ship(ship_id, fts_code, fts_crane_infos, isDebug)
            #cargo_type = SHIP_TYPEs[ship_id]
            #print("--------------------------")
            #print(i+1, ship_id, crane_codes, len(crane_delta_infos), ship_info)
            #continue
            if len(fts_delta_infos) == 0:
                #print("XXXXXXXXXXXXX")
                continue
            
            #print(crane_delta_infos[0]['crane_infos'])
            
            for fts_delta_info in fts_delta_infos:
                cid = fts_delta_info["fts_id"]
                fts_crane_info = fts_crane_infos[cid]
                
                converted_fts_infos = convert_result(fts_delta_info['crane_infos'])
                
                crane_demand = round(fts_delta_info['process_time']*fts_delta_info['process_rate'])
                fts_crane_info['ids'].append(ship_id)
                fts_crane_info['start_times'].append(fts_delta_info['start_time'])
                fts_crane_info['process_times'].append(fts_delta_info['process_time'])
                fts_crane_info['end_times'].append(fts_delta_info['end_time'])
                fts_crane_info['demands'].append(converted_fts_infos['total_loads'])
                fts_crane_info['distances'].append(fts_delta_info['distance'])
                fts_crane_info['travel_times'].append(fts_delta_info['travel_time'])
                fts_crane_info['consumption_rates'].append(converted_fts_infos['avg_consumption_rate'])
                fts_crane_info['operation_rates'].append(converted_fts_infos['avg_operation_rate'])
                fts_crane_info['crane_infos'].append(converted_fts_infos)
                #print(crane_info)

                ship_info["fts_crane_ids"].append(cid)
                ship_info["fts_crane_demands"].append(crane_demand)
                ship_info["fts_crane_enter_times"].append(fts_delta_info['start_time'])
                ship_info["fts_crane_exit_times"].append(fts_delta_info['end_time'])
                ship_info["fts_crane_operation_times"].append(fts_delta_info['process_time'])
                
        for i in range(self.NSHIP):
            ship_id = ship_order_ids[i]
            exit_time = max(ship_infos[ship_id]["fts_crane_exit_times"])
            due_time = ship_infos[ship_id]["due_time"]
            ship_infos[ship_id]["delta_time"] = due_time-exit_time
 
        return fts_crane_infos, ship_infos
         


if __name__ == "__main__":
    
    #data_lookup = create_data_lookup()
    data_lookup = load_data_lookup('./dataset/data2.json')
    decoder = DecoderV2(data_lookup)
    DM_lookup = data_lookup["DISTANCE_MATRIX"]
    print(pd.DataFrame(data_lookup['FTS_DATA']))
    print(pd.DataFrame(data_lookup['ORDER_DATA']))
    print(pd.DataFrame(data_lookup['CRANE_RATE'].crane_rate_df))
    print(DM_lookup.index_lookup)
    np.random.seed(0)
    xs = np.random.rand(decoder.D)
    
    
    crane_infos, ship_infos = decoder.decode(xs)
    print("-------------------------- CRANES  -------------------------------------------")
    for crane_info in crane_infos:
        print(crane_info)
    print()
    print("----------------------------   SHIPS --------------------------------------------")
    for ship_info in ship_infos:
        print(ship_info)
    
    print(DM_lookup.DM.shape)
    print(DM_lookup.get_carrier_distance(10, 12))
    
    print("Test utility")