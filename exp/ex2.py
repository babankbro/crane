import pandas as pd
import numpy as np
import sys
sys.path.insert(0, "./exp")
from decoder import  DecoderExp
from fts_problem import *
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

class Order:
    def __init__(self, ship_id, name, maxFTS, qauntity) -> None:
        self.ship_id = ship_id
        self.name = name
        self.maxFTS = maxFTS
        self.load = qauntity
    
    def __str__(self) -> str:
        return f"id: {self.ship_id}\tname:{self.name}\tmax FTS:{self.maxFTS}\t load:{self.load}"
        

temp_solution_schedule_json = { 
                               "solution_id": 0, "FTS_id": 0, "carrier_id": 0, 
                               'lat': 0, 'lng': 0, "arrivaltime": '2023-01-01 00:00:00',
                               "exittime": '2023-01-01 00:00:00', 
                               "operation_time":1440, "Setup_time": 150, 
                               "travel_Distance": 0, "travel_time": 0, 
                               "operation_rate": 700, "consumption_rate":0,
                               "penalty_time":0, 'labor_cost': 0,
                               "due_time":0}

class OutputConverter:
    def __init__(self, data_lookup) -> None:
        self.data_lookup= data_lookup
        
    def create_json_fts_info(self,  fts_crane_info, sid=0):
        #FTS_DATA = self.data_lookup['FTS_DATA']
        fts_setup_time = fts_crane_info['fts_setup_time']
        fts_index = fts_crane_info['fts_id']
        
        ORDER_DATA = self.data_lookup['ORDER_DATA']
        MIN_DATE_TIME = 0
        result_json = []
        temp = dict(temp_solution_schedule_json)
        temp['solution_id'] = sid
        temp['FTS_id'] = fts_crane_info['fts_db_id'] 
        temp['carrier_id'] = 0
        #temp['lat'] = FTS_DATA['LAT'][fts_index]
        #temp['lng'] = FTS_DATA['LNG'][fts_index]
        temp['operation_time'] = None
        temp['Setup_time'] = None
        temp['travel_Distance'] = None
        temp['travel_time'] = None
        temp['operation_rate'] = None
        temp['consumption_rate'] = None
        
   
        MIN_DATE_TIME = 0
        #print(MIN_DATE_TIME)
        exit_time = MIN_DATE_TIME + fts_crane_info["start_times"][0] 
        temp['arrivaltime'] = exit_time
        temp['exittime'] = exit_time
        #result_json.append(temp)
        ID_LIST = list( np.arange(len(ORDER_DATA), dtype=np.int32))
        for inx in range(len(fts_crane_info["ids"])):
            cid = fts_crane_info["ids"][inx]
            cr_id = ORDER_DATA[cid].ship_id
            #idx_cr = ID_LIST.index(cr_id)
            fts_setup_time = fts_crane_info['fts_setup_time']
            
            
            temp = dict(temp_solution_schedule_json)
            temp['solution_id'] = sid
            temp['FTS_id'] = fts_crane_info['fts_db_id'] 
            #print("cr_id", cr_id)
            temp['carrier_id'] = int(cr_id)
            #temp['lat'] = ORDER_DATA['LAT'][idx_cr]
            #temp['lng'] = ORDER_DATA['LNG'][idx_cr]
            temp['operation_time'] = fts_crane_info["process_times"][inx]
            temp['Setup_time'] = fts_crane_info["fts_setup_time"]
            temp['travel_Distance'] = fts_crane_info["distances"][inx]
            temp['travel_time'] = fts_crane_info["travel_times"][inx]
            temp['operation_rate'] = fts_crane_info["operation_rates"][inx]
            temp['consumption_rate'] = fts_crane_info["consumption_rates"][inx]
            temp['due_time'] = fts_crane_info["due_times"][inx]
            
          
            start_hours_to_add = fts_crane_info["start_times"][inx]
            end_hours_to_add = fts_crane_info["end_times"][inx]
            
            enter_time = MIN_DATE_TIME + start_hours_to_add
            exit_time = MIN_DATE_TIME + end_hours_to_add
            temp['arrivaltime'] =enter_time
            temp['exittime'] = exit_time
            
            temp['penalty_time'] = temp['due_time'] - temp['exittime']
            temp['labor_cost'] = temp['operation_rate'] 
            
            result_json.append(temp)
        
        return result_json

    def create_solution_schedule(self, sid, fts_crane_infos):
        result_json = []
        for fc_info  in fts_crane_infos:
            if fc_info['fts_id']==1:
                print(fc_info['fts_name'])
                print("##############################")
            fts_jsons = self.create_json_fts_info(fc_info, sid)
            if fc_info['fts_id']==1:
                print("##############################")
            #print(fc_info)
            result_json.extend(fts_jsons)
        #print(fc_info)
        return result_json
    



if __name__ == "__main__":
    PROBLEM_INDEX = 0
    LOAD_SHIP_PROBLEMS = [(132950.00 ,76985.41, 34430.12, 70,250.00, 19572.10, 65500.00, 39802.94, 
                           9100.00 ,70850.00 ,22698.00 ,10200.00, 20000.00, 10000.00, 63738.44 ,
                           63350.00 , 71573.15 , 27000.00 , 37725.37 , 37700.00 )]
    MAX_FTS_PROBLEMS = [(4, 4, 2, 4, 4, 4, 4, 2, 4, 4, 4, 2, 2, 4, 4, 4, 4, 2, 4)]
    
    NAMES = ["M.V.MARVELLOUS", "M.V.CL PEKING", "M.V.MCQUEEN", "M.V.IKAN BELIAK", 
             "M.V.EPIC HARMONY", "M.V.INDIAN SOLIDARITY", "M.V.GLORY ONE", "M.V.GERM SOPHIA", 
             "M.V.SAKIZAYA QUEEN", "M.V.ASIA SPRING", "M.V.CHARM LOONG", "M.V.ROYAL AWARD", 
             "M.V.VOSCO UNITY", "M.V.GOLDEN JAKE", "M.V.STAR TOPAZ", "M.V.ENERGY GLORY", 
             "M.V.PELAGIA", "M.V.CRYSTAL", "M.V.CIHAN"]
    
    order_datas = []
    for i in range(len(NAMES)):
        order_datas.append( Order(i+1, NAMES[i], MAX_FTS_PROBLEMS[PROBLEM_INDEX][i], 
                                  LOAD_SHIP_PROBLEMS[PROBLEM_INDEX][i]) )
    
    avg_consumptions = np.array([[0.3702,0.408,0.728,0.408,0.7048,0.408,0.728,0.728,0.408,0.728,0.728,0.728,0.728,0.7048,0.7048,0.408,0.7048,0.728,0.408],
                                [0.363,0.418,0.9624,0.418,0.5468,0.418,0.9624,0.9624,0.418,0.9624,0.9624,0.9624,0.9624,0.5468,0.5468,0.418,0.5468,0.9624,0.418],
                                [0.3702,0.4198,0.764,0.4198,0.3918,0.4198,0.764,0.764,0.4198,0.764,0.764,0.764,0.764,0.3918,0.3918,0.4198,0.3918,0.764,0.4198],
                                [0.3942,0.369,0.712,0.369,0.537,0.369,0.712,0.712,0.369,0.712,0.712,0.712,0.712,0.537,0.537,0.369,0.537,0.712,0.369],
                                [0.3924,0.4092,0.6678,0.4092,0.3876,0.4092,0.6678,0.6678,0.4092,0.6678,0.6678,0.6678,0.6678,0.3876,0.3876,0.4092,0.3876,0.6678,0.4092],
                                [0.3924,0.332,0.738,0.332,0.5882,0.332,0.738,0.738,0.332,0.738,0.738,0.738,0.738,0.5882,0.5882,0.332,0.5882,0.738,0.332],
                                [0.4794,0.3838,0.6794,0.3838,0.645,0.3838,0.6794,0.6794,0.3838,0.6794,0.6794,0.6794,0.6794,0.645,0.645,0.3838,0.645,0.6794,0.3838]])

    avg_operations = np.array([
        [0.002544335,0.003407155,0.004451765,0.003407155,0.003361006,0.003407155,0.004451765,0.004451765,0.003407155,0.004451765,0.004451765,0.004451765,0.004451765,0.003361006,0.003361006,0.003407155,0.003361006,0.004451765,0.003407155],
        [0.002711129,0.00399968,0.00462214,0.00399968,0.003945084,0.00399968,0.00462214,0.00462214,0.00399968,0.00462214,0.00462214,0.00462214,0.00462214,0.003945084,0.003945084,0.00399968,0.003945084,0.00462214,0.00399968],
        [0.003653235,0.003296414,0.003802137,0.003296414,0.003944151,0.003296414,0.003802137,0.003802137,0.003296414,0.003802137,0.003802137,0.003802137,0.003802137,0.003944151,0.003944151,0.003296414,0.003944151,0.003802137,0.003296414],
        [0.003676876,0.003596734,0.005022097,0.003596734,0.004431053,0.003596734,0.005022097,0.005022097,0.003596734,0.005022097,0.005022097,0.005022097,0.005022097,0.004431053,0.004431053,0.003596734,0.004431053,0.005022097,0.003596734],
        [0.003689765,0.004004164,0.004669624,0.004004164,0.004097017,0.004004164,0.004669624,0.004669624,0.004004164,0.004669624,0.004669624,0.004669624,0.004669624,0.004097017,0.004097017,0.004004164,0.004097017,0.004669624,0.004004164],
        [0.003513827,0.00396118,0.004935103,0.00396118,0.004176412,0.00396118,0.004935103,0.004935103,0.00396118,0.004935103,0.004935103,0.004935103,0.004935103,0.004176412,0.004176412,0.00396118,0.004176412,0.004935103,0.00396118],
        [0.003143764,0.002632618,0.003694672,0.002632618,0.003374388,0.002632618,0.003694672,0.003694672,0.002632618,0.003694672,0.003694672,0.003694672,0.003694672,0.003374388,0.003374388,0.002632618,0.003374388,0.003694672,0.002632618]

    ])

    travel_times = np.array(
        [[ 0.0,0.4489,0.3783,1.0148,0.9917,0.9579,0.2554,1.5401,1.9346,1.7256,1.2834,0.9803,1.2945,0.4669,0.3846,2.5144,7.1394,5.7928,5.2478],
        [ 0.4489,0.0,0.4274,0.6805,0.8331,0.9341,0.5438,1.1236,1.6718,1.5038,1.2328,0.9229,0.9551,0.7951,0.4685,2.0969,7.2444,5.7178,5.1995],
        [ 0.3783,0.4274,0.0,0.7081,0.6157,0.5927,0.6232,1.2895,1.5682,1.3518,0.9165,0.6077,0.9755,0.8451,0.6898,2.4842,6.8551,5.4315,4.8937],
        [ 1.0148,0.6805,0.7081,0.0,0.4181,0.69,1.1945,0.6072,0.9995,0.861,0.8415,0.6307,0.281,1.4465,1.1484,2.0537,6.8463,5.1351,4.6434],
        [ 0.9917,0.8331,0.6157,0.4181,0.0,0.2867,1.226,0.974,0.9624,0.7368,0.4413,0.2198,0.5389,1.4582,1.2501,2.4718,6.4796,4.8847,4.3677],
        [ 0.9579,0.9341,0.5927,0.69,0.2867,0.0,1.2106,1.2606,1.1379,0.8843,0.3254,0.0715,0.8243,1.4157,1.2807,2.736,6.3136,4.839,4.3014],
        [ 0.2554,0.5438,0.6232,1.1945,1.226,1.2106,0.0,1.6672,2.1507,1.9528,1.5359,1.2302,1.4751,0.2531,0.2049,2.4726,7.3812,6.0474,5.5031],
        [ 1.5401,1.1236,1.2895,0.6072,0.974,1.2606,1.6672,0.0,0.9778,1.0018,1.3212,1.1934,0.4495,1.9172,1.5639,1.6126,7.1247,5.1878,4.7471],
        [ 1.9346,1.6718,1.5682,0.9995,0.9624,1.1379,2.1507,0.9778,0.0,0.265,0.9403,1.0755,0.7576,2.3947,2.1339,2.5386,6.1785,4.2206,3.7704],
        [ 1.7256,1.5038,1.3518,0.861,0.7368,0.8843,1.9528,1.0018,0.265,0.0,0.6753,0.8251,0.6713,2.1906,1.9546,2.6078,6.1235,4.2829,3.8055],
        [ 1.2834,1.2328,0.9165,0.8415,0.4413,0.3254,1.5359,1.3212,0.9403,0.6753,0.0,0.3135,0.8727,1.7402,1.6018,2.8824,6.0409,4.5151,3.9807],
        [ 0.9803,0.9229,0.6077,0.6307,0.2198,0.0715,1.2302,1.1934,1.0755,0.8251,0.3135,0.0,0.7549,1.4426,1.2894,2.6813,6.3342,4.8265,4.294],
        [ 1.2945,0.9551,0.9755,0.281,0.5389,0.8243,1.4751,0.4495,0.7576,0.6713,0.8727,0.7549,0.0,1.7273,1.4235,2.0297,6.7604,4.9502,4.4767],
        [ 0.4669,0.7951,0.8451,1.4465,1.4582,1.4157,0.2531,1.9172,2.3947,2.1906,1.7402,1.4426,1.7273,0.0,0.3845,2.6429,7.4914,6.2369,5.6837],
        [ 0.3846,0.4685,0.6898,1.1484,1.2501,1.2807,0.2049,1.5639,2.1339,1.9546,1.6018,1.2894,1.4235,0.3845,0.0,2.2767,7.5181,6.1157,5.5819],
        [ 2.5144,2.0969,2.4842,2.0537,2.4718,2.736,2.4726,1.6126,2.5386,2.6078,2.8824,2.6813,2.0297,2.6429,2.2767,0.0,8.7169,6.6193,6.2354],
        [ 7.1394,7.2444,6.8551,6.8463,6.4796,6.3136,7.3812,7.1247,6.1785,6.1235,6.0409,6.3342,6.7604,7.4914,7.5181,8.7169,0.0,2.9555,2.878],
        [ 5.7928,5.7178,5.4315,5.1351,4.8847,4.839,6.0474,5.1878,4.2206,4.2829,4.5151,4.8265,4.9502,6.2369,6.1157,6.6193,2.9555,0.0,0.6258],
        [ 5.2478,5.1995,4.8937,4.6434,4.3677,4.3014,5.5031,4.7471,3.7704,3.8055,3.9807,4.294,4.4767,5.6837,5.5819,6.2354,2.878,0.6258,0.0],]
    )
    
    arrival_times = [0,33,54,73.5,120.5,313,415.5,467.5,482.5,655,
                     655,704.5,720.5,745.5,794.5,882.5,1220.5,1329,1506.5]
    due_times = [109.5,104.5,138.5,192.5,168.5,402.5,494.5,493.8333333,
                 575.5,714.5,714.5,733.6666667,746.5,818.5,868.5,954.5,
                 1260, 1410.5,1578.5]

    
    lookup_data = {
        'ORDER_DATA':order_datas,
        "OPERATION_RATE":np.round(  avg_operations, 6),
        "CONSUMPTION_RATE": avg_consumptions,
        "TRAVEL_TIME":travel_times,
        "MAX_FTS": max([o.maxFTS for o in order_datas]),
        "NFTS":avg_operations.shape[0],
        "NSHIP":len(order_datas),
        "ArrivalTime":np.array(arrival_times),
        "DueTime":np.array(due_times)    }

    
    for order in lookup_data['ORDER_DATA']:
        print(order)
    
    print(lookup_data["OPERATION_RATE"])
    print(lookup_data["TRAVEL_TIME"])
    print(lookup_data["MAX_FTS"])
    print(lookup_data["NFTS"])
    print(lookup_data["NSHIP"])
    decoder = DecoderExp(lookup_data)
    decoder.D = decoder.NFTS*decoder.NSHIP + decoder.NSHIP
    
    problem = FTSProblem(decoder)
    
    algorithm = DE(
        pop_size=50,
        sampling=LHS(),
        variant="DE/rand/1/bin",
        CR=0.8,
        dither="vector",
        jitter=False
    )

    
#callback = MyCallback()
    m = 0
    ss = 15
    termination = get_termination("time", f"00:{m:02d}:{ss:02d}")
    termination = get_termination("n_eval", 10)
    res = minimize(problem, algorithm, termination, seed=1, verbose=True)
    print("Best solution found: \nX = %s\nF = %s" % (res.X, res.F))
    fts_info, ship_info = decoder.decode(res.X)
    
    #np.random.seed(0)
    #fts_info, ship_info = decoder.decode(np.random.rand(decoder.D))
    print("------------------ FTS ----------------------")
    conveter = OutputConverter(lookup_data)
    fts_infos = conveter.create_solution_schedule(0, fts_info)
    
    for fts in fts_info:
        continue
        print(fts)
    
    for fts in fts_infos:
    
        #print(fts)
        fts['demand'] = fts["operation_time"]/fts["operation_rate"]
        #if  len(fts['ids']) > 0:
            #print(fts['ids'], fts['travel_times'], fts['distances'])
    df = pd.DataFrame(fts_infos)
    print(df)
    print()
    print("------------------ SHIP ----------------------")
    for ship in ship_info: 
        continue
        print(ship)
        
    df.to_csv(f"./exp/P{PROBLEM_INDEX+1}.csv")
        
    