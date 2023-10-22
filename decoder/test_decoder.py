import sys
from crane_configuration import *
from ship_assign import *
from crane_decoder import *
from decoder_v2 import *
sys.path.insert(0, "./utility")

from crane_utility import *
import numpy as np
import pandas as pd


def single_fts_assign(ships, ftses):
        #print(fts_rate)
    ship = ships[0]
    bulks = []
    for i in range(ship.number_bulk):
        bulks.append(i)
    min_time, min_result = generate_fts_ship_solution(ftses[0], ships[0], bulks)
    print("Operation Time", min_time)
    for result in min_result:
        print(result)
    
    due_time, fts_results = groups_assign([ftses[0]], [0], ships[0] )    
    print("due_time", due_time)
    for result in fts_results:
        print(result)
    
    print("--------------------------")
    due_time, fts_results = groups_assign([ftses[0]], [20], ships[0] )    
    print("due_time", due_time)
    for result in fts_results:
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
    
    
    crane_infos, ship_infos = decoder.decode(xs)
    print("-------------------------- CRANES  -------------------------------------------")
    for crane_info in crane_infos:
        continue
        print(crane_info)
    print()
    print("----------------------------   SHIPS --------------------------------------------")
    for ship_info in ship_infos:
        continue
        print(ship_info)
    
    #print(DM_lookup.DM.shape)
    #print(DM_lookup.get_carrier_distance(10, 12))
    
    


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
    print("len ships", len(ships), len(ftses))
    #test_group_assign(ships, ftses)
    test_decoder()
    