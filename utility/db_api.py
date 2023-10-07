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

mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="sugarotpzlab_crane",
  password="P@ssw0rd;Crane"
)

mycursor = mydb.cursor(dictionary=True)
mycursor.execute('USE sugarotpzlab_crane')


def get_all_FTS():
    mycursor.execute("select * from fts;")
    rows = mycursor.fetchall()
    return rows

def get_all_crane_FTS():
    mycursor.execute("""select *
                     from fts 
                     inner join crane on fts.id=crane.fts_id;""")
    rows = mycursor.fetchall()
    return rows

def get_all_rates():
    mycursor.execute("""select * from cargo_crane
                        join crane on cargo_crane.crane_id=crane.id
                        join cargo on cargo_crane.cargo_id=cargo.cargo_id
                        join fts on fts.id=crane.fts_id
                        order by cargo_crane.crane_id;""")
    rows = mycursor.fetchall()
    return rows

def get_all_orders():
    mycursor.execute("""select * from cargo_order
                        join cargo on cargo_order.cargo_id=cargo.cargo_id
                        join carrier_order on cargo_order.order_id=carrier_order.or_id
                        join carrier on carrier_order.cr_id=carrier.cr_id
                        order by cargo_order.order_id;""")
    rows = mycursor.fetchall()
    return rows



def get_all_cargo():
    
    mycursor.execute("select * from cargo;")
    rows = mycursor.fetchall()
    #json_data = json.dumps(rows, indent=4)
    #data_dict = json.loads(json_data)

    #print(data_dict)
    return rows



def get_all_floatingCrane():
    mycursor.execute("select * from floating_crane")
    rows = mycursor.fetchall()
    
    return rows

def get_all_carrier():
    mycursor.execute("select * from carrier")
    rows = mycursor.fetchall()
    return rows

def get_all_cargo_crane():
    mycursor.execute("""
        SELECT cargo_crane_id,floating_crane.floating_name,cargo.cargo_name,cargo_crane.consumption_rate,cargo_crane.work_rate,cargo.category 
        FROM cargo_crane INNER JOIN floating_crane ON cargo_crane.floating_id = floating_crane.floating_id 
        INNER JOIN cargo ON cargo_crane.cargo_id = cargo.cargo_id
        """)
    rows = mycursor.fetchall()
    return rows

if __name__ == "__main__":
    mycursor.execute('Show Tables')
    rows = mycursor.fetchall()
    [print(row) for row in rows]
    
    order_data = get_all_orders()
    print(order_data[""])
