from asyncio import sleep
#from website import create_app
from flask import render_template, Response
from flask_socketio import SocketIO
import numpy as np
import openpyxl
import pandas as pd
import matplotlib.pyplot as plt
import math
import requests as req
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from flask import Flask, request
#from utility import get_dataset, create_json
#from decoder import Decoder
#from problem import *
#from AMIS import *
from flask_cors import CORS, cross_origin
import json
from utility.db_api import *

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

@app.route("/FTScrane", methods = ["POST", "GET"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def all_crane_FTS():
    return get_all_crane_FTS()

@app.route("/FTS", methods = ["POST", "GET"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def all_FTS():
    return get_all_FTS()

@app.route("/cargo", methods = ["POST", "GET"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def all_cargo():
    return get_all_cargo()


@app.route("/floating", methods = ["POST", "GET"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def all_floatingCrane():
    return get_all_floatingCrane()

@app.route("/carrier", methods = ["POST", "GET"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def all_carrier():
    return get_all_carrier()

@app.route("/cargo_crane", methods = ["POST", "GET"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def all_cargo_crane():
    return get_all_cargo_crane()

@app.route("/order", methods = ["POST", "GET"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def all_order():
    return get_all_order()


if __name__ == "__main__":
    socketio.run(app=app, debug=True, host="0.0.0.0", port = 5011)
    