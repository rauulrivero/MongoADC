from flask import Blueprint, render_template, request, jsonify
import json
from src.database.Database import mongo
from src.services.mongo_service import MongoServices
from src.auth.auth import Authentication
from src.database.data_processing import init_df_football, insert_players_df
from src.services.predict_winner import calcular_clubes_ordenados, compare_teams, insert_normalized_df
from src.services.lineup_by_year import generate_player_lineups_by_season, get_best_players_by_season_and_team
from src.services.player_clusterization import insert_cluster, get_player_rank



api = Blueprint('api', __name__)

mongo_service = MongoServices(mongo)
auth = Authentication()

@api.route('/', methods=['GET'])
def index():
    return jsonify({"message": "API de Football Analytics"})

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

@api.route('/init_lineups_df', methods=['POST'])
def generate_lineups():
    result = generate_player_lineups_by_season()
    return json.dumps(result)

@api.route('/get_seasons', methods=['GET'])
def get_seasons():
    result = mongo_service.get_seasons()
    return json.dumps(result)

@api.route('/get_best_players_by_season_and_team', methods=['POST'])
def get_best_players_by_season_and_team_route():
    data = request.get_json()

    if not all([data['season'], data['club_id']]):
        return json.dumps({"error": "Se requieren la temporada y el ID del club"}), 400
    
    season = data['season']
    club_id = data['club_id']

    result = get_best_players_by_season_and_team(season, club_id)
    return json.dumps(result)

@api.route('/get_teams_by_season/<competition_id>/<int:season>', methods=['GET'])
def get_teams_by_season_route(competition_id, season):
    result = mongo_service.get_teams_by_season(competition_id, season)
    return json.dumps(result)

@api.route('/data_of_cluster_of_players', methods=['GET'])
def data_of_cluster_of_players_route():
    result = insert_players_df()
    return result

@api.route("/insert_cluster", methods=['POST'])
def insert_cluster_route():
    result = insert_cluster()
    return json.dumps(result)

@api.route("/get_player_rank/<player_id>", methods=['GET'])
def get_player_rank_route(player_id):
    result = get_player_rank(player_id)
    return json.dumps(result)