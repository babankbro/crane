import sys






sys.path.insert(0, "./utility")
sys.path.insert(0, "./decoder")

from crane_utility import *
from crane_configuration import *
from ship_assign import *
from crane_decoder import *
from decoder_v2 import *
import numpy as np
import pandas as pd
from output_converter import *
from insert_db_api import DBInsert
from output_converter import OutputConverter
#from utility.crane_utility import create_data_lookup
#from utility.lookup_data import create_order_data


if __name__ == "__main__":
    
    data_lookup = create_data_lookup()
    
    #order_data = create_order_data(["M.V.MARVELLOUS"])
    #order_data = create_order_data(["M.V.CL PEKING"])
    order_data = create_order_data(["M.V.EPIC HARMONY"])
    #print(order_data)
    fts_data = create_fts_data(["ศุภราช"])
 
    
    #data_lookup["ORDER_DATA"] = order_data
    #data_lookup["FTS_DATA"] = fts_data
    #print(fts_data)
    decoder = DecoderV2(data_lookup)
    DM_lookup = data_lookup["DISTANCE_MATRIX"]
    #print(pd.DataFrame(data_lookup['FTS_DATA']))
    #print(pd.DataFrame(data_lookup['ORDER_DATA']))
    #print(pd.DataFrame(data_lookup['CRANE_RATE'].crane_rate_df))
    #print(DM_lookup.index_lookup)
    np.random.seed(0)
    xs = np.random.rand(decoder.D)
    print('-------------- SHIPS')
    for i, ship in enumerate(decoder.ships):
        print(i, ship.total_demand)
    
    fts_infos, ship_infos = decoder.decode(xs, True)
    print("-------------------------- CRANES  -------------------------------------------")
    #print(fts_infos)
    for fts_info in fts_infos:
        #continue
        if len(fts_info['ids']) == 0:
            continue
        print("---------------------------------")
        print(fts_info['fts'].name)
        print(fts_info['ids'])
        print('demands', fts_info['demands'])
        print('consumption_rates', fts_info['consumption_rates'])
        print('operation_rates', fts_info['operation_rates'])
        print('crane_setup_times', fts_info['crane_setup_times'])
        #print(type(fts_info['crane_infos']))
        #print(fts_info['crane_infos'])
        for crane_info in fts_info['crane_infos']:
            #print(type(crane_info))
            #print(type(crane_info))
            #print(crane_info)
            continue
            for item in crane_info:
                print()
                steps = item['steps']
                for step in steps:
                    print(step)
    print()
    print("----------------------------   SHIPS --------------------------------------------")
    for ship_info in ship_infos:
        continue
        print(ship_info)
    
    print()
    print("---------------FTS--------------------")
    converter = OutputConverter(data_lookup)
    result_json = converter.create_solution_schedule(1, fts_infos) 
    for r_json in result_json:
        if r_json['operation_rate'] == None:
            continue
        
        print("Insert -----", r_json["operation_time"])
        
    print()
    print()
    result_json = converter.create_crane_solution_schedule(1, fts_infos) 
    for r_json in result_json:
        continue
        print(r_json)
        
    #print(order_data)
    
