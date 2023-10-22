import sys
from crane_configuration import *
from ship_assign import *
sys.path.insert(0, "./utility")

from crane_utility import *
import numpy as np
import pandas as pd

CASE_GROUP = {
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
    
    if nfts == 1:
        result = single_group_case(ftses[0], ship, start_times[0], bulks)
        fts_results.append(result)
        return result['due_time'], fts_results
    
    else:
        min_due_time = 1000000000000000000
        groups = CASE_GROUP[nbulk][nfts]
        
        for group in groups:
            due_time, results = group_case(group, ftses, ship, start_times, bulks)
            if due_time < min_due_time:
                min_due_time = due_time
                fts_results = results
                print(min_due_time, group)
            
    return min_due_time, fts_results
    
        

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
   