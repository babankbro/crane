import sys
from crane_configuration import *

from ship_assign import *
from crane_decoder import *
from decoder_v2 import *
sys.path.insert(0, "./utility")

from crane_utility import *
import numpy as np
import pandas as pd
from output_converter import *
from insert_db_api import DBInsert


def single_fts_assign(ships, ftses):
        #print(fts_rate)
    ship = ships[0]
    bulks = []
    for i in range(ship.number_bulk):
        bulks.append(i)
    min_time, min_result = generate_fts_ship_solution(ftses[2], ships[0], bulks)
    print("Operation Time", min_time)
    for result in min_result:
        #print(result)
        #converted_data = convert_result(result)
        #print(converted_data)
        continue
    
    due_time, fts_results = groups_assign([ftses[0]], [0], ships[0] )    
    print("due_time", due_time)
    for result in fts_results:
        print(result)
        converted_data = convert_result(result)
    
    print("--------------------------")
    due_time, fts_results = groups_assign([ftses[0]], [20], ships[0] )    
    print("due_time", due_time)
    for result in fts_results:
        continue
        print(result)
    
    print("Test utility")
    
def test_group_assign(ships, ftses):
    ship = ships[0]
    bulks = []
    for i in range(ship.number_bulk):
        bulks.append(i)
    
    print("-------------------------- 2")
    due_time, fts_results = groups_assign([ftses[0], ftses[1]], [0, 100], ships[0] )    
    print("due_time", due_time)
    for result in fts_results:
        print(result)
    
    print("-------------------------- ")
    due_time, fts_results = groups_assign([ftses[0], ftses[1], ftses[2]], [0, 50, 30], ships[0] )    
    print("due_time", due_time)
    for result in fts_results:
        print(result)
        
    print("--------------------------")
    due_time, fts_results = groups_assign([ftses[0], ftses[1], ftses[2], ftses[3]], [0, 30, 30, 0], ships[0] )    
    print("due_time", due_time)
    for result in fts_results:
        print(result)

def test_decoder():
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
    
    #print(DM_lookup.DM.shape)
    #print(DM_lookup.get_carrier_distance(10, 12))

def test_group_assign_invert(ships, ftses):
    ship = ships[0]
    bulks = []
    for i in range(ship.number_bulk):
        bulks.append(i)
    
    print('ship load', ship.total_demand)
    print("-------------------------- 2")
    #due_time, fts_results = groups_assign([ftses[0], ftses[6]], [0, 100], ships[0] )  
    due_time, fts_results = groups_assign([ftses[0]], [0], ships[0] )      
    print("due_time", due_time)
    for result in fts_results:
        #print(result)
        #print(result)
        converted_data = convert_result(result)
        print(converted_data)
        
def test_output_crane_schedule_convert():
    data_lookup = load_data_lookup('./dataset/data_10.json')
    converter = OutputConverter(data_lookup)
    decoder = DecoderV2(data_lookup)
    DM_lookup = data_lookup["DISTANCE_MATRIX"]
    #print(pd.DataFrame(data_lookup['FTS_DATA']))
    #print(pd.DataFrame(data_lookup['ORDER_DATA']))
    #print(pd.DataFrame(data_lookup['CRANE_RATE'].crane_rate_df))
    #print(DM_lookup.index_lookup)
    np.random.seed(0)
    xs = np.random.rand(decoder.D)
    fts_infos, ship_infos = decoder.decode(xs, True)
    result_json = converter.create_crane_solution_schedule(1, fts_infos)
    db_insert = DBInsert(mycursor, mydb)
    db_insert.clear_table("solution_crane_schedule", 1)
    db_insert.insert_crane_solution_schedule_jsons(result_json)
    #for js in result_json:
        #continue
        #print(js) 
        
def test_output_crane_cost_convert():
    data_lookup = load_data_lookup('./dataset/data_10.json')
    converter = OutputConverter(data_lookup)
    decoder = DecoderV2(data_lookup)
    DM_lookup = data_lookup["DISTANCE_MATRIX"]
    #print(pd.DataFrame(data_lookup['FTS_DATA']))
    #print(pd.DataFrame(data_lookup['ORDER_DATA']))
    #print(pd.DataFrame(data_lookup['CRANE_RATE'].crane_rate_df))
    #print(DM_lookup.index_lookup)
    np.random.seed(0)
    xs = np.random.rand(decoder.D)
    fts_infos, ship_infos = decoder.decode(xs, True)
    result_json = converter.create_crane_solution(1, fts_infos)
    for js in result_json:
        print(js)
    db_insert = DBInsert(mycursor, mydb)
    db_insert.clear_table("crane_solution", 1)
    db_insert.insert_crane_solution_jsons(result_json)


if __name__ == "__main__":
    
    data_lookup = create_data_lookup()
    save_data_lookup('./dataset/data_10.json', data_lookup)
    #data_lookup = load_data_lookup('./dataset/data_10.json')
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
    print("len ships", len(ships), len(ftses))
    #test_group_assign(ships, ftses)
    print("--------------------------------------------- Single Assign ----------------------------------")
    #single_fts_assign(ships, ftses)
    print()
    
    print("--------------------------------------------- Group Assign ----------------------------------")
    #test_group_assign(ships, ftses)
    #test_group_assign_invert(ships, ftses)
    
    print('--------------------------------------------- Test Decode -----------------------------------')
    test_output_crane_cost_convert()
    