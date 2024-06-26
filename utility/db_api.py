import mysql.connector
import time
import datetime
import pytz
import json
from json import JSONEncoder
import datetime
import os
import glob

class DateTimeEncoder(JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (datetime.timedelta, )):
                delta = obj
                days = delta.days
                hours, remainder = divmod(delta.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)

# Convert to a formatted string
                formatted_string = "{:02}:{:02}:{:02}".format(days, hours, minutes)
                return formatted_string
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()


def try_connect_db():
    global mydb, mycursor
    if mydb and mydb.is_connected() :
        print("Use Last connect")
        return mydb, mycursor
    
    try:
        mydb = mysql.connector.connect(
            host="127.0.0.1",
            #user="sugarotpzlab_crane",
            #password="P@ssw0rd;Crane"
            user="root",
            password="PVWtLvJGNUBPlmj71R6bAao="

        )
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute('USE sugarotpzlab_crane')
    except:
        print("No connect database")
    return mydb, mycursor

def query_table(name):
    global mydb, mycursor
    mydb, mycursor = try_connect_db()
    mycursor.execute(f"select * from {name}")
    rows = mycursor.fetchall()
    return rows

def query_table_where(name, condition):
    global mydb, mycursor
    mydb, mycursor = try_connect_db()
    mycursor.execute(f"select * from {name} where {condition}")
    rows = mycursor.fetchall()
    return rows

def query_table_join_where(tables, join_condition, condition):
    global mydb, mycursor
    mydb, mycursor = try_connect_db()
    sql_str =  f"select * from {tables[0]} "
    for i in range(1, len(tables)):
         sql_str += f"left join {tables[i]} on {join_condition[i-1]} "
    sql_str += f"where {condition}"
    #print(sql_str)
    mycursor.execute(sql_str)
    rows = mycursor.fetchall()
    return rows


def get_all_FTS():
    global mydb, mycursor
    mydb, mycursor = try_connect_db()
    mycursor.execute("select * from fts;")
    rows = mycursor.fetchall()
    return rows

def get_all_crane_FTS():
    global mydb, mycursor
    mydb, mycursor = try_connect_db()
    mycursor.execute("""select *
                     from fts 
                     inner join crane on fts.id=crane.fts_id;""")
    rows = mycursor.fetchall()
    return rows

def get_all_rates():
    global mydb, mycursor
    mydb, mycursor = try_connect_db()
    mycursor.execute("""select * from cargo_crane
                        join crane on cargo_crane.crane_id=crane.id
                        join cargo on cargo_crane.cargo_id=cargo.cargo_id
                        join fts on fts.id=crane.fts_id
                        order by cargo_crane.crane_id;""")
    rows = mycursor.fetchall()
    return rows

def get_all_orders(isAll=False, isApproved=False):
    global mydb, mycursor
    mydb, mycursor = try_connect_db()
    ig = ""
    if not isApproved:
        ig = "!"
    where_command = f'where carrier_order.status_order {ig}= "Approved"'
    if isAll:
        where_command = ''
        if isApproved:
            return []
        
    mycursor.execute(f"""select * from cargo_order
                        join cargo on cargo_order.cargo_id=cargo.cargo_id
                        join carrier_order on cargo_order.order_id=carrier_order.or_id
                        join carrier on carrier_order.cr_id=carrier.cr_id
                        {where_command}
                        order by cargo_order.order_id;""")
    rows = mycursor.fetchall()
    return rows

def get_all_cargo():
    global mydb, mycursor
    mydb, mycursor = try_connect_db()
    mycursor.execute("select * from cargo;")
    rows = mycursor.fetchall()
    #json_data = json.dumps(rows, indent=4)
    #data_dict = json.loads(json_data)

    #print(data_dict)
    return rows

def get_all_floatingCrane():
    global mydb, mycursor
    mydb, mycursor = try_connect_db()
    mycursor.execute("select * from floating_crane")
    rows = mycursor.fetchall()
    
    return rows

def get_all_carrier():
    global mydb, mycursor
    mydb, mycursor = try_connect_db()
    mycursor.execute("select * from carrier")
    rows = mycursor.fetchall()
    return rows

def get_all_cargo_crane():
    global mydb, mycursor
    mydb, mycursor = try_connect_db()
    mycursor.execute("""
        SELECT cargo_crane_id,floating_crane.floating_name,cargo.cargo_name,cargo_crane.consumption_rate,cargo_crane.work_rate,cargo.category 
        FROM cargo_crane INNER JOIN floating_crane ON cargo_crane.floating_id = floating_crane.floating_id 
        INNER JOIN cargo ON cargo_crane.cargo_id = cargo.cargo_id
        """)
    rows = mycursor.fetchall()
    return rows

def get_all_maintain_fts():
    return query_table('maintain_fts')

def get_all_maintain_crane():
    return query_table('maintain_crane')

def get_schedule_solution(solution_id):
    condition = f"solution_schedule.solution_id = {solution_id}"
    return query_table_join_where(["solution_schedule", "carrier", 'fts'], 
                                  [ "solution_schedule.carrier_id = carrier.cr_id",
                                    "solution_schedule.FTS_id = fts.id"], condition)

def get_cargo_loads_order(order_id):
    condition = f"bulks.cargo_orderOrder_id = {order_id}"
    bulks = query_table_where('bulks', condition)
    return [float(bluk["load_bulk"]) for bluk in bulks]

def get_solution_info(solution_id):
    condition = f"solutions.id = {solution_id}"
    infos = query_table_where('solutions', condition)
    if len(infos) == 1:
        start_date = infos[0]['started_at']
        end_date = infos[0]['ended_at']
        print(start_date)
        print(infos)
        new_start_date = start_date.replace(hour=0, minute=0, second=0)
        new_end_date = end_date.replace(hour=23, minute=59, second=59)
        infos[0]['started_at'] = new_start_date
        infos[0]['ended_at'] = new_end_date
        return infos[0]
    else:
        raise ValueError("Query solution unexpected id ") 

global mydb, mycursor
mydb = None
mydb, mycursor = try_connect_db()

if __name__ == "__main__":
    mycursor.execute('Show Tables')
    rows = mycursor.fetchall()
    [print(row) for row in rows]
    
    #maintain = get_all_maintain_fts()
    #maintain = get_all_maintain_crane()
    #schedule = get_schedule_solution(56)
    #for d in schedule:
        #print(d)
    #order_data = get_all_orders()
    #for d in order_data:
        #print(d)
    #bulks = get_cargo_loads_order(7306)
    #[print(bluk) for bluk in bulks]
    #print(sum(bulks))
    info = get_solution_info(114)
    print(info['started_at'])
    print(info['ended_at'])
    print(info)
