from flask_pymongo import PyMongo 
import logging

class Database:
    def __init__(self, app):
        self.app = app
        self.connect(self.app)

    def connect(self, app):
        # Initialize the PyMongo object with the app
        self.db = PyMongo(app)
        logging.debug("Connected to MongoDB")
