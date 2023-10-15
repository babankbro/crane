import sys
sys.path.insert(0, "./utility")

from crane_utility import *
import numpy as np

class Decoder:
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
        
        
        self.D = self.NSHIP*self.NFTS + self.NSHIP
        self.WEIGHT_CRANE_SHIPs = []
        self.SHIP_WEIGHTs = (due_hours-self.MIN_TIME)/(np.max(due_hours)-self.MIN_TIME) 
        for i in range(self.NSHIP):
            self.WEIGHT_CRANE_SHIPs.append(0.5)
    
    
    def assign_crane(self, ship_info, fts_crane_codes, fts_crane_infos):
        ship_id = ship_info['ship_id']
        best_cranes = []
        min_due_date = 10000000
        open_time = ship_info["open_time"]
        due_time = ship_info["due_time"]
        demand = ship_info['demand']
        category = ship_info['categroy_name']
        cargo_name = ship_info['cargo_type']
        #print("SHIP DATA", open_time, due_time, demand, ship_size, cargo_type)
        isNewStart = False
        DM_lookup = self.data_lookup["DISTANCE_MATRIX"]
        i = 0

        minDelta = -1000000000000000000000000
        temp_best_cranes = []
        FTS_CRANE_RATE = self.data_lookup['CRANE_RATE']

        while i < len(fts_crane_codes)-1:
            #print(crane_id, crane_info)

            #case 1: single crane
            fts_crane_id = fts_crane_codes[i]
            i+=1
            fts_crane_info = fts_crane_infos[fts_crane_id]
            fts_name = fts_crane_info['fts_name']
            arrive_time = -1
            start_time = -1
            #process_rate =  FTS_CRANE_RATE.get_operation_rate_by_name(crane_name, category, cargo_name)
            #print(FTS_CRANE_RATE.)
            process_rate_fts = FTS_CRANE_RATE.get_operation_rate_by_fts_name(fts_name, category, cargo_name)
            consumption_rate_fts = FTS_CRANE_RATE.get_consumption_rate_by_fts_name(fts_name, category, cargo_name)
            process_time = demand/process_rate_fts
            travel_time = 0
            distance=0

            if len(fts_crane_info["ids"]) == 0:
                arrive_time = open_time
                start_time = arrive_time + fts_crane_info["fts_setup_time"]
                isNewStart = True
            else:
                #print("1, MANAGE LAST CRANE1 xxxxxxxxxxxxxxxxxxxxxxxxx")
                previous_ship = fts_crane_info['ids'][-1]
                previous_end_time =  fts_crane_info['end_times'][-1]
                distance = DM_lookup.get_carrier_distance(previous_ship, ship_id)
                travel_time =   distance/fts_crane_info['speed']
                arrive_time = previous_end_time + travel_time
                start_time = arrive_time + fts_crane_info["fts_setup_time"]
                if start_time < open_time:
                    start_time = open_time
            
            if start_time > due_time:
                continue

            end_time = start_time + process_time
            delta = due_time - end_time
            if delta > 0:
                #print("A:{0}->S:{1}->P:{2}->E{3}->D:{4} delta:{5}".format(arrive_time,  start_time, process_time, end_time, due_time, due_time-end_time))
                best_cranes = [{"crane_id":fts_crane_id , "arrive_time": round(arrive_time, 2), 
                                "start_time":round(start_time,2), "travel_time":round(travel_time,2), 
                                "consumption_rate":round(consumption_rate_fts,2), 
                                "distance":round(distance,2),"process_rate":process_rate_fts,
                                "process_time":round(process_time,4), "end_time":round(end_time,2)} ]
                
                break
            

            if minDelta < delta:
                minDelta = delta
                #print("Delta", minDelta, delta)
                temp_best_cranes = [{"crane_id":fts_crane_id , "arrive_time": round(arrive_time, 2), 
                                     "start_time":round(start_time,2), "travel_time":round(travel_time,2),  
                                     "consumption_rate":round(consumption_rate_fts,2),
                                "distance":round(distance,2),"process_rate":process_rate_fts,
                                "process_time":round(process_time,4), "end_time":round(end_time,2)}]
        
            

            j = 0
            isFound = False
            while i + j < len(fts_crane_codes): 
                fts_crane_id2 = fts_crane_codes[i + j]
                j+=1
                fts_crane_info2 = fts_crane_infos[fts_crane_id2]
                fts_name = fts_crane_info2['fts_name']
                process_rate_fts2 = FTS_CRANE_RATE.get_operation_rate_by_fts_name(fts_name, category, cargo_name)
                consumption_rate_fts2 = FTS_CRANE_RATE.get_consumption_rate_by_fts_name(fts_name, category, cargo_name)
                
                
                arrive_time2 = -1
                start_time2 = -1
                travel_time2 = 0
                distance2 = 0

                if len(fts_crane_info2["ids"]) == 0:
                    arrive_time2 = open_time
                    start_time2 = arrive_time2 + fts_crane_info2["fts_setup_time"]
                    isNewStart = isNewStart and True

                else:
                    previous_ship2 = fts_crane_info2['ids'][-1]
                    previous_end_time2 =  fts_crane_info2['end_times'][-1]
                    distance2 = DM_lookup.get_carrier_distance(previous_ship2, ship_id)
                    travel_time2 =   distance2/fts_crane_info2['speed']
                    arrive_time2 = previous_end_time2 + travel_time2
                    start_time2 = arrive_time2 + fts_crane_info2["fts_setup_time"]
                    if start_time2 < open_time:
                        start_time2 = open_time
                
                #---- start time
                #--- start time2
                min_start = min(start_time, start_time2)
                max_start = max(start_time, start_time2)
                delta_start_time = max_start - min_start 
                if start_time < start_time2:
                    share_process_time =  (demand - delta_start_time*process_rate_fts)/ (process_rate_fts + process_rate_fts2)
                    process_time = share_process_time + delta_start_time
                    process_time2 = share_process_time
                else:
                    share_process_time =  (demand - delta_start_time*process_rate_fts2)/ (process_rate_fts + process_rate_fts2)
                    process_time2 = share_process_time + delta_start_time
                    process_time = share_process_time
                end_time = start_time + process_time
                end_time2 = start_time2 + process_time2
                    
                if process_time2 < 0 or process_time < 0  :
                    #print("Errror ", process_time, process_time2)
                    continue


                if isNewStart:
                    #print("Break new")
                    best_cranes = [{"crane_id":fts_crane_id , "arrive_time": round(arrive_time, 2), 
                                    "start_time":round(start_time,2), "travel_time":round(travel_time,2),  
                                    "consumption_rate":round(consumption_rate_fts,2),
                                    "distance":round(distance,2),"process_rate":process_rate_fts,
                                    "process_time":round(process_time,4), "end_time":round(end_time,2)},
                                {"crane_id":fts_crane_id2 , "arrive_time": round(arrive_time2, 2), 
                                 "start_time":round(start_time2,2), "travel_time":round(travel_time2,2), 
                                 "consumption_rate":round(consumption_rate_fts2,2),
                                    "distance":round(distance2,2),"process_rate":process_rate_fts2,
                                    "process_time":round(process_time2,4), "end_time":round(end_time2,2)}]

                    #print("Crane 1 A:{0}->S:{1}->P:{2}->E{3}->D:{4} delta:{5}".format(arrive_time,  start_time, process_time, end_time, due_time, due_time-end_time))
                    #print("Crane 2 A:{0}->S:{1}->P:{2}->E{3}->D:{4} delta:{5}".format(arrive_time2,  start_time2, process_time2, end_time2, due_time, due_time-end_time2))
                    return best_cranes
                #print("start_time <= due_time", start_time, due_time)
                if start_time <= due_time and start_time2 < due_time:
                    isFound = True
                    break
                #print("loop here")
            
            if not isFound:
                continue

            #end_time = start_time + process_time
            delta = due_time - end_time
            if delta > 0:
                #print("Break new")
                best_cranes = [{"crane_id":fts_crane_id , "arrive_time": round(arrive_time, 2), 
                                "start_time":round(start_time,2), "travel_time":round(travel_time,2),  
                                "consumption_rate":round(consumption_rate_fts,2),
                                "distance":round(distance,2),"process_rate":process_rate_fts,
                                "process_time":round(process_time,4), "end_time":round(end_time,2)},
                            {"crane_id":fts_crane_id2 , "arrive_time": round(arrive_time2, 2),
                             "start_time":round(start_time2,2), "travel_time":round(travel_time2,2),  
                             "consumption_rate":round(consumption_rate_fts2,2),
                                "distance":round(distance2,2),"process_rate":process_rate_fts2,
                                "process_time":round(process_time2,4), "end_time":round(end_time2,2)}]

                #print("Crane 1 A:{0}->S:{1}->P:{2}->E{3}->D:{4} delta:{5}".format(arrive_time,  start_time, process_time, end_time, due_time, due_time-end_time))
                #print("Crane 2 A:{0}->S:{1}->P:{2}->E{3}->D:{4} delta:{5}".format(arrive_time2,  start_time2, process_time2, end_time2, due_time, due_time-end_time2))
                return best_cranes
            #print("DELTA2 ---------", due_time-end_time, crane_id, crane_id2)
            #print("3 Manange notNewStart!!     xxxxxxxxxxxxxxxxxxxxxxxxxx")

            if minDelta < delta:
                minDelta = delta
                #print("Delta", minDelta, delta)
                temp_best_cranes = [{"crane_id":fts_crane_id , "arrive_time": round(arrive_time, 2),
                                     "start_time":round(start_time,2), "travel_time":round(travel_time,2), 
                                     "consumption_rate":round(consumption_rate_fts,2),
                                "distance":round(distance,2),"process_rate":process_rate_fts,
                                "process_time":round(process_time,4), "end_time":round(end_time,2)},
                            {"crane_id":fts_crane_id2 , "arrive_time": round(arrive_time2, 2), 
                             "start_time":round(start_time2,2), "travel_time":round(travel_time2,2),  
                             "consumption_rate":round(consumption_rate_fts2,2),
                                "distance":round(distance2,2),"process_rate":process_rate_fts2,
                                "process_time":round(process_time2,4), "end_time":round(end_time2,2)}]
        

        if len(best_cranes) == 0:
            #print("4 Manange notNewStart!!     xxxxxxxxxxxxxxxxxxxxxxxxxx")
            #if len(temp_best_cranes)==0:
                #print("Error-------------------", ship_id)
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
                         "consumption_rates":[]}
            #print(crane_info)
            fts_infos.append(fts_info)
        return fts_infos

    def init_ship_infos(self):
        NSHIP = self.NSHIP 
        ship_infos = []
        ORDER_DATA = self.data_lookup['ORDER_DATA']
        for ship_id in range(NSHIP):
            ship_info = {"ship_id": ship_id, 
                         "ship_db_id": ORDER_DATA['CARRIER_ID'][ship_id],
                         "ship_name": ORDER_DATA['CARRIER'][ship_id],
                         "open_time": ORDER_DATA['ARRIVAL_TIME_HOUR'][ship_id], 
                         "due_time": ORDER_DATA['DUE_TIME_HOUR'][ship_id], 
                         "cargo_type":ORDER_DATA['CARGO'][ship_id], 
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
    
    
    def decode(self, xs):
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
        #for fts in fts_crane_infos:
            #print(fts)
        
        for i in range(self.NSHIP):
            ship_id = ship_order_ids[i]
            ship_info = ship_infos[ship_id]
            fts_code = fts_codes[ship_id]
            #print(ship_id, fts_code)

        

            crane_delta_infos = self.assign_crane(ship_info, fts_code, fts_crane_infos)
            #cargo_type = SHIP_TYPEs[ship_id]
            #print("--------------------------")
            #print(i+1, ship_id, crane_codes, len(crane_delta_infos), ship_info)
        
            if len(crane_delta_infos) == 0:
                #print("XXXXXXXXXXXXX")
                return None, None
                


            for crane_delta_info in crane_delta_infos:
                cid = crane_delta_info["crane_id"]
                crane_info = fts_crane_infos[cid]
                crane_demand = round(crane_delta_info['process_time']*crane_delta_info['process_rate'])
                crane_info['ids'].append(ship_id)
                crane_info['start_times'].append(crane_delta_info['start_time'])
                crane_info['process_times'].append(crane_delta_info['process_time'])
                crane_info['end_times'].append(crane_delta_info['end_time'])
                crane_info['demands'].append(crane_demand)
                crane_info['distances'].append(crane_delta_info['distance'])
                crane_info['travel_times'].append(crane_delta_info['travel_time'])
                crane_info['consumption_rates'].append(crane_delta_info['consumption_rate'])
                #print(crane_info)

                ship_info["fts_crane_ids"].append(cid)
                ship_info["fts_crane_demands"].append(crane_demand)
                ship_info["fts_crane_enter_times"].append(crane_delta_info['start_time'])
                ship_info["fts_crane_exit_times"].append(crane_delta_info['end_time'])
                ship_info["fts_crane_operation_times"].append(crane_delta_info['process_time'])
        return fts_crane_infos, ship_infos
        
        




if __name__ == "__main__":
    
    #data_lookup = create_data_lookup()
    data_lookup = load_data_lookup('./dataset/data2.json')
    decoder = Decoder(data_lookup)
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