import pandas as pd
import numpy as np
from json import JSONEncoder

class RATE_LOOKUP(dict):
    def __init__(self, crane_rate_df):
        self.crane_id_lookup = {}
        self.crane_name_lookup = {}
        self.crane_index_id_lookup = {}
        self.crane_index_lookup = {}
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
        for i in range(len(crane_ids)):
            self.crane_id_lookup[crane_names[i]] =  crane_ids[i]
            self.crane_name_lookup[crane_ids[i]] =  crane_names[i]
            self.crane_index_id_lookup[i] = crane_ids[i]
            self.crane_index_lookup[crane_ids[i]] = i
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
        print(self.raw_data_consumption_rates.shape, self.raw_data_operation_rates.shape)  
        
        #print(self.crane_rate_df['category'])
    
    def get_consumption_rate_by_id(self, crane_id, category_id, cargo_id):
        crane_index  = self.crane_index_lookup[crane_id]
        cargo_index  = self.cargo_index_lookup[cargo_id]
        return self.raw_data_consumption_rates[crane_index, category_id, cargo_index]
    
    def get_consumption_rate_by_name(self, crane_name, category, cargo_name):
        crane_id = self.crane_id_lookup[crane_name]
        category_id = self.category_id_lookup[crane_name]
        cargo_id = self.cargo_id_lookup[cargo_name]
        return self.get_consumption_rate_by_id(crane_id, category_id, cargo_id)
    
    def get_operation_rate_by_id(self, crane_id, category_id, cargo_id):
        crane_index  = self.crane_index_lookup[crane_id]
        cargo_index  = self.cargo_index_lookup[cargo_id]
        return self.raw_data_operation_rates[crane_index, category_id, cargo_index]
    
    def get_operation_rate_by_name(self, crane_id, category, cargo_id):
        crane_id = self.crane_id_lookup[crane_name]
        category_id = self.category_id_lookup[crane_name]
        cargo_id = self.category_id_lookup[cargo_name]
        return self.get_operation_rate_by_id(crane_id, category_id, cargo_id)

    def default(self, o):
        return o.__dict__  
