import numpy as np
from pymoo.core.callback import Callback
from pymoo.optimize import minimize
from pymoo.algorithms.soo.nonconvex.brkga import BRKGA
from sklearn.metrics import accuracy_score
from pymoo.algorithms.soo.nonconvex.de import DE
import numpy as np
from pymoo.core.problem import ElementwiseProblem
import math
from pymoo.problems import get_problem
from pymoo.operators.sampling.lhs import LHS
from pymoo.optimize import minimize
from pymoo.termination import get_termination

class DecoderExp:
    def __init__(self, data_lookup) -> None:
        self.data_lookup = data_lookup
        self.NSHIP = data_lookup['NSHIP']
        self.NFTS = data_lookup['NFTS']
        
        
        self.arrival_times = np.zeros(self.NSHIP)
        self.due_times = np.ones(self.NSHIP)*1e9
        self.MIN_TIME = min(self.arrival_times)
        self.MAX_TIME = max(self.arrival_times)
        print(self.arrival_times)
        print(self.arrival_times)
        
    def get_ship_codes(self, xs):
        codes = []
        for i in range(self.NSHIP):
            k =  i*self.NFTS
            cs = np.argsort(xs[k:k+self.NFTS])
            codes.append(cs)
        return codes
    
    def init_fts_infos(self):
        #SETUP_TIMEs = self.data_lookup['FTS_DATA']["SETUP_TIME"] 
        #IDs = self.data_lookup['FTS_DATA']["FTS_ID"] 
        #NAMEs = self.data_lookup['FTS_DATA']["NAME"] 
        #SPEEDs = self.data_lookup['FTS_DATA']["SPEED"] 
        fts_infos = []
        for i in range(self.NFTS):
            setup_time = 0
            fts_info = {  "fts_id": i, 
                          "fts_db_id": i+1,
                           "fts_name": i+1  ,
                           'speed': 30, 
                          "ids":[], 
                          "end_times":[], 
                          "start_times":[], 
                          "demands":[], 
                          "process_times":[],
                          "fts_setup_time":0,
                          "crane_setup_times": [],
                         "distances":[], 
                         "travel_times":[], 
                         "consumption_rates":[],
                         "operation_rates":[],
                         "crane_infos": [],
                         'fts':None}
            fts_infos.append(fts_info)
        return fts_infos
    
    def init_ship_infos(self):
        NSHIP = self.NSHIP 
        ship_infos = []
        ORDER_DATA = self.data_lookup['ORDER_DATA']
        for ship_id in range(NSHIP):
            ship_info = {"ship_id": ship_id, 
                         "order_id": ship_id,
                         "ship_db_id": ORDER_DATA[ship_id].ship_id,
                         "ship_name": ORDER_DATA[ship_id].name,
                         "open_time": self.arrival_times[ship_id], 
                         "due_time": self.due_times[ship_id], 
                         #"cargo_type":0, 
                        # "penalty_rate":0,
                        # "reward_rate":0,
                        'maxFTS':ORDER_DATA[ship_id].maxFTS,
                        "demand":     ORDER_DATA[ship_id].load, 
                        #"categroy_name": 'export' if  ORDER_DATA['CATEGORY'][ship_id] else 'import', 
                        "fts_ids":[], 
                        "fts_demands":[], 
                        "fts_enter_times":[],
                        "fts_exit_times":[],  
                        "fts_operation_times":[]}
            #print(ship_info)
            ship_infos.append(ship_info)
        return ship_infos
    
    def get_result_info(self, fts_info, ship_info):
        ship_id=ship_info['ship_id']
        
        if len(fts_info['ids']) == 0:
            last_point_time = 0
            distance = 30
        else:
            last_ship_id = fts_info['ids'][-1]
            last_point_time = fts_info["end_times"][-1]
            distance = self.data_lookup['TRAVEL_TIME'][last_ship_id][ship_id]
        t_time =  distance
        a_time = last_point_time + t_time
        s_time = a_time if a_time > self.arrival_times[ship_id] else self.arrival_times[ship_id]
        return distance, t_time, a_time, s_time
    
    def groups_assign(self, fts_ids, fts_start_times, fts_infos, ship_info):
        ship_id = ship_info['ship_id']
        #print(fts_ids, fts_start_times)
        #print(ship_info)
        due_time = 0
        fts_results = []
        rates = self.data_lookup['OPERATION_RATE'][fts_ids, ship_id]
        st = np.array(fts_start_times)
        sr = st/rates
        due_time = (ship_info['demand'] + np.sum(sr))/np.sum(1/rates)
        
        for i, fts_id  in enumerate(fts_ids):
            s_time = fts_start_times[i]
            p_time = due_time - s_time
            fts_info = fts_infos[fts_id]
            if len(fts_info['ids']) == 0:
                t_time = 30
            else:
                t_time = self.data_lookup['TRAVEL_TIME'][fts_info['ids'][-1]][ship_id]
            
            if len(fts_info['ids']) == 0 and t_time != 30:
                print("UNKKKKKKKKKKKK", len(fts_info['ids']), t_time)
            result = {"fts_id": fts_id,
                      "start_time": fts_start_times[i],
                      "process_time": p_time,
                      "total_loads":p_time/ rates[i], 
                      "end_time": due_time,
                      "distance":t_time, 
                      "travel_time": t_time,
                      "operation_rate": rates[i],
                      }
            fts_results.append(result)
        
        return due_time, fts_results

        
    
    def assign_fts_ship(self, islastLevel, fts_codes, ship_id, ship_infos, fts_infos, isDebug):
        ship_info = ship_infos[ship_id]
        i = 0
        best_fts = []
        best_due_time = 1000000000000000000000000
        while i < len(fts_codes):
            ii = i
            i+=1
            findex = fts_codes[ii]
            fts_ids = list(ship_info['fts_ids'])
            if findex in fts_ids:
                continue
            distance, t_time, a_time, s_time = self.get_result_info(fts_infos[findex],  ship_info)
            
            
            
            fts_start_times = list(ship_info['fts_enter_times'])
            
            fts_ids.append(findex)
            fts_start_times.append(s_time)
            
            due_time, temp_best_fts = self.groups_assign(fts_ids, fts_start_times, fts_infos, ship_info )   
            
            isFalse = False
            for temp_fts in temp_best_fts:
                if temp_fts['process_time'] < 0:
                    isFalse = True
                    break
            if isFalse:
                continue
            
            if best_due_time > due_time:
                best_due_time = due_time
                best_fts = temp_best_fts
            if not islastLevel:
                break
        
        return best_fts
            
            
    
    def decode(self, xs, isDebug=False):
        #ship_order_ids = np.argsort(xs[:self.NSHIP])
        ship_order_ids = np.arange(self.NSHIP)
        fts_codes = self.get_ship_codes(xs[self.NSHIP:])
        #print(fts_codes)
        
        fts_infos = self.init_fts_infos()
        ship_infos = self.init_ship_infos()
        for fts in fts_infos:
            continue
            print(fts)
        for ship in ship_infos:
            continue
            print(ship)
        MAX_FTS = self.data_lookup["MAX_FTS"]
        for k in range(MAX_FTS):
            #print("============================================================================")
            for i in range(self.NSHIP):
                ship_id = ship_order_ids[i]
                ship_info = ship_infos[ship_id]
                fts_code = fts_codes[ship_id]
                
                if len(ship_info['fts_ids']) >= ship_info['maxFTS']:
                    continue
                isLast = (len(ship_info['fts_ids']) - 1) ==  ship_info['maxFTS']
                fts_delta_infos = self.assign_fts_ship(isLast, fts_code, ship_id,  ship_infos, 
                                                    fts_infos, isDebug)
                
                #print(fts_delta_infos)
                if i <= self.NSHIP - 1 and k == 0:
                    for delta in fts_delta_infos:
                        continue
                        print(delta)
                        
                if len(fts_delta_infos) > 0:
                    for fts_id in ship_info["fts_ids"]:
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
                    
                    ship_info["fts_ids"].clear()
                    ship_info["fts_demands"].clear()
                    ship_info["fts_enter_times"].clear()
                    ship_info["fts_exit_times"].clear()
                    ship_info["fts_operation_times"].clear()
                
                for fts_delta_info in fts_delta_infos:
                    cid = fts_delta_info["fts_id"]
                    fts_info = fts_infos[cid]
                    fts_info['ids'].append(ship_id)
                    fts_info['start_times'].append(fts_delta_info['start_time'])
                    fts_info['process_times'].append(fts_delta_info['process_time'])
                    fts_info['end_times'].append(fts_delta_info['end_time'])
                    fts_info['demands'].append(fts_delta_info['total_loads'])
                    fts_info['distances'].append(fts_delta_info['distance'])
                    fts_info['travel_times'].append(fts_delta_info['travel_time'])
                    #fts_info['consumption_rates'].append(converted_fts_infos['avg_consumption_rate'])
                    fts_info['operation_rates'].append(fts_delta_info['operation_rate'])
                    #print("update----------------------------------", fts_info['fts_id'])
                    """
                    if ship_id not in fts_info['ids']:
                        fts_info['ids'].append(ship_id)
                        fts_info['start_times'].append(fts_delta_info['start_time'])
                        fts_info['process_times'].append(fts_delta_info['process_time'])
                        fts_info['end_times'].append(fts_delta_info['end_time'])
                        fts_info['demands'].append(fts_delta_info['total_loads'])
                        fts_info['distances'].append(fts_delta_info['distance'])
                        fts_info['travel_times'].append(fts_delta_info['travel_time'])
                        #fts_info['consumption_rates'].append(converted_fts_infos['avg_consumption_rate'])
                        fts_info['operation_rates'].append(fts_delta_info['operation_rate'])
                    else:
                        if len(fts_info['ids']) == 1 and fts_delta_info['distance'] != 30:
                            #print (fts_info['fts_id'], fts_info['ids'], fts_info['distances'], fts_delta_info['distance'])
                            #print("ERRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
                            fts_delta_info['distance'] = 30
                            fts_delta_info['travel_time'] = 30
                        fts_info['start_times'][-1] = fts_delta_info['start_time']
                        fts_info['process_times'][-1] = fts_delta_info['process_time']
                        fts_info['end_times'][-1] = fts_delta_info['end_time']
                        fts_info['demands'][-1] = fts_delta_info['total_loads']
                        fts_info['distances'][-1] = fts_delta_info['distance']
                        fts_info['travel_times'][-1] = fts_delta_info['travel_time']
                    """
                    #fts_crane_info['crane_infos'].append(converted_fts_infos)
                    #print(crane_info)
                    
                    
                    ship_info["fts_ids"].append(cid)
                    ship_info["fts_demands"].append(fts_delta_info['total_loads'])
                    ship_info["fts_enter_times"].append(fts_delta_info['start_time'])
                    ship_info["fts_exit_times"].append(fts_delta_info['end_time'])
                    ship_info["fts_operation_times"].append(fts_delta_info['process_time'])
                    
                
                #break
            #break
        return fts_infos, ship_infos
                