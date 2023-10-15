import mysql.connector
import time
import datetime
import pytz
import json
from json import JSONEncoder
import datetime
import os
import glob
import pandas as pd

from db_api import *
from crane_utility import *
from output_converter import *

class DBInsert:
    def __init__(self, mycursor, mydb) -> None:
        self.cursor = mycursor
        self.db = mydb
        self.solution_id = 1
        
    def clear_solution(self, sid):
        sql = f"DELETE FROM solution_schedule WHERE solution_id = {sid};"
        self.cursor.execute(sql)
        self.db.commit()
        
    def insert_jsons(self, json_data):
        colum_names = """solution_id,	 FTS_id,	 carrier_id,	 latlng	,
            arrivaltime,	exittime,	operation_time,	Setup_time,	travel_Distance,
            travel_time, operation_rate,	consumption_rate"""
        for d in json_data:
            print(d)
            d["arrivaltime"] = f"'{d['arrivaltime']}'"
            d["exittime"] = f"'{d['exittime']}'"
            values = [str(d[x]) for x in d]
            columns = [x for x in d]
            colum_names = ', '.join(columns)
           
            values = ', '.join(values)
            #print(colum_names)
            print(values)
            values = values.replace('None', 'NULL')
            insert_query = f"INSERT INTO solution_schedule({colum_names}) VALUES ({values})"
            print(insert_query)
            self.cursor.execute(insert_query)
            self.db.commit()
        


if __name__ == "__main__":
    data_lookup = load_data_lookup('./dataset/data2.json')
    converter = OutputConverter(data_lookup)
    db_insert = DBInsert(mycursor, mydb)
    db_insert.clear_solution(1)
    
    #df = pd.read_csv("./dataset/solution_schedule_head.csv")
    #print(df)
    #json_data = df.to_json(orient='records')
    #json_data = json.loads(json_data)
    #print(json)
    #print("------------------------------------ JSON")
    
    f= open("./dataset/solution1.json", 'r')
    json_data = json.load(f)['fts_infos']
    result_json = converter.create_solution_schedule(1, json_data) 
    #json_string = json.dumps(result_json, indent=2)
    #df = pd.read_json(json_string)
    #print(df)
    db_insert.insert_jsons(result_json)
    