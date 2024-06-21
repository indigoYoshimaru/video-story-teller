from pymongo import MongoClient
from dotenv import dotenv_values

def connect_db(dotenv_path: str = "story_teller/database/.env"): 
    try: 
        env_vals = dotenv_values(dotenv_path)
        env_vals["port"] = int(env_vals["port"])
        mg_client = MongoClient(**env_vals)
    except Exception as e: 
        raise e
    else: 
        return mg_client

