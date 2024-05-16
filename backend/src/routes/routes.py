from flask import Blueprint, request, jsonify
import json
from src.database.Database import mongo
from src.services.mongo_service import MongoServices
from src.auth.auth import Authentication
from src.database.data_processing import init_df_football, insert_players_df
from src.services.predict_winner import compare_teams, insert_normalized_df
from src.services.lineup_by_year import generate_player_lineups_by_season, get_best_players_by_season_and_team
from src.services.player_clusterization import insert_clusters, get_player_rank



api = Blueprint('api', __name__)

mongo_service = MongoServices(mongo)
auth = Authentication()

@api.route('/', methods=['GET'])
def index():
    return jsonify({"message": "API de Football Analytics"})


# RUTAS DE INICIALIZACIÓN DE BASE DE DATOS


@api.route('/initialize_database', methods=['GET'])
def initialize_database():
    try:
        # Inicializar la base de datos con los datos de fútbol
        init_df_football()

        print("Datos de fútbol inicializados")

        # Insertar DataFrame normalizado
        insert_normalized_df()

        print("DataFrame normalizado insertado")

        # Inserción de datos de cluster de jugadores
        insert_players_df()

        print("Datos de jugadores insertados")

        # Generar datos de alineaciones de jugadores por temporada
        generate_player_lineups_by_season()

        print("Datos de alineaciones de jugadores generados")
    
        # Inserción de datos de cluster de jugadores
        insert_clusters()

        print("Datos de cluster de jugadores insertados")

        # Devolver una respuesta del éxito de la inicialización
        return jsonify({
            "message": "Inicialización de la base de datos completa"
        }), 200

    except Exception as e:
        # En caso de un error, devolver un mensaje indicando el fallo en la inicialización
        return jsonify({"error": str(e)}), 500
    


# RUTAS DE USUARIO


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



# RUTAS DE CONSULTA DE DATOS


@api.route('/get_competitions', methods=['GET'])
def get_competitions_route():
    result = mongo_service.get_competitions()
    return json.dumps(result)

@api.route('/get_teams/<competition_id>', methods=['GET'])
def get_teams_route(competition_id):
    result = mongo_service.get_teams_by_competition_id_service(competition_id)
    return json.dumps(result)

@api.route('/get_seasons', methods=['GET'])
def get_seasons():
    result = mongo_service.get_seasons()
    return json.dumps(result)


@api.route('/get_players', methods=['GET'])
def get_players_route():
    result = mongo_service.get_players()
    return json.dumps(result)


@api.route('/get_teams_by_season/<competition_id>/<int:season>', methods=['GET'])
def get_teams_by_season_route(competition_id, season):
    result = mongo_service.get_teams_by_season(competition_id, season)
    return json.dumps(result)




# RUTAS DE PREDICCIÓN Y ANÁLISIS DE DATOS

@api.route('/get_best_players_by_season_and_team', methods=['POST'])
def get_best_players_by_season_and_team_route():
    data = request.get_json()

    if not all([data['season'], data['club_id']]):
        return json.dumps({"error": "Se requieren la temporada y el ID del club"}), 400
    
    season = data['season']
    club_id = data['club_id']

    result = get_best_players_by_season_and_team(season, club_id)
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

@api.route("/get_player_rank/<player_id>", methods=['GET'])
def get_player_rank_route(player_id):
    result = get_player_rank(player_id)
    return json.dumps(result)
