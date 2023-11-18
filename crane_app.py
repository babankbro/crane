######################################################################### crane_app.py #####################
from asyncio import sleep
from flask_socketio import SocketIO
import numpy as np
import openpyxl
import requests as req
import matplotlib.pyplot as plt
from datetime import datetime
from flask import Flask, request, render_template, Response

from flask_cors import CORS, cross_origin
import time
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
import json
import pandas as pd

import sys
sys.path.insert(0, "./utility")
sys.path.insert(0, "./decoder")

from insert_db_api import DBInsert
from crane_utility import *
from decoder_v2 import *
from decoder_v3 import *
from insert_db_api import *
from output_converter import *
from route_algorithm import *
from AMIS import *


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


app = Flask(__name__, template_folder='./')
socketio = SocketIO(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/", methods = ["POST", "GET"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def hello_world():
    return "<p> Hello </p>"


#@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@app.route("/route", methods = ["POST", "GET"])
@cross_origin()
def route():
    datas = request.get_json( )
    #data_date = datas['date']
    compute_time = int(datas['computetime'])
    #current_time = datas['currenttime']
    
    data_lookup = create_data_lookup()
    decoder = DecoderV3(data_lookup)
    converter = OutputConverter(data_lookup)
    
    
    
    compute_time = compute_time*1
    m = compute_time//60
    ss = compute_time % 60
    print("compute_time",compute_time, m, ss)
    problem = CraneProblem(decoder)
    


    algorithm = BRKGA(
        n_elites=40,
        n_offsprings=80,
        n_mutants=40,
        bias=0.9,
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

    
#callback = MyCallback()
    termination = get_termination("time", f"00:{m:02d}:{ss:02d}")
    res = minimize(problem,
                algorithm,
                termination,
                    seed=1,
                    #callback=callback,
                    verbose=True)

    print("Best solution found: \nX = %s\nF = %s" % (res.X, res.F))
    

    fts_crane_infos, ship_infos =  decoder.decode(res.X, True)

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
        if fts_crane_info['fts_name'] == "แก่นตะวัน":
            print(fts_crane_info)

    db_insert = DBInsert(mycursor, mydb)
    db_insert.clear_solution(1)
    
    result_json = converter.create_solution_schedule(1, fts_crane_infos) 
    db_insert.insert_jsons(result_json)
    result_json = converter.create_crane_solution_schedule(1, fts_crane_infos) 
    db_insert.insert_crane_solution_schedule_jsons(result_json)
    result_json = converter.create_crane_solution(1, fts_crane_infos, ship_infos) 
    db_insert.insert_crane_solution_jsons(result_json)
    result_json = converter.create_ship_solution_schedule(1, ship_infos) 
    db_insert.insert_carrier_solution_jsons(result_json)

    np.save("./dataset/bestX.npy", np.array(res.X))
    
    return {'status':"success",
            #"data_date":data_date, 
                "compute_time":compute_time,
              #  "start_date":current_time
                }
    
if __name__ == "__main__":
    socketio.run(app=app, debug=True, host="0.0.0.0", port = 5011)
    