from db_api import *
import pandas as pd
import numpy as np
from rate_lookup import *
from datetime import datetime
from distance_lookup import *

BASE_DATE_TIME = datetime(2022, 1, 1)
ns = 1e-9
def convert_to_hour_from_new_year(dt):
    #dt = datetime.utcfromtimestamp(npdate_time.astype(int)*ns)
    #dt = int(dt_obj.replace(tzinfo=timezone.utc).timestamp())
    delta = (dt - BASE_DATE_TIME).total_seconds() / 60/60
    return delta

def convert_to_hours(array_times):
    time_hours = []
    for i in range(len(array_times)):
        npdate_time = array_times[i]
        #print(npdate_time)
        if 'T' in npdate_time and 'Z' in npdate_time:
            npdate_time = npdate_time.replace("T", " ")
            npdate_time = npdate_time.replace(".000Z", "")
        
        npdate_time = datetime.strptime(npdate_time, '%Y-%m-%d %H:%M:%S')
        t = convert_to_hour_from_new_year(npdate_time)
        time_hours.append(t)
    return np.array(time_hours)

def create_fts_data(filter_fts=[]):
    fts_json = get_all_FTS()
    fts_df = pd.DataFrame(fts_json)
    if len(filter_fts) != 0:
        fts_df = fts_df[fts_df['FTS_name'].isin(filter_fts)]
    
    return {
        "NAME": fts_df['FTS_name'].to_numpy(),
        "FTS_ID":fts_df['id'].to_numpy(),
        "LAT": fts_df['lat'].to_numpy().astype(np.float),
        "LNG": fts_df['lng'].to_numpy().astype(np.float),
        "SETUP_TIME": fts_df['setuptime_FTS'].to_numpy().astype(np.float),
        "SPEED": fts_df['speed'].to_numpy().astype(np.float),
            }

def create_order_data(filter_carriers=[]):
    order_json = get_all_orders()
    order_df = pd.DataFrame(order_json)
    
    if len(filter_carriers) != 0:
        order_df = order_df[order_df['carrier_name'].isin(filter_carriers)]
    
    arrival_times = order_df['arrival_time'].to_numpy()
    dutedate_times = order_df['deadline_time'].to_numpy()
    #print("arrival_times", arrival_times)
    arrival_hour_times = convert_to_hours(arrival_times)
    dutedate_hour_times = convert_to_hours(dutedate_times)
    mhour = np.min(arrival_hour_times)
    index_min = np.argmin(arrival_hour_times)
    arrival_hour_times= arrival_hour_times - mhour
    dutedate_hour_times= dutedate_hour_times - mhour
    print("create_order_data", 'min time', order_df.iloc[index_min]['arrival_time'])
    print(order_df.columns)
    return {
        "MIN_DATE_TIME": order_df.iloc[index_min]['arrival_time'],
        "ARRIVAL_TIME": arrival_times,
        "ARRIVAL_TIME_HOUR": arrival_hour_times,
        "DUE_TIME": dutedate_times,
        "DUE_TIME_HOUR": dutedate_hour_times,
        "LAT": order_df['latitude'].to_numpy().astype(np.float),
        "LNG": order_df['longitude'].to_numpy().astype(np.float),
        "MAX_FTS": order_df['maxFTS'].to_numpy().astype(np.float),
        "DEMAND": order_df['load'].to_numpy().astype(np.float),
        "CATEGORY": order_df['category'].to_numpy() == 'import' ,
        "BULK": order_df['bulk'].to_numpy().astype(np.int),
        "CARGO": order_df['cargo_name'].to_numpy(),
        "CARGO_ID": order_df['cargo_id'].to_numpy(),
        "CARRIER": order_df['carrier_name'].to_numpy(),
        "CARRIER_ID":order_df['cr_id'].to_numpy(),
            }

def create_crane_rate_data():
    crane_rate_json = get_all_rates()
    crane_rate_df = pd.DataFrame(crane_rate_json)
    rate_lookup = RATE_LOOKUP(crane_rate_df)
    return rate_lookup

def print_json(fts_lookup):
    for key in fts_lookup:
        print(key, fts_lookup[key])
    #print(fts_lookup)
    
        
def print_order():
    order_json = get_all_orders()
    for row in order_json:
        #continue
        print(row)
    print(order_json)

if __name__ == "__main__":
    #print_order()
    #create_order_data()
    #print_json(create_order_data())
    print_json(create_order_data())
    rate_lookup = create_crane_rate_data()
    #print(rate_lookup.get_consumption_rate_by_id(1, 0, 21))
    #print(rate_lookup.get_operation_rate_by_id(1, 0, 21))
    order_data = create_order_data()
    print(order_data['ARRIVAL_TIME_HOUR'])
    
    #rates = get_all_rates()
    #for rate in rates:
        #print(rate)
    #rate_lookup = create_crane_rate_data()
    #fts_datalookup = create_fts_data()
    #print(pd.DataFrame(fts_datalookup))
    #print(pd.DataFrame(order_data))
    
    #distance_datalookup = Distance_Lookup(fts_datalookup, order_data)
    #print(distance_datalookup.DM)
    
    
