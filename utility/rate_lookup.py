import pandas as pd
import numpy as np
from json import JSONEncoder
from lookup_data import *
from db_api import *

class FTS_CRANE_RATE(dict):
    def __init__(self, fts_id, fts_name, df_fts) -> None:
        self.name = fts_name
        self.id = fts_id
        self.df_fts = df_fts
        self.crane_lookup = {}
        self.cranes = []
        self.setup_time_cranes = []
        self.wage_month_costs  = []
        self.premium_rates = []
        self.crane_ids = np.unique(self.df_fts['crane_id'])
        for crane_id in self.crane_ids:
            df_crane = self.df_fts.loc[ self.df_fts["crane_id"] == crane_id ]
            crane_name = np.unique(df_crane['crane_name'])[0] 
            setup_time = np.unique(df_crane['setuptime_crane'])[0]
            wage_month_cost = np.unique(df_crane['wage_month_cost'])[0]
            premium_rate = np.unique(df_crane['premium_rate'])[0]
            self.setup_time_cranes.append(setup_time/60)
            self.wage_month_costs.append(wage_month_cost)
            self.premium_rates.append(premium_rate)
            #print(fts_id, fts_name)      
            #print(results)         
            crane_rate = CRANE_CARGO_RATE(self, crane_id, crane_name, df_crane)
            self.crane_lookup[crane_id] = crane_rate
            self.cranes.append(crane_rate)
        
        self.display_cargo_name = None
        self.category = None
            
    def set_display_rate(self, cargo_name, category):
        self.display_cargo_name = cargo_name
        self.category = category
        for crane_id in self.crane_lookup:
            self.crane_lookup[crane_id].set_display_rate(cargo_name, category)
    
    def __str__(self):
        result = ''
        for crane_id in self.crane_lookup:
            result += f"\t{self.crane_lookup[crane_id]}\n"
        return f"{self.name}: \n {result}" 


class CRANE_CARGO_RATE(dict):
    def __init__(self, fts, crane_id, crane_name, df_crane) -> None:
        self.crane_name = crane_name
        self.crane_id = crane_id
        self.df_crane = df_crane
        self.fts = fts
        self.category_id_lookup = {'import': 0, 'export':1}
        self.category_name_lookup = {0: 'import', 1:'export'}
        self.consumption_rates = []
        self.operation_rates = []
        self.cargo_names = np.unique(df_crane["cargo_name"])
        self.cargo_id_lookup = {}
        #print(df_crane)
        for i in range(len(self.cargo_names)):
            self.cargo_id_lookup[self.cargo_names[i]] = i
        
        for i in range(len(self.category_id_lookup)):
            key = self.category_name_lookup[i]
            crates = []
            orates = []
            for cargo in self.cargo_names:
                result = self.df_crane.loc[ (self.df_crane["category"] == key) &
                                       (self.df_crane["cargo_name"] == cargo)]
                if len(result) > 0:
                    crates.append(result.iloc[0]['consumption_rate'])
                    orates.append(result.iloc[0]['work_rate'])
                else:
                    result = self.df_crane.loc[ (self.df_crane["cargo_name"] == cargo)]
                    if len(result) > 0:
                        crates.append(result.iloc[0]['consumption_rate'])
                        orates.append(result.iloc[0]['work_rate'])
                    else:
                        print("Need to Fix missing =================================================")
                        crates.append(-1)
                        orates.append(-1)
            
            self.consumption_rates.append(crates)
            self.operation_rates.append(orates)
        self.consumption_rates = np.array(self.consumption_rates)
        self.operation_rates = np.array(self.operation_rates)
        self.display_cargo_name = None
        self.category = None
    
    def get_rates(self, cargo_name, category):
        index1 = self.category_id_lookup[category]
        index2 = self.cargo_id_lookup[cargo_name]
        return {'consumption_rate': self.consumption_rates[index1, index2] , 
                'operation_rate': self.operation_rates[index1, index2] } 
        
    def set_display_rate(self, cargo_name, category):
        self.display_cargo_name = cargo_name
        self.category = category
        
    
    def __str__(self):
        crates =self.consumption_rates
        orates =self.operation_rates
        ctype = ""
        if self.display_cargo_name != None:
            rates = self.get_rates(self.display_cargo_name, self.category)
            crates = rates['consumption_rate']
            orates = rates['operation_rate']
            ctype = f"{self.display_cargo_name} {self.category}"
            
        return f"{self.crane_name}  {ctype}: crate: {crates} orate: {orates}"


class FTS_INFO_LOOKUP(dict):
    def __init__(self, crane_rate_df, maintain_fts_df, maintain_crane_df):
        self.crane_id_lookup = {}
        self.crane_name_lookup = {}
        self.crane_index_id_lookup = {}
        self.crane_index_lookup = {}
        
        self.fts_id_lookup = {}
        self.fts_name_lookup = {}
        self.fts_index_id_lookup = {}
        self.fts_index_lookup = {}
        
        self.cargo_id_lookup = {}
        self.cargo_name_lookup = {}
        self.cargo_index_id_lookup = {}
        self.cargo_index_lookup = {}
        self.category_id_lookup = {'import': 0, 'export':1}
        self.category_name_lookup = {0: 'import', 1:'export'}
        self.crane_rate_df = crane_rate_df
        crane_ids = np.unique(crane_rate_df["crane_id"])
        crane_names = np.unique(crane_rate_df["crane_name"])
        cargo_ids = np.unique(crane_rate_df["cargo_id"])
        cargo_names = np.unique(crane_rate_df["cargo_name"])
        
        fts_ids = np.unique(crane_rate_df["FTS_id"])
        fts_names = np.unique(crane_rate_df["FTS_name"])
        #print(crane_rate_df)
        for i in range(len(crane_ids)):
            self.crane_id_lookup[crane_names[i]] =  crane_ids[i]
            self.crane_name_lookup[crane_ids[i]] =  crane_names[i]
            self.crane_index_id_lookup[i] = crane_ids[i]
            self.crane_index_lookup[crane_ids[i]] = i
            
        for i in range(len(fts_ids)):
            self.fts_id_lookup[fts_names[i]] =  fts_ids[i]
            self.fts_name_lookup[fts_ids[i]] =  fts_names[i]
            self.fts_index_id_lookup[i] = fts_ids[i]
            self.fts_index_lookup[fts_ids[i]] = i
            
        for i in range(len(cargo_ids)):
            self.cargo_id_lookup[cargo_names[i]] =  cargo_ids[i]
            self.cargo_name_lookup[cargo_ids[i]] =  cargo_names[i]
            self.cargo_index_id_lookup[i] = cargo_ids[i]
            self.cargo_index_lookup[cargo_ids[i]] = i
        
        self.raw_data_consumption_rates = []
        self.raw_data_operation_rates = []
        for i in range(len(crane_ids)):
            crane_id = self.crane_index_id_lookup[i]
            crane_consumption_rates = []
            crane_operation_rates = []
            for j in range(2):
                category_name = self.category_name_lookup[j] 
                category_consumption_rates = []
                category_operation_rates = []
                for k in range(len(cargo_ids)):
                    cargo_id = self.cargo_index_id_lookup[k]
                    
                    result = self.crane_rate_df.loc[ (self.crane_rate_df["crane_id"] == crane_id) &
                                       (self.crane_rate_df["cargo_id"] == cargo_id) &
                                       (self.crane_rate_df["category"] == category_name)]
                    if len(result) == 0:
                        result = self.crane_rate_df.loc[ (self.crane_rate_df["crane_id"] == crane_id) &
                                       (self.crane_rate_df["cargo_id"] == cargo_id) ]
                        print("Fixed missing =================================================")
                    crate = result.iloc[0]['consumption_rate']
                    orate = result.iloc[0]['work_rate']
                    category_consumption_rates.append(crate)
                    category_operation_rates.append(orate)
                    #print(crane_id, category_name, cargo_id, crate, orate)
                    
                crane_consumption_rates.append(category_consumption_rates)
                crane_operation_rates.append(category_operation_rates)
                    
            self.raw_data_consumption_rates.append(crane_consumption_rates)
            self.raw_data_operation_rates.append(crane_operation_rates)
            
        self.raw_data_consumption_rates = np.array(self.raw_data_consumption_rates)
        self.raw_data_operation_rates = np.array(self.raw_data_operation_rates)
        #print(self.raw_data_consumption_rates.shape, self.raw_data_operation_rates.shape)  
        
        
        self.raw_data_fts_consumption_rates = []
        self.raw_data_fts_operation_rates = []
        for i in range(len(fts_ids)):
            fts_id = self.fts_index_id_lookup[i]
            crane_ids = np.unique(self.crane_rate_df[self.crane_rate_df["FTS_id"] == fts_id]['crane_id'])
            fts_consumption_rates = []
            fts_operation_rates = []
            
            for j in range(2):
                category_name = self.category_name_lookup[j] 
                category_consumption_rates = []
                category_operation_rates = []
                for k in range(len(cargo_ids)):
                    cargo_id = self.cargo_index_id_lookup[k]
                    totalc = 0
                    totalo = 0
                    for crane_id in crane_ids:
                        crate = self.get_consumption_rate_by_id(crane_id, j, cargo_id)
                        orate = self.get_operation_rate_by_id(crane_id, j, cargo_id)
                        totalc += crate
                        totalo += orate
                    totalc /= len(crane_ids)
                    totalo /= len(crane_ids)
                    category_consumption_rates.append(totalc)
                    category_operation_rates.append(totalo)
                fts_consumption_rates.append(category_consumption_rates)
                fts_operation_rates.append(category_operation_rates)
            
            self.raw_data_fts_consumption_rates.append(fts_consumption_rates)
            self.raw_data_fts_operation_rates.append(fts_operation_rates)
        
        self.raw_data_fts_consumption_rates = np.array(self.raw_data_fts_consumption_rates)
        self.raw_data_fts_operation_rates = np.array(self.raw_data_fts_operation_rates)
        #print(self.raw_data_consumption_rates.shape, self.raw_data_operation_rates.shape)  
                        
        
        
        fts_ids = np.unique(self.crane_rate_df['FTS_id'])
        #print(self.crane_rate_df)
        self.lookup_fts_ids = {}
        for fts_id in fts_ids:
            df_fts = self.crane_rate_df.loc[ self.crane_rate_df["FTS_id"] == fts_id ]
            single_maintain_df = maintain_fts_df.loc[ maintain_fts_df["mt_FTS_id"] == fts_id ]
            print(df_fts)
            print(single_maintain_df)
            print( "", np.unique(df_fts["crane_id"]))
            
            fts_name = np.unique(df_fts['FTS_name'])[0] 
            print("FTS_ID", fts_id, fts_name)      
            #print(results)         
            fts_rate = FTS_CRANE_RATE(fts_id, fts_name, df_fts)
            self.lookup_fts_ids[fts_id] = fts_rate
    
    def get_consumption_rate_by_id(self, crane_id, category_id, cargo_id):
        crane_index  = self.crane_index_lookup[crane_id]
        cargo_index  = self.cargo_index_lookup[cargo_id]
        return self.raw_data_consumption_rates[crane_index, category_id, cargo_index]
    
    def get_consumption_rate_by_name(self, crane_name, category, cargo_name):
        crane_id = self.crane_id_lookup[crane_name]
        category_id = self.category_id_lookup[category]
        cargo_id = self.cargo_id_lookup[cargo_name]
        return self.get_consumption_rate_by_id(crane_id, category_id, cargo_id)
    
    def get_operation_rate_by_id(self, crane_id, category_id, cargo_id):
        crane_index  = self.crane_index_lookup[crane_id]
        cargo_index  = self.cargo_index_lookup[cargo_id]
        return self.raw_data_operation_rates[crane_index, category_id, cargo_index]
    
    def get_operation_rate_by_name(self, crane_name, category, cargo_name):
        crane_id = self.crane_id_lookup[crane_name]
        category_id = self.category_id_lookup[category]
        cargo_id = self.cargo_id_lookup[cargo_name]
        return self.get_operation_rate_by_id(crane_id, category_id, cargo_id)
    
    def get_operation_rate_by_fts_id(self, fts_id, category_id, cargo_id):
        fts_index  = self.fts_index_lookup[fts_id]
        cargo_index  = self.cargo_index_lookup[cargo_id]
        return self.raw_data_operation_rates[fts_index, category_id, cargo_index]
    
    def get_operation_rate_by_fts_name(self, fts_name, category, cargo_name):
        fts_id = self.fts_id_lookup[fts_name]
        category_id = self.category_id_lookup[category]
        cargo_id = self.cargo_id_lookup[cargo_name]
        return self.get_operation_rate_by_fts_id(fts_id, category_id, cargo_id)
    
    def get_consumption_rate_by_fts_id(self, fts_id, category_id, cargo_id):
        fts_index  = self.fts_index_lookup[fts_id]
        cargo_index  = self.cargo_index_lookup[cargo_id]
        return self.raw_data_fts_consumption_rates[fts_index, category_id, cargo_index]
    
    def get_consumption_rate_by_fts_name(self, fts_name, category, cargo_name):
        fts_id = self.fts_id_lookup[fts_name]
        category_id = self.category_id_lookup[category]
        cargo_id = self.cargo_id_lookup[cargo_name]
        return self.get_consumption_rate_by_fts_id(fts_id, category_id, cargo_id)
        
        
if __name__ == "__main__":
    crane_rate_json = get_all_rates()
    maintain_fts_df = pd.DataFrame(get_all_maintain_fts())
    maintain_crane_df = pd.DataFrame(get_all_maintain_crane())
    
    finish_maintain_times = maintain_fts_df['start_time_FTS'].to_numpy()
    start_maintain_times = maintain_fts_df['downtime_FTS'].to_numpy()
    #print("arrival_times", arrival_times)
    maintain_fts_df['start_maintain_times'] = convert_to_hours(start_maintain_times)
    maintain_fts_df['finish_maintain_times'] = convert_to_hours(finish_maintain_times)
    
    finish_maintain_times = maintain_crane_df['start_time'].to_numpy()
    start_maintain_times = maintain_crane_df['downtime'].to_numpy()
    #print("arrival_times", arrival_times)
    maintain_crane_df['start_maintain_times'] = convert_to_hours(start_maintain_times)
    maintain_crane_df['finish_maintain_times'] = convert_to_hours(finish_maintain_times)
    
   #print("Maintain_df")
    print(maintain_crane_df)
    print(maintain_fts_df)
    
    crane_rate_df = pd.DataFrame(crane_rate_json)
    rate_lookup = FTS_INFO_LOOKUP(crane_rate_df, maintain_fts_df, maintain_crane_df)