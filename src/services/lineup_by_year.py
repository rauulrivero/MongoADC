from src.database.Database import mongo
from pymongo import errors

def generate_player_lineups_by_season():
    # Colecciones
    games_collection = mongo.db['games']
    appearances_collection = mongo.db['appearences']

    # Paso 1: Obtener un listado con todas las seasons a la tabla games
    seasons = games_collection.distinct('season')  # Esto asumiendo que 'season' es el nombre del campo
    print(f'Se han encontrado las siguientes temporadas: {seasons}')

    # Paso 2-5: Bucle a través de las seasons, filtrar games, filtrar appearances y sumar minutos
    for season in seasons:
        # Filtrar juegos por temporada
        game_ids = games_collection.find({'season': season}, {'game_id': 1})
        game_ids = [g['game_id'] for g in game_ids]
        print(f'Procesando temporada {season} con {len(game_ids)} juegos.')

        appearances = appearances_collection.find({'game_id': {'$in': game_ids}})

        # Crear estructura para almacenar los detalles por jugador y club
        team_details = {}
        for appearance in appearances:
            player_id = appearance['player_id']
            minutes_played = appearance['minutes_played']
            player_club_id = appearance['player_club_id']


            # Inicializar club_id si no existe
            if player_club_id not in team_details:
                team_details[player_club_id] = {}

            # Sumar minutos jugados
            if player_id not in team_details[player_club_id]:
                team_details[player_club_id][player_id] = {
                    'minutes_played': 0,
                }
            team_details[player_club_id][player_id]['minutes_played'] += minutes_played

        # Procesar cada club
        for club_id, players in team_details.items():

            # Preparar y guardar las líneas de jugadores para cada club
            for player_id, details in players.items():
                player_info = mongo.db.players.find_one({'player_id': player_id})

                if player_info is not None:
                    player_lineup = {
                        'player_name': player_info.get('name', 'Unknown'),
                        'player_id': player_id,
                        'club_id': club_id,  # Usar club_id del bucle
                        'position': player_info.get('position', 'Unknown'),  # Añadido manejador de None 
                        'minutes_played': details['minutes_played'],
                        'season': season
                    }
                
                    try:
                        mongo.db.player_lineup.insert_one(player_lineup)
                    except errors.DuplicateKeyError as e:
                        print(f"Duplicate key error: {e}")

    return 'response: Se ha añadido con éxito.'

def get_best_players_by_season_and_team(season, club_id):
    # Obtener jugadores con más minutos jugados por temporada y club
    pipeline = [
        {"$match": {"season": season, "club_id": club_id}},
        {"$group": {
            "_id": "$player_id",
            "player_name": {"$first": "$player_name"},
            "position": {"$first": "$position"},
            "total_minutes": {"$sum": "$minutes_played"}
        }},
        {"$sort": {"total_minutes": -1}},
        {"$limit": 11}
    ]
    top_players = mongo.db.player_lineup.aggregate(pipeline)
    return list(top_players)
