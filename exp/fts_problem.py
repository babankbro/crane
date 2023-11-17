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


class FTSProblem(ElementwiseProblem):

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
        max_time = 100000000000000000000000000000
        if crane_infos == None:
            td = 100000
            total_delta_due_time = -100000
            sum_delta_load = 100000000
            tcost = 1000000000000
        else:
            max_time = 0
            for ship_info in ship_infos:
                max_time = max(max_time, max(ship_info["fts_exit_times"]))

        #print(tcost)
        out["hash"] = hash(str(x)) + max_time
        out["F"] = max_time
        out["pheno"] = { 'max_time':max_time, 'time':0}