from src.database.Database import mongo
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from flask import jsonify

# Función de normalización
def normalize(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value)

def calcular_clubes_ordenados():
    # Encontrar valores máximos y mínimos
    max_win_percentage = mongo.db.clubs.find_one(sort=[("win_percentage", -1)])["win_percentage"]
    min_win_percentage = mongo.db.clubs.find_one(sort=[("win_percentage", 1)])["win_percentage"]
    max_club_players_value = mongo.db.clubs.find_one(sort=[("club_players_value", -1)])["club_players_value"]
    min_club_players_value = mongo.db.clubs.find_one(sort=[("club_players_value", 1)])["club_players_value"]

    print(f"Max win percentage: {max_win_percentage}")
    print(f"Min win percentage: {min_win_percentage}")

    print(f"Max club players value: {max_club_players_value}")
    print(f"Min club players value: {min_club_players_value}")




    clubs = mongo.db.clubs.find()

    # Crear una lista para almacenar los clubes con su puntuación calculada
    calculated_scores = []

    for club in clubs:
        normalized_wp = normalize(club["win_percentage"], min_win_percentage, max_win_percentage)
        normalized_pvalue = normalize(club["club_players_value"], min_club_players_value, max_club_players_value)

        # Cálculo de la puntuación total
        total_score = normalized_wp + normalized_pvalue
        calculated_scores.append({"name": club["name"], "total_score": total_score})

    # Ordenar los clubes por su puntuación total de mayor a menor
    sorted_clubs = sorted(calculated_scores, key=lambda x: x["total_score"], reverse=True)

    return sorted_clubs
                                           
def obtener_ultimos_enfrentamientos_y_puntos_entre_clubs(club_id1, club_id2):
    # Obtener los últimos 5 enfrentamientos
    enfrentamientos = list(mongo.db.games.find(
        {"$or": [{"home_club_id": club_id1, "away_club_id": club_id2}, {"home_club_id": club_id2, "away_club_id": club_id1}]},
        sort=[("date", -1)],
        limit=5
    ))

    puntos_club1 = 0
    puntos_club2 = 0

    for enfrentamiento in enfrentamientos:
        if enfrentamiento["home_club_id"] == club_id1:
            if enfrentamiento["home_club_goals"] > enfrentamiento["away_club_goals"]:
                puntos_club1 += 3
            elif enfrentamiento["home_club_goals"] == enfrentamiento["away_club_goals"]:
                puntos_club1 += 1
                puntos_club2 += 1
            else:
                puntos_club2 += 3
        else:
            if enfrentamiento["home_club_goals"] > enfrentamiento["away_club_goals"]:
                puntos_club2 += 3
            elif enfrentamiento["home_club_goals"] == enfrentamiento["away_club_goals"]:
                puntos_club1 += 1
                puntos_club2 += 1
            else:
                puntos_club1 += 3

    return puntos_club1, puntos_club2

def obtener_ultimos_partidos_y_puntos(club_id):
    # Obtener los últimos 5 partidos
    partidos = list(mongo.db.games.find(
        {"$or": [{"home_club_id": club_id}, {"away_club_id": club_id}]},
        sort=[("date", -1)],
        limit=5
    ))

    puntos = 0

    # Calcular los puntos para el club
    for partido in partidos:
        if partido["home_club_id"] == club_id:
            if partido["home_club_goals"] > partido["away_club_goals"]:
                puntos += 3
            elif partido["home_club_goals"] == partido["away_club_goals"]:
                puntos += 1
        else:
            if partido["away_club_goals"] > partido["home_club_goals"]:
                puntos += 3
            elif partido["away_club_goals"] == partido["home_club_goals"]:
                puntos += 1

    return puntos


def calcular_distancia_entre_clubes(club_id1, club_id2):
    # Obtener los datos de los clubes
    club1 = mongo.db.normalized_data.find_one({"club_id": club_id1})
    club2 = mongo.db.normalized_data.find_one({"club_id": club_id2})

    if club1 is None:
        return "No se ha encontrado el club con el ID proporcionado.", None
    if club2 is None:
        return None, "No se ha encontrado el club con el ID proporcionado."
    
    # Calcular la distancia entre los clubes
    normalized_pvalue1 = club1["club_players_value"]
    normalized_pvalue2 = club2["club_players_value"]
    ratio_goals_per_game_team1 = club1["ratio_goals"]
    ratio_goals_per_game_team2 = club2["ratio_goals"]
    ratio_goals_oponent_team1 = club1["ratio_opponent_goals"]
    ratio_goals_oponent_team2 = club2["ratio_opponent_goals"]
    global_points1 = club1["points"]
    global_points2 = club2["points"]
    points1, points2 = obtener_ultimos_enfrentamientos_y_puntos_entre_clubs(club_id1, club_id2)
    points1 = normalize(points1, 0, 15)
    points2 = normalize(points2, 0, 15)
    normalized_wp1 = 0.8*normalized_pvalue1 + 0.92*ratio_goals_per_game_team1- 0.82*ratio_goals_oponent_team1 + 0.49*global_points1 + 0.5*points1
    normalized_wp2 = 0.8*normalized_pvalue2 + 0.92*ratio_goals_per_game_team2 - 0.82*ratio_goals_oponent_team2 + 0.49*global_points2 + 0.5*points2

    normalized_wp1 = normalized_wp1 * 1.1
    
    return normalized_wp1, normalized_wp2

def insert_normalized_df():
    df = create_table()
    dataframes_dict = {"normalized_data": df}
    for collection_name, df in dataframes_dict.items():
        collection = mongo.db[collection_name]
        records = df.to_dict(orient='records')
        collection.insert_many(records)
    return jsonify({'response': "Se ha añadido con éxito."}), 200

def create_table():
    clubs = list(mongo.db.clubs.find())
    data = []
    for club in clubs:
        club_id = club['club_id']
        win_rate = club["win_percentage"]
        club_players_value = club["club_players_value"]
        num_games = mongo.db.club_games.count_documents({"club_id": club_id})
        total_goals = sum(game['own_goals'] for game in mongo.db.club_games.find({"club_id": club_id}))
        total_opponent_goals = sum(game['opponent_goals'] for game in mongo.db.club_games.find({"club_id": club_id}))
        ratio_goals = total_goals / num_games if num_games > 0 else 0
        ratio_opponent_goals = total_opponent_goals / num_games if num_games > 0 else 0
        points = obtener_ultimos_partidos_y_puntos(club_id)

        data.append({
            "club_id": club_id,
            "win_rate": win_rate,
            "club_players_value": club_players_value,
            "num_games": num_games,
            "total_goals": total_goals,
            "total_opponent_goals": total_opponent_goals,
            "ratio_goals": ratio_goals,
            "ratio_opponent_goals": ratio_opponent_goals,
            "points": points
        })

    # Crear un DataFrame con los datos
    df = pd.DataFrame(data)
    scaler = MinMaxScaler()
    columns_to_scale = ["win_rate", "club_players_value", "num_games", "total_goals", "total_opponent_goals", "ratio_goals", "ratio_opponent_goals", "points"]
    df[columns_to_scale] = scaler.fit_transform(df[columns_to_scale])
    return df

def compare_teams(club_id1, club_id2):
    # Calcular la distancia entre los clubes
    team1, team2 = calcular_distancia_entre_clubes(club_id1, club_id2)

    if isinstance(team1, str):
        return team1
    if isinstance(team2, str):
        return team2

    # Obtener los nombres de los clubes
    nombre_club1 = mongo.db.clubs.find_one({"club_id": club_id1})["name"]
    nombre_club2 = mongo.db.clubs.find_one({"club_id": club_id2})["name"]
    if team1 > team2:
        return f"El equipo {nombre_club1} es mejor que el equipo {nombre_club2}, por tanto apostaría por una victoria de {nombre_club1}."
    elif team1 < team2:
        return f"El equipo {nombre_club2} es mejor que el equipo {nombre_club1}, por tanto apostaría por una victoria de {nombre_club2}."
    else:
        return f"Ambos equipos ({nombre_club1} y {nombre_club2}) están igualados, para el próximo partido, yo apostaría por un empate."