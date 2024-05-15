import os
from dotenv import load_dotenv

load_dotenv() 

class Config:
    MONGO_URI = os.getenv('MONGO_URI')
    THESPORTSDB_API_KEY = os.getenv('THESPORTSDB_API_KEY')
    BASE_URL = "https://www.thesportsdb.com/api/v1/json/"