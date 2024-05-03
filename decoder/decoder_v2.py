import sys
from crane_configuration import *
from ship_assign import *
from crane_decoder import *
sys.path.insert(0, "./utility")

from crane_utility import *
from output_converter import *
import numpy as np
import pandas as pd
from base_decoder import BaseDecoder

class DecoderV2(BaseDecoder):
    def __init__(self, data_lookup):
        super().__init__(data_lookup)
    
    def get_result_info2(self, findex,  ship_index, fts_crane_infos):
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
        tta = 0
        deltacc = 0
        #print("------------------------", fts_codes)
        while i < len(fts_codes):
            #print("decode ================", i, len(temp_best_cranes))
            ii = i
            i+=1
            findex = fts_codes[ii]
            fts = self.ftses[findex]
            if len(self.data_lookup["FTS_ID_IS_ACTIVE"]) != 0 and fts.id not in self.data_lookup["FTS_ID_IS_ACTIVE"]:
                continue
            distance, t_time, a_time, s_time = self.get_result_info_base(findex,  ship_index, fts_crane_infos, -1000)
            
            if a_time > ship.closed_time:
                tta += 1
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
            
            #print(type(fts))
            #print(fts)
            fts_setup_time = fts_crane_infos[findex]['fts_setup_time']
            process_time = max_due_date
            due_time = max_due_date + s_time + fts_setup_time
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
            #print("\ttemp_best_cranes", len(temp_best_cranes), findex)
            
            if delta > 0  :
                #print("\tbreak")
                deltacc += 1
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
            
            while j < len(fts_codes): 
                jj = j
                j+=1
                k = jj

                if ii == k:
                    #print(i, k)
                    continue
                
                findex2 = fts_codes[k]
                distance2, t_time2, a_time2, s_time2 = self.get_result_info_base(findex2,  ship_index, fts_crane_infos, -1000)
                
                if ship.id in test:
                    print(i, k, findex, findex2)
                
                fts2 = self.ftses[findex2]
                
                if len(self.data_lookup["FTS_ID_IS_ACTIVE"]) != 0 and  fts2.id not in self.data_lookup["FTS_ID_IS_ACTIVE"]:
                    continue
                
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
                    
                    fts_setup_time = fts_crane_infos[fts_indexs[v]]['fts_setup_time']
                    process_time = max_due_date
                    due_time = max_due_date + start_times[v] + fts_setup_time
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
                if minDelta < delta and len(temp_cranes) != 0:
                    minDelta = delta
                    best_cranes = temp_cranes
                    
                    #best_cranes = temp_best_cranes
                    
            #print("")
                
            #if isFound:
                #break
            
        #if len(best_cranes) == 0 and len(temp_best_cranes):
            #print(deltacc, ship, tta, tta == len(fts_crane_infos))
        
        
        #print("temp_best_cranesssssssssssss", temp_best_cranes)
        if len(best_cranes) == 0:
            #print("temp_best_cranes", ship.id, temp_best_cranes, deltacc, tta)
            #print('end_time', temp_best_cranes[0]['end_time'])
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

    def decode(self, xs, isDebug=False):
        #ARRIVAL_TIME_HOUR
        
        #ship_ids = np.argsort(xs[:self.NSHIP]*self.WSHIP + (1-self.WSHIP)*self.SHIP_WEIGHTs)
        ship_order_ids = np.argsort(self.data_lookup['ORDER_DATA']['DUE_TIME_HOUR'])
        fts_codes = self.get_ship_codes(xs[:])
        
        fts_infos = self.init_fts_infos()
        #print(ship_order_ids)
        #print(crane_infos)
        #print("fts_crane_infos", len(fts_crane_infos), len(fts_codes), len(fts_codes[0]))
        
        ship_infos = self.init_ship_infos()
        #for ship in ship_infos:
            #print(ship)
        if isDebug:
            i = 0
            for fts in fts_infos:
                continue
                #print(fts)
                #print(self.ftses[i])
                #i+=1
            #print("------------------------------")
            #print(ship_order_ids)
            for i in range(self.NSHIP):
                continue
                ship_info = ship_infos[i]
                #print(ship_info)
                #print(self.ships[i])
                ship_id = ship_order_ids[i]
                ship_info = ship_infos[ship_id]
                fts_code = fts_codes[ship_id]
                
                order_id = ship_info["order_id"]
                #print(ship_id, fts_code)
            #print("------------------------------")
        
        
        for i in range(self.NSHIP):
            ship_id = ship_order_ids[i]
            ship_info = ship_infos[ship_id]
            fts_code = fts_codes[ship_id]
            order_id = ship_info["order_id"]
            #print(ship_id, fts_code)

            fts_delta_infos = self.assign_fts_ship(ship_id, fts_code, fts_infos, isDebug)
            #cargo_type = SHIP_TYPEs[ship_id]
            #print("--------------------------")
            #print(i+1, ship_id, crane_codes, len(crane_delta_infos), ship_info)
            #continue
            isFound = False
            if len(fts_delta_infos) == 0:
                #print("XXXXXXXXXXXXX")
                continue
            
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
            ship_id = ship_order_ids[v]
            if len(ship_infos[ship_id]["fts_crane_exit_times"]) == 0:
                continue
            #print(ship_infos[ship_id])
            exit_time = max(ship_infos[ship_id]["fts_crane_exit_times"])
            due_time = ship_infos[ship_id]["due_time"]
            ship_infos[ship_id]["delta_time"] = due_time-exit_time
        return fts_infos, ship_infos
         

if __name__ == "__main__":
    
    user_group = 3
    solution_id = 56
    mydb, mycursor = try_connect_db()
    data_lookup = create_data_lookup(isAll=True, group=user_group)
    #data_lookup = load_data_lookup('./dataset/data2.json')
    decoder = DecoderV2(data_lookup)
    DM_lookup = data_lookup["DISTANCE_MATRIX"]
    print(pd.DataFrame(data_lookup['FTS_DATA']))
    print(pd.DataFrame(data_lookup['ORDER_DATA']))
    print(pd.DataFrame(data_lookup['CRANE_RATE'].crane_rate_df))
    print(DM_lookup.index_lookup)
    np.random.seed(0)
    xs = np.random.rand(decoder.D)
    converter = OutputConverter(data_lookup)
    
    crane_infos, ship_infos = decoder.decode(xs)
    
    print("----------------------------   SHIPS --------------------------------------------")
    for ship_info in ship_infos:
        #continue
        print(ship_info)
    
    print("-------------------------- CRANES  -------------------------------------------")
    
    fts_infos = converter.create_solution_schedule(0, crane_infos)
    
    for crane_info in crane_infos:
        #continue
        print(crane_info)
        date_str = '2023-02-28 14:30:00'
        date_format = '%Y-%m-%d %H:%M:%S'
        #crane_info['delta'] = (datetime.strptime(crane_info['exittime'], date_format) - 
        #                       datetime.strptime(crane_info['arrivaltime'], date_format))
    print()
    
    df = pd.DataFrame(fts_infos)
    print(df)
    
    print(DM_lookup.DM.shape)
   # print(DM_lookup.get_carrier_distance(10, 12))
    
    print("Test utility")