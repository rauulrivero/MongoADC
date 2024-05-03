from flask import Blueprint, render_template, request, jsonify
import json
from src.database.Database import mongo
from src.services.mongo_service import MongoServices
from src.auth.auth import Authentication
from src.services.api_service import add_event_by_season_service, get_events_by_teams_service
from src.database.data_processing import init_df_football
from src.predict.predict_model import calcular_clubes_ordenados, compare_teams, insert_normalized_df


api = Blueprint('api', __name__)

mongo_service = MongoServices(mongo)
auth = Authentication()

@api.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@api.route('/create_user', methods=['POST'])
def create_user():
    data = request.get_json()
    name = data['name']
    password = data['password']
    email = data['email']
    

    if not all([name, password, email]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400
        
    if mongo_service.user_exists(email):
        return jsonify({"error": "El usuario ya existe"}), 409
        
    mongo_service.create_user(name, email, password)
    return jsonify({"message": "Usuario creado exitosamente"}), 201

@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']
    
    if not all([email, password]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400
    
    user = mongo_service.get_user(email)
    if user is None:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    if user['password'] != password:
        return jsonify({"error": "Contraseña incorrecta"}), 401
    
    auth.set_user(email, password)
    return jsonify({"message": "Inicio de sesión exitoso"}), 200

@api.route('/logout', methods=['POST'])
def logout():
    auth.logout()
    return jsonify({"message": "Cierre de sesión exitoso"}), 200


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
        
    events = get_events_by_teams_service(local_team, away_team) 
        
    return json.dumps({"result" : f"{events}"})
    

@api.route('/init_df_football', methods=['POST'])
def init_df_football_route():
    result = init_df_football()
    return result

@api.route('/init_df_normalized', methods=['GET'])
def insert_normalized_df_route():
    result = insert_normalized_df()
    return result

@api.route('/calcular_clubes_ordenados', methods=['GET'])
def calcular_clubes_ordenados_route():
    result = calcular_clubes_ordenados()
    return json.dumps(result)

@api.route('/predict_winner', methods=['POST'])
def compare_teams_route():
    data = request.get_json()
    
    if not all([data['local_team_id'], data['away_team_id']]):
        return json.dumps({"error": "Se requieren los IDs de los clubes 'local_team_id' y 'away_team_id'."}), 400
    
    local_team_id = data['local_team_id']
    away_team_id = data['away_team_id']
    
    result = compare_teams(local_team_id, away_team_id)
    
    return json.dumps({"prediction": result})

@api.route('/get_competitions', methods=['GET'])
def get_competitions_route():
    result = mongo_service.get_competitions()
    return json.dumps(result)

@api.route('/get_teams/<competition_id>', methods=['GET'])
def get_teams_route(competition_id):
    result = mongo_service.get_teams_by_competition_id_service(competition_id)
    return json.dumps(result)