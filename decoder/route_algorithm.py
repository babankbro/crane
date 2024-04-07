from pymoo.core.callback import Callback
from pymoo.optimize import minimize
from pymoo.algorithms.soo.nonconvex.brkga import BRKGA
from sklearn.metrics import accuracy_score
from pymoo.algorithms.soo.nonconvex.de import DE
import numpy as np
from pymoo.core.problem import ElementwiseProblem
import math
import sys
from pymoo.algorithms.soo.nonconvex.de import DE
from pymoo.problems import get_problem
from pymoo.operators.sampling.lhs import LHS
from pymoo.optimize import minimize
from pymoo.termination import get_termination
import json
import pandas as pd


sys.path.insert(0, "./utility")

from insert_db_api import DBInsert
from crane_utility import *
from decoder_v3 import *
from decoder_v2 import *
from insert_db_api import *
from output_converter import *



class CraneProblem(ElementwiseProblem):

    def __init__(self, decoder):
        self.decoder = decoder
        self.N = decoder.D
        super().__init__(n_var=self.N, n_obj=1, n_constr=0, xl=0, xu=1)

    def get_total_distance(self, crane_infos):
        td = 0
        for ci in crane_infos:
            td += np.sum(ci["distances"])
        return td

    def get_total_delta_due_times(self, ship_infos):
        tt = 0
        for si in ship_infos:
            #print(si)
            #tt += si["due_time"] - np.max(si["crane_exit_times"])
            tt += np.max(si["fts_crane_operation_times"])
        return tt

    def get_balance_work_loads(self, crane_infos):
        loads = []
        for ci in crane_infos:
            tload = np.sum(ci["demands"])
            loads.append(tload)
        loads = np.array(loads)
        return np.sum(np.abs(loads - np.mean(loads)))

    def cost(self, crane_infos):
        tcost = 0
        for ci in crane_infos:
            travel = np.sum(np.array(ci["travel_times"])*0.1)
            travel = 0
            #print(ci["process_times"])
            process  =  np.sum(np.array(ci["demands"])*np.array(ci["consumption_rates"]))
            #print(process)
            tcost += process + travel
        return tcost
    
    def single_fts_cost(self, fts_info):
        tcost = 0
        for si in range(len(fts_info['ids'])):
                crane_ship_info = fts_info['crane_infos'][si]
                crane_bulks = crane_ship_info['crane_infos']
                for cindx, cbulk in enumerate(crane_bulks):
                    consumption_rate = cbulk["consumption_rate"]
                    operation_rate = cbulk["operation_rate"]
                    for ibluck, bulk in enumerate(cbulk['bulks']):
                        load = cbulk["loads"][ibluck]
                        tcost += load*consumption_rate
        return tcost

    def cost_v2(self, crane_infos):
        tcost = 0
        for fts_info in crane_infos:
            tcost += self.single_fts_cost(fts_info)
        return tcost   
    
    def create_json_crane_info(self, sid, fts_info):
        #print("---------------------------------")
        #print(fts_info['fts'].name)
        ORDER_DATA = self.data_lookup['ORDER_DATA']
        CRANE_RATE = self.data_lookup['CRANE_RATE']
        format_string = "%Y-%m-%d %H:%M:%S" 
        MIN_DATE_TIME = ORDER_DATA['MIN_DATE_TIME']
        MIN_DATE_TIME = datetime.strptime(MIN_DATE_TIME, format_string)
    
        #print(fts_info)
        #print('demands', fts_info['demands'])
        #print('consumption_rates', fts_info['consumption_rates'])
        #print('operation_rates', fts_info['operation_rates'])
        #print('crane_setup_times', fts_info['crane_setup_times'])
        #print(type(fts_info['crane_infos']))
        #print(fts_info['crane_infos'])
        result_json = []
        for si in range(len(fts_info['ids'])):
            crane_ship_info = fts_info['crane_infos'][si]
            start_ship_time = fts_info['start_times'][si]
            fts_setup_time = fts_info['fts_setup_time']
            
            crane_bulks = crane_ship_info['crane_infos']
            order_id = fts_info['order_ids'][si]
           
            
            for cindx, cbulk in enumerate(crane_bulks):
                #print("cbulk ==========", cbulk)
                operation_rate = cbulk["operation_rate"]
                consumption_rate = cbulk["consumption_rate"]
                crane_index = cbulk['crane_index']
                ship = cbulk['ship']
                #order_id = cbulk['order_id']
                #print(cbulk["operation_times"])
                for ibluck, bulk in enumerate(cbulk['bulks']):
                    temp = dict(temp_solution_crane_schedule_json)
                    
                    
                    """
                    solution_id	
                    order_id 
                    carrier_id	
                    start_time	due_time	operation_time	Setup_time	
                    travel_Distance	
                    travel_time	operation_rate
                    consumption_rate
                    crane_id	
                    bulk	
                    load_cargo
                    cargo_id
                    """
                    #print(cbulk)
                    start_hours_to_add = timedelta(hours=start_ship_time + fts_setup_time+\
                                                   cbulk["offset_start_times"][ibluck])
                    end_hours_to_add = timedelta(hours=start_ship_time + fts_setup_time+\
                                                 cbulk["finish_times"][ibluck])
                
                    #if len(fts_crane_info["start_times"]) > 0:
                        #hours_to_add = timedelta(hours=fts_crane_info["start_times"][0])
                    enter_time = MIN_DATE_TIME + start_hours_to_add
                    exit_time = MIN_DATE_TIME + end_hours_to_add
                    temp['solution_id'] = sid
                    temp['order_id']  = order_id
                    temp['carrier_id'] = cbulk['ship'].id
                    temp['start_time'] =enter_time.strftime('%Y-%m-%d %H:%M:%S')
                    temp['due_time'] = exit_time.strftime('%Y-%m-%d %H:%M:%S')
                    temp['operation_time'] = cbulk["operation_times"][ibluck]
                    temp['Setup_time'] = 0
                    temp['travel_time'] = 0
                    temp['travel_Distance'] = 0
                    temp['operation_rate'] = operation_rate
                    temp['consumption_rate'] = consumption_rate
                    temp['crane_id'] = fts_info['fts'].crane_ids[crane_index]
                    temp['bulk'] = cbulk["bulks"][ibluck] + 1
                    temp['load_cargo'] = cbulk["loads"][ibluck]
                    temp['cargo_id'] = ship.cargo_id
                    #print(temp)
                    result_json.append(temp)
                    #temp['start_time'] = 
                    #temp['lng'] = FTS_DATA['LNG'][fts_index]
                    #temp['operation_time'] = None
                    #temp['Setup_time'] = None
                    #temp['travel_Distance'] = None
                    #temp['travel_time'] = None
                    #temp['operation_rate'] = None
                    #temp['consumption_rate'] = None
                    #print(temp)
                    #break
                
            #continue
            #print(crane_info)
               
        return result_json
    
    
    def ship_cost(self, ship_infos):
        tcost = 0
        ttime = 0
        for si in ship_infos:
            if si['delta_time'] < 0:
                tcost += (si['delta_time'])*si['penalty_rate']
            else:
                tcost += -(si['delta_time'])*si['reward_rate']
            ttime += si['delta_time']
                
        return tcost, ttime

    def _evaluate(self, x, out, *args, **kwargs):
        crane_infos, ship_infos = self.decoder.decode(x)
        if crane_infos == None:
            td = 100000
            total_delta_due_time = -100000
            sum_delta_load = 100000000
            tcost = 1000000000000
        else:
            td = self.get_total_distance(crane_infos)
            total_delta_due_time= self.get_total_delta_due_times(ship_infos)
            sum_delta_load = self.get_balance_work_loads(crane_infos)
            tcost = self.cost_v2(crane_infos)*35
            #tcost += self.ship_cost(ship_infos)*10000

        #print(tcost)
        out["hash"] = hash(str(x)) + tcost
        out["F"] = total_delta_due_time/1000 +  tcost/2000000
        out["pheno"] = { 'distance':td, 'time':0}


if __name__ == "__main__":
    [6, 7, 10, 11, 19, 20, 21, 23, 24, 31, 32, 1, 2, 3, 4,  12, 13, 14, 15, 16, 17, 18, 5]
    for group in [ 8]:
        print(f"########################## {group}")
        #data_lookup = load_data_lookup('./dataset/data2.json')
        global mydb, mycursor
        mydb, mycursor = try_connect_db()
        #group = 31
        data_lookup = create_data_lookup(isAll=True, group=group)
        decoder = DecoderV3(data_lookup)
        converter = OutputConverter(data_lookup)
        db_insert = DBInsert(mycursor, mydb)
        db_insert.clear_solution(1)
        
        algorithm = BRKGA(
            n_elites=20,
            n_offsprings=40,
            n_mutants=10,
            bias=0.8,
            #eliminate_duplicates=MyElementwiseDuplicateElimination()
            )
        
        algorithm = DE(
            pop_size=5,
            sampling=LHS(),
            variant="DE/rand/1/bin",
            CR=0.3,
            dither="vector",
            jitter=False
            )

        problem = CraneProblem(decoder)
        termination = get_termination("time", "00:0:29")
        print(f"########################## {group}")
        resGA = minimize(problem,algorithm,termination,seed=1,verbose=True)

        print("Best solution found: \nX = %s\nF = %s" % (resGA.X, resGA.F))
        print("Solution", resGA.opt.get("pheno")[0])
        print()
        xs = resGA.X
        
        #xs = np.random.random(decoder.D)
        fts_crane_infos, ship_infos =  decoder.decode(xs, True)

        #for ci in fts_crane_infos:
            #print(ci)

        #print()
        #for si in ship_infos:
            #print(si)

        loads = []
        for ci in fts_crane_infos:
            tload = np.sum(ci["demands"])
            loads.append(tload)
        loads = np.array(loads)
        np.sum(np.abs(loads - np.mean(loads))), loads
        
        
        save_file = open("./dataset/solution1.json", "w")  
        
        json.dump( {'fts_infos':fts_crane_infos,
                    'ship_infos':ship_infos} , save_file, indent = 4,  cls=NpEncoder) 
        
        for fts_crane_info in fts_crane_infos:
            #if fts_crane_info['fts_name'] == "แก่นตะวัน":
            #print(fts_crane_info)
            if len(fts_crane_info['process_times']) > 0 :
                if (fts_crane_info['process_times'][0]) < 1:
                    print(fts_crane_info['process_times'])
        
        db_insert = DBInsert(mycursor, mydb)
        db_insert.clear_solution(group)
        
        result_json = converter.create_solution_schedule(group, fts_crane_infos) 
        db_insert.insert_jsons(result_json)
        result_json = converter.create_crane_solution_schedule(group, fts_crane_infos) 
        df_crane_solution_schedule = pd.DataFrame(result_json)
        #print(result_json)
        print("Load Cargo",sum(df_crane_solution_schedule['load_cargo']))
        db_insert.insert_crane_solution_schedule_jsons(result_json)
        result_json = converter.create_crane_solution(group, fts_crane_infos, ship_infos) 
        df_crane_solution = pd.DataFrame(result_json)
        db_insert.insert_crane_solution_jsons(result_json)
        

        
        result_json = converter.create_ship_solution_schedule(group, ship_infos, df_crane_solution_schedule, data_lookup) 
        db_insert.insert_carrier_solution_jsons(result_json)
        column_names = df_crane_solution_schedule.columns

    

        for rj in result_json:
            print(rj)
            #df = df_crane_solution_schedule[ df_crane_solution_schedule['order_id']  == rj['order_id']]
            #left_join_df = pd.merge(df, cargo_df, on='cargo_id', how='left')
            #left_join_df['consumption_liter'] = left_join_df["load_cargo"] * left_join_df['premium_rate']
            #print(left_join_df)
            break
            print("LEN", len(df_crane_solution_schedule[ df_crane_solution_schedule['order_id']  == rj['order_id']] ))
        
        print("----------------------------   SHIPS --------------------------------------------")
        for ship_info in ship_infos:
            continue
            print(ship_info)
        
        
        result = {}
        problem._evaluate(xs,result)
        #print(result)
        #fts_infos = converter.create_solution_schedule(1, fts_crane_infos)
        for crane_info in fts_crane_infos:
            continue
            #print(crane_info)
            date_str = '2023-02-28 14:30:00'
            date_format = '%Y-%m-%d %H:%M:%S'
            crane_info['delta'] = (datetime.strptime(crane_info['exittime'], date_format) - 
                                datetime.strptime(crane_info['arrivaltime'], date_format))
        print()
        
        df = pd.DataFrame(fts_crane_infos)
        #print(df)
        np.save("./dataset/xs_v2.npy", xs)
    
    
  