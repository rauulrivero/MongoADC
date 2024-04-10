import os
from dotenv import load_dotenv

load_dotenv() 

class Config:
    FLASK_ENV = os.getenv('FLASK_ENV')
    MONGO_URI = os.getenv('MONGO_URI')
    THESPORTSDB_API_KEY = os.getenv('THESPORTSDB_API_KEY')
    BASE_URL = "https://www.thesportsdb.com/api/v1/json/"
    

class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True