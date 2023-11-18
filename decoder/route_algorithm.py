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
        #for si in ship_infos:
            #tt += si["due_time"] - np.max(si["crane_exit_times"])
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
    
    def ship_cost(self, ship_infos):
        tcost = 0
        for si in ship_infos:
            if si['delta_time'] < 0:
                tcost += -(si['delta_time'])*si['penalty_rate']
            else:
                tcost += -(si['delta_time'])*si['reward_rate']
                
        return tcost

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
            tcost = self.cost(crane_infos)
            tcost += self.ship_cost(ship_infos)

        #print(tcost)
        out["hash"] = hash(str(x)) + tcost
        out["F"] = tcost
        out["pheno"] = { 'distance':td, 'time':0}


if __name__ == "__main__":
    
    #data_lookup = load_data_lookup('./dataset/data2.json')
    data_lookup = create_data_lookup()
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
        pop_size=20,
        sampling=LHS(),
        variant="DE/rand/1/bin",
        CR=0.3,
        dither="vector",
        jitter=False
        )


    problem = CraneProblem(decoder)
    termination = get_termination("time", "00:00:10")
    
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
    
    result_json = converter.create_solution_schedule(1, fts_crane_infos) 
    db_insert.insert_jsons(result_json)
    result_json = converter.create_crane_solution_schedule(1, fts_crane_infos) 
    db_insert.insert_crane_solution_schedule_jsons(result_json)
    result_json = converter.create_crane_solution(1, fts_crane_infos, ship_infos) 
    db_insert.insert_crane_solution_jsons(result_json)
    result_json = converter.create_ship_solution_schedule(1, ship_infos) 
    db_insert.insert_carrier_solution_jsons(result_json)
    
    print("----------------------------   SHIPS --------------------------------------------")
    for ship_info in ship_infos:
        #continue
        print(ship_info)
    
    
    result = {}
    problem._evaluate(xs,result)
    print(result)
    fts_infos = converter.create_solution_schedule(1, fts_crane_infos)
    for crane_info in fts_infos:
        #continue
        print(crane_info)
        date_str = '2023-02-28 14:30:00'
        date_format = '%Y-%m-%d %H:%M:%S'
        crane_info['delta'] = (datetime.strptime(crane_info['exittime'], date_format) - 
                               datetime.strptime(crane_info['arrivaltime'], date_format))
    print()
    
    df = pd.DataFrame(fts_infos)
    print(df)
    np.save("./dataset/xs_v1.npy", xs)
    
    
  