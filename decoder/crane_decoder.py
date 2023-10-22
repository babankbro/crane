import sys
from crane_configuration import *
sys.path.insert(0, "./utility")

from crane_utility import *
import numpy as np
import pandas as pd

class Ship:
    def __init__(self, lookup) -> None:
        self.lat = lookup['LAT']
        self.lng = lookup['LNG']
        self.open_time = lookup['ARRIVAL_TIME_HOUR']
        self.closed_time =  lookup['DUE_TIME_HOUR']
        self.total_demand = lookup['DEMAND']
        self.category = 'import' if lookup['CATEGORY'] else 'export'
        self.name = lookup['CARRIER']
        self.cargos = [lookup['CARGO']]
        self.cargo = self.cargos[0]
        self.number_bulk= lookup['BULK']
        self.number_bulks = [self.number_bulk] 
        self.load_bulks = []
        for i in range(self.number_bulk):
            self.load_bulks.append( round(self.total_demand/self.number_bulk, 2))
            
    def __str__(self):
        return f""" {self.name}  open-closed: {round(self.open_time, 2)} - {round(self.closed_time, 2)}  {self.load_bulks} """
            
CASE_LOOK_UPX = { 
                #"C2-B1-T1": {"NCRANE":2, "NBULK": 1, "INDEX": [[0, 1]]},
                "C2-B1-T1": {"NCRANE":2, "NBULK": 1, "INDEX": [[0]]},
                "C2-B1-T2": {"NCRANE":2, "NBULK": 1, "INDEX": [[1]]},
                
                "C2-B2-T1": {"NCRANE":2, "NBULK": 2, "INDEX":[[0], [1]]},
                "C2-B3-T1": {"NCRANE":2, "NBULK": 3, "INDEX":[[0], [0], [1]]},
                "C2-B3-T2": {"NCRANE":2, "NBULK": 3, "INDEX":[[0], [1], [1]]},
                "C2-B4-T1": {"NCRANE":2, "NBULK": 4, "INDEX":[[0], [0], [1], [1]]},
                "C3-B1-T1": {"NCRANE":3, "NBULK": 1, "INDEX": [[0]]},
                "C3-B1-T2": {"NCRANE":3, "NBULK": 1, "INDEX": [[1]]},
                "C3-B1-T3": {"NCRANE":3, "NBULK": 1, "INDEX": [[2]]},
                "C3-B2-T1": {"NCRANE":3, "NBULK": 2, "INDEX":[[0], [1]]},
                "C3-B2-T2": {"NCRANE":3, "NBULK": 2, "INDEX":[[1], [2]]},
                "C3-B2-T3": {"NCRANE":3, "NBULK": 2, "INDEX":[[0], [2]]},
                #"C3-B1-T1": {"NCRANE":3, "NBULK": 1, "INDEX":[[0, 1, 2]]},
                #"C3-B2-T1": {"NCRANE":3, "NBULK": 2, "INDEX":[[0, 1], [2]]},
                #"C3-B2-T2": {"NCRANE":3, "NBULK": 2, "INDEX":[[0], [1, 2]]},
                "C3-B3-T1": {"NCRANE":3, "NBULK": 3, "INDEX":[[0], [1], [2]]},
                "C3-B4-T1": {"NCRANE":3, "NBULK": 4, "INDEX":[[0], [0], [1], [2]]},
                "C3-B4-T2": {"NCRANE":3, "NBULK": 4, "INDEX":[[0], [1], [1], [2]]},
                "C3-B4-T3": {"NCRANE":3, "NBULK": 4, "INDEX":[[0], [1], [2], [2]]},
                "C3-B5-T1": {"NCRANE":3, "NBULK": 5, "INDEX":[[0], [0], [1], [2], [2]]},
                "C3-B5-T2": {"NCRANE":3, "NBULK": 5, "INDEX":[[0], [0], [1], [1], [2]]},
                "C3-B5-T3": {"NCRANE":3, "NBULK": 5, "INDEX":[[0], [1], [1], [2], [2]]},
                "C3-B6-T1": {"NCRANE":3, "NBULK": 6, "INDEX":[[0], [0], [1], [1], [2], [2]]},
                }

CASE_LOOK_UP = { 
                "C2-B1-T1": {"NCRANE":2, "NBULK": 1, "INDEX": [[0, 1]]},
                "C2-B2-T1": {"NCRANE":2, "NBULK": 2, "INDEX":[[0], [1]]},
                "C2-B3-T1": {"NCRANE":2, "NBULK": 3, "INDEX":[[0], [0], [1]]},
                "C2-B3-T2": {"NCRANE":2, "NBULK": 3, "INDEX":[[0], [1], [1]]},
                "C2-B4-T1": {"NCRANE":2, "NBULK": 4, "INDEX":[[0], [0], [1], [1]]},
                "C3-B1-T1": {"NCRANE":3, "NBULK": 1, "INDEX": [[0]]},
                "C3-B1-T1": {"NCRANE":3, "NBULK": 1, "INDEX":[[0, 1, 2]]},
                "C3-B2-T1": {"NCRANE":3, "NBULK": 2, "INDEX":[[0, 1], [2]]},
                "C3-B2-T2": {"NCRANE":3, "NBULK": 2, "INDEX":[[0], [1, 2]]},
                "C3-B3-T1": {"NCRANE":3, "NBULK": 3, "INDEX":[[0], [1], [2]]},
                "C3-B4-T1": {"NCRANE":3, "NBULK": 4, "INDEX":[[0], [0], [1], [2]]},
                "C3-B4-T2": {"NCRANE":3, "NBULK": 4, "INDEX":[[0], [1], [1], [2]]},
                "C3-B4-T3": {"NCRANE":3, "NBULK": 4, "INDEX":[[0], [1], [2], [2]]},
                "C3-B5-T1": {"NCRANE":3, "NBULK": 5, "INDEX":[[0], [0], [1], [2], [2]]},
                "C3-B5-T2": {"NCRANE":3, "NBULK": 5, "INDEX":[[0], [0], [1], [1], [2]]},
                "C3-B5-T3": {"NCRANE":3, "NBULK": 5, "INDEX":[[0], [1], [1], [2], [2]]},
                "C3-B6-T1": {"NCRANE":3, "NBULK": 6, "INDEX":[[0], [0], [1], [1], [2], [2]]},
                }

def compute_step_process_time(case, fts, ship, sbulks):
    info = CASE_LOOK_UP[case]
    
    INDEX = info["INDEX"]
    
    
    max_otime = 0
    results =  []
    for i in range(len(fts.cranes)):
        crane = fts.cranes[i]
        orate = crane.get_rates(ship.cargo, ship.category)['operation_rate']
        row = {
            "bulks":[], 
            'loads':[],
            'crane':i,
            'opearation_times':[],
            "opearation_rate":orate
        }
        results.append(row)
    
    
    for k in range(len(INDEX)):
        index = INDEX[k]
        cid = index[0]
        crane = fts.cranes[cid]
        bulk = sbulks[k]
        load = ship.load_bulks[bulk]
        otime = round(load/orate, 2)
        orate = crane.get_rates(ship.cargo, ship.category)['operation_rate']
        if len(index) == 1:
            row = results[cid]
            row["bulks"].append(bulk)
            row["loads"].append(load)
            row["opearation_times"].append(otime)
        else:
            for i in range(1, len(index)):
                cid = index[i]
                crane = fts.cranes[cid]
                orate += crane.get_rates(ship.cargo, ship.category)['operation_rate']
            otime = round(load/orate, 2)
            for i in range(len(index)):
                cid = index[i]
                row = results[i]
                row["bulks"].append(bulk)
                crane = fts.cranes[cid]
                corate =  crane.get_rates(ship.cargo, ship.category)['operation_rate']
                load = otime*corate
                row["loads"].append(load)
                row["opearation_times"].append(otime)
    
    max_otime = sum(results[0]["opearation_times"])
    for i in range(1, len(results)):
        max_otime = max(max_otime, sum(results[i]["opearation_times"]))
     
    return max_otime, results


def compute_process_times(case, fts, ship, bulks):
    info = CASE_LOOK_UP[case]
    step_nbulk = info["NBULK"]
    ncrane = len(fts.crane_lookup)
    crane_key = f"C{ncrane}"
    nbulk = len(bulks)
    steps = []
    for i in range(0, nbulk, step_nbulk):
        sbulks = bulks[i:i+ step_nbulk]
        
        if len(sbulks) == step_nbulk:
            
            otime, result = compute_step_process_time(case, fts, ship, sbulks)
            steps.append([otime, result])
            #print("STEP RIGHT", sbulks, otime)
        else:
            
            min_time = 10000000000000000000000
            min_result=None
            for key in CASE_LOOK_UP:
                info = CASE_LOOK_UP[key]
                if crane_key in key and len(sbulks) == info["NBULK"]:
                    
                    otime, result = compute_step_process_time(key, fts, ship, sbulks)
                    if min_time > otime:
                        min_time = otime
                        min_result = result
                    #print("\t", key, otime)
            steps.append([min_time, min_result])
            #print("STEP DOWN", sbulks, min_time)
    total_time = steps[0][0]
    for i in range(1, len(steps)):
        total_time += MOVE_TIME_FTS
        total_time += steps[i][0]
    return total_time, steps
                    
            
    

def generate_fts_ship_solution(fts, ship, bulks):
    ncrane = len(fts.crane_lookup)
    crane_key = f"C{ncrane}"
    nbulk = len(bulks)
    min_time = 10000000000000000000000
    min_result=None
    for key in CASE_LOOK_UP:
        info = CASE_LOOK_UP[key]
        if crane_key in key and nbulk >= info["NBULK"]:
            #compute_process_times
            
            o_time, steps = compute_process_times(key, fts, ship, bulks)
            if min_time > o_time:
                min_time = o_time
                min_result = steps
    return min_time, min_result
        
        



if __name__ == "__main__":
    
    #data_lookup = create_data_lookup()
    data_lookup = load_data_lookup('./dataset/data_10.json')
    df = pd.DataFrame(data_lookup['ORDER_DATA'])
    fts_rate_lookups = data_lookup['CRANE_RATE'].lookup_fts_ids
    
    #print(df)
    for i in range(len(df)):
        ship = Ship(df.iloc[i])
        break
        #print(ship)
        
    for key in fts_rate_lookups:
        fts_rate = fts_rate_lookups[key]
        fts_rate.set_display_rate('ถ่านหิน', 'import')
        
        break
        #print(fts_rate)
    bulks = []
    for i in range(ship.number_bulk):
        bulks.append(i)
    min_time, min_result = generate_fts_ship_solution(fts_rate, ship, bulks)
    print("Operation Time", min_time)
    for result in min_result:
        print(result)
    print(ship.total_demand)
    print("Test utility")