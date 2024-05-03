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
                               "operation_rate": 700, "consumption_rate":0 }

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
          
            start_hours_to_add = fts_crane_info["start_times"][inx]
            end_hours_to_add = fts_crane_info["end_times"][inx]
            
            enter_time = MIN_DATE_TIME + start_hours_to_add
            exit_time = MIN_DATE_TIME + end_hours_to_add
            temp['arrivaltime'] =enter_time
            temp['exittime'] = exit_time
            
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
    PROBLEM_INDEX = 5
    LOAD_SHIP_PROBLEMS = [(132950.00	,76985.41	,4430.12	,70250.00	,19572.10	),
                          (146245.0, 69286.9, 30987.1, 77275.0, 17614.9),
                          (190118.5, 48500.8, 21691.0, 100457.5, 22899.4),
                          (95059.25	,24250.40	,10845.49	,50228.75	,34349.04),
                          (161600.73	,7275.12	,18437.33	,15068.63	,58393.36),
                          (65500.00	, 39802.94	, 9100.00	,  70850.00	),
                          (22698.00, 10200.00, 20000.00, 10000.00, 63738.44),
                          (63350.00	,71573.15	,27000.00	,37725.37	,37700.00)]
    MAX_FTS_PROBLEMS = [(4,4,2,4,4), (2,2,2,4,2), (4,2,2,2,2), (2,4,2,2,2), (2,2,4,2,2),
                        (4, 4, 2, 4), (4,4,2,2,4), (4,4,4,2,4)]
    
    order_datas = [
    Order(1, "M.V.MARVELLOUS", MAX_FTS_PROBLEMS[PROBLEM_INDEX][0], LOAD_SHIP_PROBLEMS[PROBLEM_INDEX][0]),
    Order(2, "M.V.CL PEKING", MAX_FTS_PROBLEMS[PROBLEM_INDEX][1], LOAD_SHIP_PROBLEMS[PROBLEM_INDEX][1]),
    Order(3, "M.V.MCQUEEN", MAX_FTS_PROBLEMS[PROBLEM_INDEX][2], LOAD_SHIP_PROBLEMS[PROBLEM_INDEX][2]),
    Order(4, "M.V.IKAN BELIAK", MAX_FTS_PROBLEMS[PROBLEM_INDEX][3], LOAD_SHIP_PROBLEMS[PROBLEM_INDEX][3]),
    #Order(5, "M.V.EPIC HARMONY", MAX_FTS_PROBLEMS[PROBLEM_INDEX][4], LOAD_SHIP_PROBLEMS[PROBLEM_INDEX][4]),
    ]
    
    avg_operations = np.array([[0.22	,	0.22	,	0.22	,	0.22	,	0.22],
                [0.244	,	0.244	,	0.244	,	0.244	,	0.244],
                [0.194	,	0.194	,	0.194	,	0.194	,	0.194],
                [0.259	,	0.259	,	0.259	,	0.259	,	0.259],
                [0.248	,	0.248	,	0.248	,	0.248	,	0.248],
                [0.245	,	0.245	,	0.245	,	0.245	,	0.245],
                [0.192	,	0.192	,	0.192	,	0.192	,	0.192]])
    
    avg_operations2 = np.array([[0.22	,	0.22	,	0.22	,	0.22	,	0.22],
                [0.24	,	0.24	,	0.24	,	0.24	,	0.24],
                [0.19	,	0.19	,	0.19	,	0.19	,	0.19],
                [0.26	,	0.26	,	0.26	,	0.26	,	0.26],
                [0.25	,	0.25	,	0.25	,	0.25	,	0.25],
                [0.25	,	0.25	,	0.25	,	0.25	,	0.25],
                [0.19	,	0.19	,	0.19	,	0.19	,	0.19]])
    
    travel_times = np.array(
        [[0	,	0.49	,	0.41	,	1.1	,	1.08],
        [0.49	,	0	,	0.47	,	0.74	,	0.92],
        [0.41	,	0.47	,	0	,	0.77	,	0.67],
        [1.1	,	0.74	,	0.77	,	0	,	0.46],
        [1.08	,	0.92	,	0.67	,	0.46	,	0]]
    )

    travel_times = np.array(
        [[0	,	1.33	,	1.38	,	1.23	],
        [1.33	,	0	,	1.8	,	2.34	],
        [1.38	,	1.8		,	0	,	1.09	],
        [1.23	,	2.34	,	1.09	,	0	],
        ]
    )
    
    travel_times2 = np.array(
        [[0	,	0.73	,	0.89	,	0.74	,	2.39],
        [0.73	,	0	,	0.35	,	0.96	,	1.91],
        [0.89	,	0.35	,	0	,	0.83	,	1.58],
        [1.1	,	0.74	,	0.83	,	0	,	1.87],
        [2.39	,	1.91	,	0.58	,	1.87	,	0]]
    )

    travel_times2 = np.array(
        [[0	,	2.49	,	8.35	,	6.74	,	6.16],
        [2.49	,	0	,	9.69	,	7.35	,	6.93],
        [8.35	,	9.69	,	0	,	3.26	,	3.19],
        [6.74	,	7.35	,	3.26	,	0	,	0.68],
        [6.16	,	6.93	,	3.19	,	0.68	,	0]]
    )
    
    
    lookup_data = {
        'ORDER_DATA':order_datas,
        "OPERATION_RATE":np.round(  avg_operations, 4),
        "TRAVEL_TIME":travel_times,
        "MAX_FTS": max([o.maxFTS for o in order_datas]),
        "NFTS":avg_operations.shape[0],
        "NSHIP":len(order_datas),
        
    }

    
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
    ss = 59
    termination = get_termination("time", f"00:{m:02d}:{ss:02d}")
    termination = get_termination("n_eval", 10000)
    res = minimize(problem, algorithm, termination, seed=1, verbose=True)
    print("Best solution found: \nX = %s\nF = %s" % (res.X, res.F))
    fts_info, ship_info = decoder.decode(res.X)
    
    #np.random.seed(0)
    #fts_info, ship_info = decoder.decode(np.random.rand(decoder.D))
    print("------------------ FTS ----------------------")
    conveter = OutputConverter(lookup_data)
    fts_infos = conveter.create_solution_schedule(0, fts_info)
    
    for fts in fts_info:
        print(fts)
    
    for fts in fts_infos:
        print(fts)
        fts['demand'] = fts["operation_time"]/fts["operation_rate"]
        #if  len(fts['ids']) > 0:
            #print(fts['ids'], fts['travel_times'], fts['distances'])
    df = pd.DataFrame(fts_infos)
    print(df)
    print()
    print("------------------ SHIP ----------------------")
    for ship in ship_info:
        print(ship)
        
    df.to_csv(f"./exp/P{PROBLEM_INDEX+1}.csv")
        
    