import sys

sys.path.insert(0, "./utility")
sys.path.insert(0, "./decoder")
from route_algorithm import CraneProblem
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

from customized_route import *

#from utility.crane_utility import create_data_lookup
#from utility.lookup_data import create_order_data
def test_main():
    user_group = 3
    solution_id = 71
    mydb, mycursor = try_connect_db()
    data_lookup = create_data_lookup(isAll=True, group=user_group)
    
    decoder = DecoderV2(data_lookup)
    converter = OutputConverter(data_lookup)

    
    print("------------------------------- Get Schedule")
    print("--------------------------------------------")
    print("--------------------------------------------")
    primitive_ship_infos =  get_schedule(solution_id, np.min(data_lookup["ORDER_DATA"]["MIN_TIME_HOUR"]))
    for item in primitive_ship_infos:
        print(item)

    fts_crane_infos, ship_infos =  decoder.manual_assign(primitive_ship_infos)
  
    #for ci in fts_crane_infos:
        #print(ci)

    #print()
    #for si in ship_infos:
        #print(si)

    
    #global mydb, mycursor
    print("================================================")
    print("================================================")
    solution_id = 69
    mydb, mycursor = try_connect_db()
    db_insert = DBInsert(mycursor, mydb)
    db_insert.clear_solution(solution_id)
    
    result_json = converter.create_solution_schedule(solution_id, fts_crane_infos) 
    db_insert.insert_jsons(result_json)
    result_json = converter.create_crane_solution_schedule(solution_id, fts_crane_infos) 
    df_crane_solution = pd.DataFrame(result_json)
    #print(result_json)
    #print(df_crane_solution)
    print("++++++++++++++++++++++++++++++++++++++++++++++++")
    print("++++++++++++++++++++++++++++++++++++++++++++++++")
    db_insert.insert_crane_solution_schedule_jsons(result_json)
    result_json = converter.create_crane_solution(solution_id, fts_crane_infos, ship_infos) 
    db_insert.insert_crane_solution_jsons(result_json)
    
    
    result_json = converter.create_ship_solution_schedule(solution_id, ship_infos, df_crane_solution, data_lookup) 
    db_insert.insert_carrier_solution_jsons(result_json)

    total_demand = 0
    
    for ship_info in ship_infos:
        #continue
        print(ship_info['ship_id'], ship_info['ship_name'], ship_info['maxFTS'], ship_info['demand'],  ship_info['open_time'], 
              ship_info['due_time'], ship_info['fts_crane_ids'],
              ship_info['fts_crane_enter_times'], ship_info['fts_crane_exit_times']) 
        total_demand += ship_info['demand']
        if len(ship_info['fts_crane_enter_times']) > 0 and np.sum(np.array(ship_info['fts_crane_exit_times'][:1])
            - np.array(ship_info['fts_crane_enter_times'][:1])) < 0:
            print(ship_info)

    print(total_demand)
    print(np.sum(data_lookup["ORDER_DATA"]['DEMAND']))
    """"""

def test_ship_order():
    user_group = 3
    solution_id = 69
    mydb, mycursor = try_connect_db()
    data_lookup = create_data_lookup(isAll=True, group=user_group)
    
    decoder = DecoderV2(data_lookup)
    converter = OutputConverter(data_lookup)

    
    print("------------------------------- Get Schedule")
    print("--------------------------------------------")
    print("--------------------------------------------")
    primitive_ship_infos =  get_schedule(solution_id, np.min(data_lookup["ORDER_DATA"]["MIN_TIME_HOUR"]))
    for item in primitive_ship_infos:
        print(item)
        
def test_create_start_date_hour():
    user_group = 3
    solution_id = 69
    mydb, mycursor = try_connect_db()
    data_lookup = create_data_lookup(isAll=True, group=user_group)
    
    decoder = DecoderV2(data_lookup)
    converter = OutputConverter(data_lookup)

    
    print("------------------------------- Get Schedule")
    print("--------------------------------------------")
    print("--------------------------------------------")
    primitive_ship_infos =  get_schedule(solution_id, np.min(data_lookup["ORDER_DATA"]["MIN_TIME_HOUR"]))
    create_order_start_date_hour(primitive_ship_infos,
                                 np.min(data_lookup["ORDER_DATA"]["MIN_TIME_HOUR"]))

if __name__ == "__main__":
    test_create_start_date_hour()
    
    