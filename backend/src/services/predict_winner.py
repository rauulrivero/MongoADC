from src.database.Database import mongo
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from flask import jsonify




def compare_teams(club_id1, club_id2):
    # Calculate the distance between clubs
    team1, team2 = calculate_distance_between_clubs(club_id1, club_id2)

    if isinstance(team1, str):
        return team1
    if isinstance(team2, str):
        return team2

    # Get club names
    club_name1 = mongo.db.clubs.find_one({"club_id": club_id1})["name"]
    club_name2 = mongo.db.clubs.find_one({"club_id": club_id2})["name"]
    
    # Calculate the difference between normalized distances
    diff = team1 - team2
    
    # Calculate probability of victory for each team
    prob_victory1 = 0.5 + diff * 0.1 
    prob_victory2 = 0.5 - diff * 0.1

    if abs(prob_victory1 - prob_victory2) < 0.1:
        return f"Ambos equipos ({club_name1} y {club_name2}) tienen una probabilidad de victoria muy similar ({prob_victory1*100:.2f}% vs {prob_victory2*100:.2f}%), para el próximo partido, yo apostaría por un empate."
    elif prob_victory1 > prob_victory2:
        return f"El equipo {club_name1} tiene una probabilidad de victoria del {prob_victory1*100+10:.2f}% frente al {club_name2}, por tanto apostaría por una victoria de {club_name1}."
    elif prob_victory1 < prob_victory2:
        return f"El equipo {club_name2} tiene una probabilidad de victoria del {prob_victory2*100+10:.2f}% frente al {club_name1}, por tanto apostaría por una victoria de {club_name2}."
    else:    
        return "Error al calcular la probabilidad de victoria."




# Normalization function
def normalize(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value)
                                           
def get_last_matchups_and_points_between_clubs(club_id1, club_id2):
    # Get the last 5 matchups
    matchups = list(mongo.db.games.find(
        {"$or": [{"home_club_id": club_id1, "away_club_id": club_id2}, {"home_club_id": club_id2, "away_club_id": club_id1}]},
        sort=[("date", -1)],
        limit=5
    ))

    club1_points = 0
    club2_points = 0

    for matchup in matchups:
        if matchup["home_club_id"] == club_id1:
            if matchup["home_club_goals"] > matchup["away_club_goals"]:
                club1_points += 3
            elif matchup["home_club_goals"] == matchup["away_club_goals"]:
                club1_points += 1
                club2_points += 1
            else:
                club2_points += 3
        else:
            if matchup["home_club_goals"] > matchup["away_club_goals"]:
                club2_points += 3
            elif matchup["home_club_goals"] == matchup["away_club_goals"]:
                club1_points += 1
                club2_points += 1
            else:
                club1_points += 3

    return club1_points, club2_points

def get_last_matches_and_points(club_id):
    # Get the last 5 matches
    matches = list(mongo.db.games.find(
        {"$or": [{"home_club_id": club_id}, {"away_club_id": club_id}]},
        sort=[("date", -1)],
        limit=5
    ))

    points = 0

    # Calculate points for the club
    for match in matches:
        if match["home_club_id"] == club_id:
            if match["home_club_goals"] > match["away_club_goals"]:
                points += 3
            elif match["home_club_goals"] == match["away_club_goals"]:
                points += 1
        else:
            if match["away_club_goals"] > match["home_club_goals"]:
                points += 3
            elif match["away_club_goals"] == match["home_club_goals"]:
                points += 1

    return points

def calculate_distance_between_clubs(club_id1, club_id2):
    # Get clubs data
    club1 = mongo.db.normalized_data.find_one({"club_id": club_id1})
    club2 = mongo.db.normalized_data.find_one({"club_id": club_id2})

    if club1 is None:
        return "Club with provided ID not found.", None
    if club2 is None:
        return None, "Club with provided ID not found."
    
    # Calculate distance between clubs
    normalized_player_value1 = club1["club_players_value"]
    normalized_player_value2 = club2["club_players_value"]
    ratio_goals_per_game_team1 = club1["ratio_goals"]
    ratio_goals_per_game_team2 = club2["ratio_goals"]
    ratio_opponent_goals_team1 = club1["ratio_opponent_goals"]
    ratio_opponent_goals_team2 = club2["ratio_opponent_goals"]
    global_points1 = club1["points"]
    global_points2 = club2["points"]
    points1, points2 = get_last_matchups_and_points_between_clubs(club_id1, club_id2)
    points1 = normalize(points1, 0, 15)
    points2 = normalize(points2, 0, 15)
    normalized_wp1 = 0.8 * normalized_player_value1 + 0.92 * ratio_goals_per_game_team1 - 0.82 * ratio_opponent_goals_team1 + 0.49 * global_points1 + 0.5 * points1
    normalized_wp2 = 0.8 * normalized_player_value2 + 0.92 * ratio_goals_per_game_team2 - 0.82 * ratio_opponent_goals_team2 + 0.49 * global_points2 + 0.5 * points2

    normalized_wp1 = normalized_wp1 * 1.1
    
    return normalized_wp1, normalized_wp2

def insert_normalized_df():
    df = create_table()
    dataframes_dict = {"normalized_data": df}
    for collection_name, df in dataframes_dict.items():
        collection = mongo.db[collection_name]
        records = df.to_dict(orient='records')
        collection.insert_many(records)
    return jsonify({'response': "Successfully added."}), 200

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
        points = get_last_matches_and_points(club_id)

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

    # Create a DataFrame with the data
    df = pd.DataFrame(data)
    scaler = MinMaxScaler()
    columns_to_scale = ["win_rate", "club_players_value", "num_games", "total_goals", "total_opponent_goals", "ratio_goals", "ratio_opponent_goals", "points"]
    df[columns_to_scale] = scaler.fit_transform(df[columns_to_scale])
    return df
