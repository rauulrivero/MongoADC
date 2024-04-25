from flask import Blueprint, render_template, request
import json
from src.services.api_service import add_event_by_season_service, get_events_by_teams_service
from src.database.data_processing import init_df_football
from src.predict.predict_model import calcular_clubes_ordenados

api = Blueprint('api', __name__)


@api.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@api.route('/add_event_by_season', methods=['POST'])
def add_event_by_season():
    # Asumiendo que recibes los datos en formato JSON en el cuerpo de la solicitud
    data = request.get_json()

    local_team = data['local_team']
    away_team = data['away_team']
    season = data['season']

    if not all([local_team, away_team, season]):
        return json.dumps({"error": "Se requieren los nombres de los equipos 'local_team' y 'away_team' y la temporada 'season'."}), 400
   
    result = add_event_by_season_service(local_team, away_team, season)  # Suponiendo que tienes esta función implementada
        
    # Retorna el resultado de la operación en formato JSON
    return result
    

@api.route('/get_events', methods=['POST'])
def get_events_route():
    # Asumiendo que recibes los datos en formato JSON en el cuerpo de la solicitud
    data = request.get_json()
    
    if not all([data['local_team'], data['away_team']]):
        return json.dumps({"error": "Se requieren los nombres de los equipos 'local_team' y 'away_team'."}), 400
    
    local_team = data['local_team']
    away_team = data['away_team']
        
    events = get_events_by_teams_service(local_team, away_team)  # Suponiendo que tienes esta función implementada
        
    return json.dumps({"result" : f"{events}"})
    

@api.route('/init_df_football', methods=['POST'])
def init_df_football_route():
    result = init_df_football()
    return result

@api.route('/calcular_clubes_ordenados', methods=['GET'])
def calcular_clubes_ordenados_route():
    result = calcular_clubes_ordenados()
    return json.dumps(result)

