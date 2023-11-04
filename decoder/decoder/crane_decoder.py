import sys
from crane_configuration import *
from ship_assign import *
sys.path.insert(0, "./utility")

from crane_utility import *
import numpy as np
import pandas as pd

CASE_GROUP = {
    2: {
        1: [[2]],
        2: [[1], [1]]
    },
    3: {1: [[3]],
        2: [[2, 1], [1, 2]],
        3: [[1, 1, 1]]
    },
    4: {
        1: [[4]],
        2: [[2, 2], [3, 1]],
        3: [[2, 1, 1]],
        4: [[1, 1, 1, 1]],
    }, 
    5: {
        1: [[5]],
        2: [[3, 2], [4, 1]],
        3: [[2, 2, 1], [3, 1, 1]],
        4: [[2, 1, 1, 1]],
    },
    6: {
        1: [[6]],
        2: [[3, 3], [4, 2], [5, 1]],
        3: [[2, 2, 2], [3, 2, 1], [4, 1, 1]],
        4: [[2, 2, 1, 1], [3, 1, 1, 1]],
    },
    7: {
        1: [[7]],
        2: [[4, 3], [5, 2], [6, 1]],
        3: [[3, 2, 2], [3, 3, 1], [4, 2, 1], [5, 1, 1]],
        4: [[2, 2, 2, 1], [3, 2, 1, 1], [4, 1, 1, 1]],
    },
    8: {
        1: [[8]],
        2: [[4, 4], [5, 3], [6, 2] , [7, 1]],
        3: [[3, 3, 2], [4, 3, 1], [5, 2, 1], [6, 1, 1]],
        4: [[2, 2, 2, 2], [3, 2, 2, 1], [3, 3, 1, 1], [4, 2, 1, 1], [5, 1, 1, 1]],
    },
    9: {
        1: [[9]],
        2: [[5, 4], [6, 3], [7, 2] , [8, 1]],
        3: [[3, 3, 3], [4, 3, 2], [5, 2, 2], [6, 2, 1], [7, 1, 1]],
        4: [[3, 2, 2, 2], [3, 3, 2, 1], [4, 3, 1, 1], [5, 2, 1, 1], [6, 1, 1, 1]],
    },
    10: {
        1: [[10]],
        2: [[5, 5], [6, 4], [7, 3] , [8, 2], [9, 1]],
        3: [[4, 3, 3], [4, 4, 2], [5, 3, 2], [5, 4, 1], [6, 2, 2], [6, 3, 1], [7, 2, 1], [8, 1, 1]],
        4: [[3, 3, 2, 2], [4, 3, 2, 1], [4, 4, 1, 1], [5, 3, 1, 1], [6, 2, 1, 1]],
    }
    
}

def single_group_case(fts, ship, start_time, bulks):
    o_time, step_moves = generate_fts_ship_solution(fts, ship, bulks)
    due_time =start_time + o_time
    return {
        "fts_name":fts.name,
        "fts":fts,
        "ship":ship,
        "operation_time":o_time,
        "steps":step_moves,
        "start_time":start_time,
        'due_time': due_time,
        
    }
    
def group_case(group, ftses, ship, start_times, bulks):
    group_bulks = []
    st= 0
    due_time = 0
    results = []
    max_due_time = 0
    for i in range(len(group)):
        n = group[i]
        cbulks = bulks[st:st+n]
        group_bulks.append(cbulks)
        st += n
        info = single_group_case(ftses[i], ship, start_times[i], cbulks)
        results.append(info)
        if due_time < info['due_time']:
            due_time = info['due_time']
    
    return due_time, results

def groups_assign(ftses, start_times, ship):
    nfts = len(ftses)
    nbulk = ship.number_bulk
    bulks = []
    fts_results = []
    for i in range(ship.number_bulk):
        bulks.append(i)
    
    if nfts == 1 or (nfts==2 and nbulk==1):
        result = single_group_case(ftses[0], ship, start_times[0], bulks)
        fts_results.append(result)
        return result['due_time'], fts_results
    
    else:
        min_due_time = 1000000000000000000
  
        #print(nbulk, nfts)
        groups = CASE_GROUP[nbulk][nfts]
        for group in groups:
            due_time, results = group_case(group, ftses, ship, start_times, bulks)
            if due_time < min_due_time:
                min_due_time = due_time
                fts_results = results
                #print(min_due_time, group)
            
    return min_due_time, fts_results

def convert_result(fts_info):
    steps = fts_info["steps"]
    fts = fts_info["fts"]
    ship = fts_info["ship"]
    crane_infos = []
    ncrane = len(fts.crane_lookup)
    for i in range(ncrane):
        crane_infos.append({ 
                            "bulks":[],
                            'ship':ship,
                            'fts':fts,
                            'loads': [],
                            'operation_times':[],
                            'offset_start_times':[],
                            'waiting_start_times':[],
                            'finish_times':[],
                            'operation_rate':0,
                            'consumption_rate':0,
                            'total_loads':0,
                            "crane_index":i,
                            })
        
    nstep = len(steps)
    for step in steps:
        step_time, each_steps = step
        for crane_step in each_steps:
            #print(crane)
            crane_index = crane_step['crane']
            crane_info = crane_infos[crane_index]
            crane_info['bulks'].extend(crane_step['bulks'])
            crane_info['loads'].extend(crane_step['loads'])
            crane_info['operation_times'].extend(crane_step['operation_times'])
            crane_info['operation_rate'] = crane_step['operation_rate']
            crane_info['consumption_rate'] = crane_step['consumption_rate']
    
    max_step = 0  
    for i in range(ncrane):  
         max_step = max(max_step, len(crane_infos[i]['bulks']))
    
    max_step_times = []
    for s in range(max_step):
        max_step_time = 0
        for i in range( ncrane):
            if len(crane_infos[i]['operation_times']) <= s:
                continue
            #print(s, i, crane_infos[i]['operation_times'])
            max_step_time = max(max_step_time, crane_infos[i]['operation_times'][s])
        max_step_times.append(max_step_time)
    
    max_finish_times = []
    for s in range(max_step):  
        max_finish_time = 0   
        for i in range( ncrane):
            if len(crane_infos[i]['operation_times']) <= s:
                continue
            if s == 0:
                crane_infos[i]['offset_start_times'].append(0)
                crane_infos[i]['finish_times'].append(crane_infos[i]['operation_times'][0])
                crane_infos[i]['waiting_start_times'].append(max_step_times[0] - crane_infos[i]['operation_times'][0])
            else:
                s_time = max_finish_times[-1]
                f_time = s_time+crane_infos[i]['operation_times'][s]
                crane_infos[i]['offset_start_times'].append(s_time)
                crane_infos[i]['finish_times'].append(f_time)
                crane_infos[i]['waiting_start_times'].append(max_step_times[s] - crane_infos[i]['operation_times'][s])
            max_finish_time = max(max_finish_time, crane_infos[i]['finish_times'][-1])
        max_finish_times.append(max_finish_time)
        
        
            
    fts_load = 0
    avg_consumption_rate = 0
    avg_operation_rate = 0
    for i in range(ncrane):
        crane_infos[i]['total_loads'] = sum(crane_infos[i]['loads'])
        fts_load += crane_infos[i]['total_loads']
        avg_consumption_rate += crane_info['consumption_rate']*crane_infos[i]['total_loads']
        avg_operation_rate += crane_info['operation_rate']*crane_infos[i]['total_loads']
    avg_consumption_rate /= fts_load
    avg_operation_rate /= fts_load
    return {
        "fts_name":fts.name,
        "ship":ship,
        "fts" : fts,
        'total_loads':fts_load,
        "crane_infos":crane_infos, 
        'avg_consumption_rate': avg_consumption_rate,
        'avg_operation_rate': avg_operation_rate
    }

if __name__ == "__main__":
    
    #data_lookup = create_data_lookup()
    data_lookup = load_data_lookup('./dataset/data_10.json')
    df = pd.DataFrame(data_lookup['ORDER_DATA'])
    fts_rate_lookups = data_lookup['CRANE_RATE'].lookup_fts_ids
    
    #print(df)
    ships = []
    for i in range(len(df)):
        ship = Ship(df.iloc[i])
        ships.append(ship)
        #print(ship)
    
    ftses = []
    for key in fts_rate_lookups:
        fts_rate = fts_rate_lookups[key]
        fts_rate.set_display_rate('ถ่านหิน', 'import')
        ftses.append(fts_rate)
   