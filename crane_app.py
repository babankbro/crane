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
from db_api import *
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
    #compute_time = 0
    user_group = int(datas['Group'])
    FTS = [fts['fts_id'] for fts in datas['fts']] if len(datas['fts']) > 0 else None
    solution_id = user_group if "solution_id" not in datas else int(datas['solution_id'])
    
    print(user_group,  solution_id)
    global mydb, mycursor
    mydb, mycursor = try_connect_db()
    data_lookup = create_data_lookup(isAll=True, group=user_group, 
                                     duration_date_time =[datas["started"], datas["ended"]],
                                     ftses = FTS)
    decoder = DecoderV2(data_lookup)
    converter = OutputConverter(data_lookup)
    
    
    
    compute_time = compute_time*60
    m = compute_time//60
    ss = compute_time % 60
    print("compute_time",compute_time, m, ss, solution_id)
    problem = CraneProblem(decoder)

    algorithm = BRKGA(
        n_elites=40,
        n_offsprings=80,
        n_mutants=40,
        bias=0.9,
    #eliminate_duplicates=MyElementwiseDuplicateElimination()
    )
    
    algorithm = DE(
        pop_size=10,
        sampling=LHS(),
        variant="DE/rand/1/bin",
        CR=0.5,
        dither="vector",
        jitter=False
    )


    #callback = MyCallback()
    termination = get_termination("time", f"00:{m:02d}:{ss:02d}")
    #termination = get_termination("time", f"00:00:10")
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

    #global mydb, mycursor
    mydb, mycursor = try_connect_db()
    db_insert = DBInsert(mycursor, mydb)
    db_insert.clear_solution(solution_id)
    
    result_json = converter.create_solution_schedule(solution_id, fts_crane_infos) 
    db_insert.insert_jsons(result_json)
    result_json = converter.create_crane_solution_schedule(solution_id, fts_crane_infos) 
    df_crane_solution = pd.DataFrame(result_json)
    #print(result_json)
    print(df_crane_solution)
    db_insert.insert_crane_solution_schedule_jsons(result_json)
    result_json = converter.create_crane_solution(solution_id, fts_crane_infos, ship_infos) 
    db_insert.insert_crane_solution_jsons(result_json)
    
    
    result_json = converter.create_ship_solution_schedule(solution_id, ship_infos, df_crane_solution, data_lookup) 
    db_insert.insert_carrier_solution_jsons(result_json)

    np.save("./dataset/bestX.npy", np.array(res.X))
    print("----------------------------   SHIPS --------------------------------------------")
    for ship_info in ship_infos:
        #continue
        print(ship_info['ship_id'], ship_info['maxFTS'], ship_info['demand'],  ship_info['open_time'], ship_info['due_time'], ship_info['fts_crane_ids'],
              ship_info['fts_crane_enter_times'], ship_info['fts_crane_exit_times'])
    
    
    for key in datas:
        
        print(key, datas[key])
    
    return {'status':"success",
            #"data_date":data_date, 
                "compute_time":compute_time,
              #  "start_date":current_time
                }
    
@app.route("/update", methods = ["POST", "GET"])
@cross_origin()
def update_plan():
    datas = request.get_json( )
    for key in datas:
        print(key, datas[key])
    
    old_solution_id = int(datas['old_solution_id'])
    #old_solution_id = 114
    old_solution_info = get_solution_info(old_solution_id)

    datas["started"] = old_solution_info['started_at'].strftime("%Y-%m-%d %H:%M:%S")
    datas["ended"] = old_solution_info['ended_at'].strftime("%Y-%m-%d %H:%M:%S")
    
    for key in datas:
        print(key, datas[key])


    #datas["ended"] = datas["ended"].split(" ")[0] + " 23:59:59"
    
    user_group = datas["user_group"]
    print("user_group", user_group, "START", datas["started"], datas["ended"])

    mydb, mycursor = try_connect_db()
    data_lookup = create_data_lookup(isAll=True, group=user_group,
                                     duration_date_time =[datas["started"], datas["ended"]])
    
    decoder = DecoderV2(data_lookup)
    converter = OutputConverter(data_lookup)

    solution_id = int(datas['solution_id'])
    #solution_id = 70
    primitive_ship_infos = datas['plan']

    create_order_start_date_hour(primitive_ship_infos,
                                 np.min(data_lookup["ORDER_DATA"]["MIN_TIME_HOUR"]))
    print(len(primitive_ship_infos), print(len(data_lookup["ORDER_DATA"])))
    print("user_group", user_group, "START", datas["started"], datas["ended"])
    
    fts_crane_infos, ship_infos =  decoder.manual_assign(primitive_ship_infos)

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
    print(f"Insert Solution:{solution_id}")
    
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


    return {'status':'sucess'}

if __name__ == "__main__":
    app.run( debug=True, host="0.0.0.0", port = 5012)
    #socketio.run(app=app, debug=True, host="0.0.0.0", port = 5011, ssl_context=("cert.pem", "key.pem"))
    #app.run( debug=True, host="0.0.0.0", port = 5012, ssl_context=("/etc/ssl/certs/certificate.pem", 
    #"/etc/ssl/private.key"))
    #app.run(ssl_context=("cert.pem", "key.pem"))
  
