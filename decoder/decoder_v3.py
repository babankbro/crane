import sys
from crane_configuration import *
from ship_assign import *
from crane_decoder import *
sys.path.insert(0, "./utility")

from crane_utility import *
from output_converter import *
import numpy as np
import pandas as pd

class DecoderV3:
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
    
    
    def get_result_info(self, findex,  ship_index, fts_crane_infos):
        ship = self.ships[ship_index]
        fts_crane_info = fts_crane_infos[findex]
        if len(fts_crane_info['ids']) == 0:
            last_point_time = -100
            distance = self.DM_lookup.get_fts_distance(findex, ship_index)
        else:
            last_point_time = -100
            distance = self.DM_lookup.get_fts_distance(findex, ship_index)
            for k in range(len(fts_crane_info['ids'])):
                if ship_index == fts_crane_info['ids'][-(1+k)]:
                    continue
                last_ship_id = fts_crane_info['ids'][-(1+k)]
                last_point_time = fts_crane_info["end_times"][-(1+k)]
                distance = self.DM_lookup.get_carrier_distance(last_ship_id, ship_index) 
                break
                if last_point_time < ship.open_time:
                    break
                #else:
                    #print("Here")
            
        t_time =  distance/fts_crane_info['speed']
        a_time = last_point_time + t_time
        s_time = a_time if a_time > ship.open_time else ship.open_time
        return distance, t_time, a_time, s_time
    
    def assign_fts_ship(self, islastLevel, fts_codes, ship_id, ship_infos, fts_infos, isDebug=False):
        ship_info = ship_infos[ship_id]
        ship = self.ships[ship_id]
        i = 0
        best_fts = []
        best_due_time = 1000000000000000000000000
        #if ship_id == 19:
            #print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        while i < len(fts_codes):
            ii = i
            i+=1
            findex = fts_codes[ii]
            fts_ids = list(ship_info['fts_crane_ids'])
            #if ship_id == 19:
                #print(findex, fts_ids)
            if findex in fts_ids:
                continue
            
            
            #for i
            
            fts_ids.append(findex)
            fts_input = []
            fts_start_times = []
            arrival_times = []
            distances = []
            travel_times = []
            isOverArrive = False
            for finx in fts_ids:
                fts_info = fts_infos[finx]
                fts = self.ftses[finx]
                distance, t_time, a_time, s_time = self.get_result_info(finx,  ship_id, fts_infos)
                #if a_time > ship.closed_time:
                    #isOverArrive = True
                    #break
                fts_input.append(fts)
                fts_start_times.append(s_time)
                arrival_times.append(a_time)
                distances.append(distance)
                travel_times.append(t_time)
            if isOverArrive:
                #print("isOverArrive", isOverArrive)
                continue
            #if len(fts_ids) <= 2:
                #print("fts_start_times",fts_start_times)
                #print("arrival_times", arrival_times)
             
            temp_cranes = []
            due_time, fts_results = groups_assign(fts_input, fts_start_times, ship )   
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
                
            
           
            isFalse = False
            for temp_fts in temp_cranes:
                is_interset = False
                fts_info = fts_infos[temp_fts['fts_id']]
                #if temp_fts['fts_id'] == 5 :
                    #print('check ###############################', fts_info['ids'])
                
                if len(fts_info['ids']) == 0:
                    #print(fts_info['fts_id'], fts_info['ids'], "eeeeeeeeeee")
                    continue
                for ik, sid in enumerate(fts_info['ids']):
                    if sid == ship_id:
                        continue
                    if ((temp_fts['end_time'] > fts_info['start_times'][ik] and 
                        temp_fts['end_time'] < fts_info['end_times'][ik]) or 
                        (temp_fts['start_time'] > fts_info['start_times'][ik] and 
                        temp_fts['start_time'] < fts_info['end_times'][ik])   or 
                        (fts_info['end_times'][ik] > temp_fts['start_time'] and 
                        fts_info['end_times'][ik] <  temp_fts['end_time'] and True) or 
                        (fts_info['start_times'][ik] > temp_fts['start_time'] and 
                        fts_info['start_times'][ik] <  temp_fts['end_time']and True)):
                        is_interset = True
                        break
                if (temp_fts['process_time'] < 0 or 
                    temp_fts['start_time'] > temp_fts['end_time'] or 
                    is_interset):
                    isFalse = True
                    
                    break
            
            if ship_info['order_id'] == 19:
                
                #print(fts_info)
                #pass
                print("not completed! --------------------------------------------------------------")
                print(fts_infos[fts_ids[-1]]['fts_db_id'], len(fts_ids), is_interset, fts_infos[fts_ids[-1]]['ids'])  
                for temp_fts in temp_cranes:
                    #if temp_fts['fts_id'] == 5:
                    #fts_info = fts_infos[temp_fts['fts_id']]
                    print("temp_fts", temp_fts)
                    print(is_interset, fts_info["start_times"], fts_info["end_times"], fts_info['speed'])
                    
            
            if isFalse:
                #print("********************************")
                continue
            else:
                if len(fts_ids) == 2:
                    pass
                    #print("CCCCCCCCCCCCCCCCCCCCC********************************")
                    
            
             
            
            if ship_info['order_id'] == 19:
                print("best_due_time", best_due_time, due_time)
            if best_due_time > due_time:
                best_due_time = due_time
                best_fts = temp_cranes
            #if not islastLevel:
                #break
        
        return best_fts
    
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
            fts_info = { "fts_id": i, 
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
    
    def decode(self, xs, isDebug=False):
        ship_order_ids = np.argsort(self.data_lookup['ORDER_DATA']['ARRIVAL_TIME_HOUR'])
        fts_codes = self.get_ship_codes(xs[:])
        fts_infos = self.init_fts_infos()
        ship_infos = self.init_ship_infos()
        print("ship_order_ids", len(ship_order_ids), ship_order_ids, 
              len(self.data_lookup['ORDER_DATA']['ARRIVAL_TIME_HOUR']), self.data_lookup['ORDER_DATA']['ARRIVAL_TIME_HOUR'])
        for fts_code in fts_codes:
            print(fts_code)
        
        for i in range(self.NSHIP):
            #print("============================================================================")
            for k in range(self.MAX_FTS):
                
                ship_id = ship_order_ids[i]
                ship_info = ship_infos[ship_id]
                fts_code = fts_codes[ship_id]
                
                if (len(ship_info['fts_crane_ids'])> 0 and 
                       (ship_info['due_time'] - max(ship_info["fts_crane_exit_times"])) * ship_info["penalty_rate"] >= 0 ) :
                    print(" Done =====================================================",
                          ship_id, ship_info['due_time'] , max(ship_info["fts_crane_exit_times"]))
                    continue
                    
                if len(ship_info['fts_crane_ids']) >= ship_info['maxFTS']: #:
                    continue
                isLast = (len(ship_info['fts_crane_ids']) - 1) ==  ship_info['maxFTS']
                fts_delta_infos = self.assign_fts_ship(isLast, fts_code, ship_id,  
                                                       ship_infos, fts_infos, isDebug)
                
                isFound = False
                if i <= self.NSHIP - 1 and k == 0:
                    #print(fts_delta_infos)
                    for delta in fts_delta_infos:
                        continue
                        print("EEEEEEEE -------------------------------------")
                        print(delta)
                        #isFound = True
                #print("SHIP", ship_id, k, len(fts_delta_infos), "---------------------")    
                if len(fts_delta_infos) > 0:
                    for fts_id in ship_info["fts_crane_ids"]:
                        fts_info = fts_infos[fts_id]
                        index = fts_info['ids'].index(ship_id)
                        fts_info['ids'].pop(index)
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
                    
                    crane_demand = round(fts_delta_info['process_time']*fts_delta_info['process_rate'])
                    total_loads = converted_fts_infos['total_loads']
                    fts_info['ids'].append(ship_id)
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
            ship_id = ship_order_ids[v]
            if len(ship_infos[ship_id]["fts_crane_exit_times"]) == 0:
                continue
            print(ship_infos[ship_id])
            exit_time = max(ship_infos[ship_id]["fts_crane_exit_times"])
            due_time = ship_infos[ship_id]["due_time"]
            ship_infos[ship_id]["delta_time"] = due_time-exit_time
        return fts_infos, ship_infos
        
        
        return {}, {}
       
        """
        
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
            #if len(ship_infos[ship_id]["fts_crane_exit_times"]) == 0:
                #continue
            exit_time = max(ship_infos[ship_id]["fts_crane_exit_times"])
            due_time = ship_infos[ship_id]["due_time"]
            ship_infos[ship_id]["delta_time"] = due_time-exit_time
 
        return fts_crane_infos, ship_infos
        """


if __name__ == "__main__":
    
    data_lookup = create_data_lookup(isAll=True)
    #data_lookup = load_data_lookup('./dataset/data2.json')
    decoder = DecoderV3(data_lookup)
    DM_lookup = data_lookup["DISTANCE_MATRIX"]
    print(pd.DataFrame(data_lookup['FTS_DATA']))
    print(pd.DataFrame(data_lookup['ORDER_DATA']))
    print(pd.DataFrame(data_lookup['CRANE_RATE'].crane_rate_df))
    print(DM_lookup.index_lookup)
    np.random.seed(0)
    xs = np.random.rand(decoder.D)
    #xs = np.load("./dataset/xs_v2.npy")
    converter = OutputConverter(data_lookup)
    
    crane_infos, ship_infos = decoder.decode(xs)
    
    print("----------------------------   SHIPS --------------------------------------------")
    for ship_info in ship_infos:
        continue
        print(ship_info)
    
    print("-------------------------- CRANES  -------------------------------------------")
    
    fts_infos = converter.create_solution_schedule(0, crane_infos)
    
    for crane_info in crane_infos:
        continue
        print(crane_info)
        date_str = '2023-02-28 14:30:00'
        date_format = '%Y-%m-%d %H:%M:%S'
        #crane_info['delta'] = (datetime.strptime(crane_info['exittime'], date_format) - 
        #                       datetime.strptime(crane_info['arrivaltime'], date_format))
    print()
    
    
    
    
    df = pd.DataFrame(fts_infos)
    #print(df)
    
    print(DM_lookup.DM.shape)
    print(DM_lookup.get_carrier_distance(10, 12))
    
    
    print("----------------------------   FTS --------------------------------------------")
    for fts_info in crane_infos:
        continue
        print(fts_info)
        print()
        
    print("----------------------------   SHIPS --------------------------------------------")
    for ship_info in ship_infos:
        #continue
        print(ship_info['ship_id'], ship_info['maxFTS'], ship_info['demand'],  ship_info['open_time'], ship_info['due_time'], ship_info['fts_crane_ids'],
              ship_info['fts_crane_enter_times'], ship_info['fts_crane_exit_times'])
    
    print("Test utility")
    print(data_lookup["APPROVED_ORDER_DATA"])