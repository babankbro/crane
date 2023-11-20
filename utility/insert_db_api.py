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
        
    def clear_table(self, table_name, sid, sol_name_id = "solution_id"):
        sql = f"DELETE FROM {table_name} WHERE {sol_name_id} = {sid};"
        self.cursor.execute(sql)
        self.db.commit()
        
    def clear_solution(self, sid):
        self.clear_table("solution_crane_schedule", sid)
        self.clear_table("crane_solution", sid)
        self.clear_table("solution_carrier_order", sid, sol_name_id="s_id")
        sql = f"DELETE FROM solution_schedule WHERE solution_id = {sid};"
        self.cursor.execute(sql)
        self.db.commit()
        
        
        
    def insert_jsons(self, json_data):
        colum_names = """solution_id,	 FTS_id,	 carrier_id,	 latlng	,
            arrivaltime,	exittime,	operation_time,	Setup_time,	travel_Distance,
            travel_time, operation_rate,	consumption_rate, cargo_id"""
        for d in json_data:
            #print(d)
            d["arrivaltime"] = f"'{d['arrivaltime']}'"
            d["exittime"] = f"'{d['exittime']}'"
            values = [str(d[x]) for x in d]
            columns = [x for x in d]
            colum_names = ', '.join(columns)
           
            values = ', '.join(values)
            #print(colum_names)
            #print(values)
            values = values.replace('None', 'NULL')
            print(values )
            insert_query = f"INSERT INTO solution_schedule({colum_names}) VALUES ({values})"
            #print(insert_query)
            self.cursor.execute(insert_query)
            self.db.commit()
            
    def insert_crane_solution_schedule_jsons(self, json_data):
        colum_names = """solution_id,	
                    carrier_id,	
                    start_time,	due_time,	operation_time,	Setup_time,	
                    travel_Distance,	
                    travel_time,	operation_rate,
                    consumption_rate,
                    crane_id,	
                    bulk,	
                    load_cargo,
                    cargo_id, 
                    penalty_cost, 
                    reward"""
        for d in json_data:
            #print(d)
            d["start_time"] = f"'{d['start_time']}'"
            d["due_time"] = f"'{d['due_time']}'"
            d["penalty_cost"] = 0
            d["reward"] = 0
            values = [str(d[x]) for x in d]
            columns = [x for x in d]
            colum_names = ', '.join(columns)
           
            values = ', '.join(values)
            #print(colum_names)
            #print(values)
            values = values.replace('None', 'NULL')
            insert_query = f"INSERT INTO solution_crane_schedule({colum_names}) VALUES ({values})"
            #print(insert_query)
            self.cursor.execute(insert_query)
            self.db.commit()

    def insert_crane_solution_jsons(self, json_data):
        colum_names = """solution_id,	
                            FTS_id,	
                            crane_id,	
                            total_cost,	
                            total_consumption_cost,	
                            total_wage_cost,	
                            penality_cost,	
                            total_reward,	
                            total_late_time,	
                            total_early_time,	
                            total_operation_consumption_cost,
                            total_operation_time,
                            total_preparation_crane_time,
                            date"""
        for d in json_data:
            d["date"] = f"'{d['date']}'"
            #print(d)
            values = [str(d[x]) for x in d]
            columns = [x for x in d]
            colum_names = ', '.join(columns)
           
            values = ', '.join(values)
            #print(colum_names)
            #print(values)
            values = values.replace('None', 'NULL')
            insert_query = f"INSERT INTO crane_solution({colum_names}) VALUES ({values})"
            #print(insert_query)
            self.cursor.execute(insert_query)
            self.db.commit()
        print("insert", len(json_data))

    def insert_carrier_solution_jsons(self, json_data):
        colum_names = """s_id,  
                         order_id,
                         start_time,
                        finish_time,
                        penalty_cost, 
                        reward"""
        for d in json_data:
            d["start_time"] = f"'{d['start_time']}'"
            d["finish_time"] = f"'{d['finish_time']}'"
            #print(d)
            values = [str(d[x]) for x in d]
            columns = [x for x in d]
            colum_names = ', '.join(columns)
           
            values = ', '.join(values)
            #print(colum_names)
            #print(values)
            values = values.replace('None', 'NULL')
            insert_query = f"INSERT INTO solution_carrier_order({colum_names}) VALUES ({values})"
            #print(insert_query)
            self.cursor.execute(insert_query)
            self.db.commit()
        print("insert", len(json_data))


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
    