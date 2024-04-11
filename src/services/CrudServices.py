from flask import jsonify

from src.database.Database import mongo
from src.api.TSDApiClient import TSDApiClient
from config.config import Config

api = TSDApiClient(Config.THESPORTSDB_API_KEY)

def create_team(team):
    response = api.make_request("/searchteams.php", t=team)

    print(response['teams'])
    if response['teams'] == None:
        return jsonify({'response': 'No se encontraron resultados.'}), 404
    
    mongo.db.teams.insert_one(response['teams'][0])

    
    return jsonify({'response': "Se ha guardado con éxito."}), 200