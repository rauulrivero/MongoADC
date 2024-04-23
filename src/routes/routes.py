from flask import Blueprint, render_template, request, jsonify
from src.services.CrudServices import add_event_by_season_service, get_events_by_teams_service


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
        return jsonify({"error": "Se requieren los nombres de los equipos 'local_team' y 'away_team' y la temporada 'season'."}), 400
   
    result = add_event_by_season_service(local_team, away_team, season)  # Suponiendo que tienes esta función implementada
        
    # Retorna el resultado de la operación en formato JSON
    return jsonify({"result": result})

    

@api.route('/get_events', methods=['POST'])
def get_events():
    # Asumiendo que recibes los datos en formato JSON en el cuerpo de la solicitud
    data = request.get_json()
    
    # Verifica si los datos contienen los equipos
    if 'local_team' in data and 'away_team' in data:
        local_team = data['local_team']
        away_team = data['away_team']
        
        # Aquí deberías implementar la lógica para obtener los eventos por equipos
        # desde tu archivo JSON o base de datos
        events = get_events_by_teams_service(local_team, away_team)  # Suponiendo que tienes esta función implementada
        
        # Retorna los eventos encontrados en formato JSON
        return jsonify(events)
    else:
        # Si no se proporcionan equipos, devuelve un mensaje de error
        return jsonify({"error": "Se requieren los nombres de los equipos 'team1' y 'team2'."}), 400

