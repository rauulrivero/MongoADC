from flask import Flask
from config.config import Config
from src.database.Database import mongo

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config['MONGO_URI'] = Config.MONGO_URI


    mongo.init_app(app)

    
    return app


