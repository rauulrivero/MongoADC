from flask import jsonify

from src.database.Database import mongo
from src.api.TSDApiClient import TSDApiClient
from config.config import Config

api = TSDApiClient(Config.THESPORTSDB_API_KEY)

def add_event(team1, team2):
    response = api.make_request("searchevents.php", e=f"{team1}_vs_{team2}")

    if response['event'] == None:
        return jsonify({'response': 'No se encontraron resultados.'}), 404


    mongo.db.events.insert_many(response['events'])
    return jsonify({'response': "Se ha añadido con éxito."}), 200


def add_event_by_season_service(team1, team2, season):
    response = api.make_request("/searchevents.php", e=f"{team1}_vs_{team2}", s=season)

    print(response)

    if response['event'] == None:
        return jsonify({'response': 'No se encontraron resultados.'}), 404
    
    filtered_events = []
    for event in response['event']:
        filtered_event = {
            "strEvent": event["strEvent"],
            "dateEventLocal": event["dateEvent"],
            "strTime": event["strTime"],
            "strVenue": event["strVenue"],
            "intHomeScore": event["intHomeScore"],
            "intAwayScore": event["intAwayScore"],
        }
        filtered_events.append(filtered_event)

    mongo.db.events.insert_many(filtered_events)
    return jsonify({'response': "Se ha añadido con éxito."}), 200

def get_events_by_teams_service(team1, team2):
    response = mongo.db.events.find({"strEvent": f"{team1}_vs_{team2}"})
    events = []
    for event in response:
        events.append(event)
    return jsonify(events), 200