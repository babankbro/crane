import sys

sys.path.insert(0, "./utility")
sys.path.insert(0, "./decoder")
from route_algorithm import CraneProblem
from crane_utility import *
from crane_configuration import *
from ship_assign import *
from crane_decoder import *
from decoder_v2 import *
import numpy as np
import pandas as pd
from output_converter import *
from insert_db_api import DBInsert
from output_converter import OutputConverter
#from utility.crane_utility import create_data_lookup
#from utility.lookup_data import create_order_data


if __name__ == "__main__":
    user_group = 3
    solution_id = 71
    mydb, mycursor = try_connect_db()
    data_lookup = create_data_lookup(isAll=True, group=user_group)

    print(data_lookup["ORDER_DATA"].keys())