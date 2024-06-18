from pymongo import MongoClient
from dotenv import dotenv_values

def connect_db(): 
    try: 
        env_vals = dotenv_values()
        env_vals["port"] = int(env_vals["port"])
        mg_client = MongoClient(**env_vals)
    except Exception as e: 
        raise e
    else: 
        return mg_client

