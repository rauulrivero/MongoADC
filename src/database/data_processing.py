from src.database.Database import mongo
import pandas as pd
from flask import jsonify

def clean_csv_data():
    appearances_df = pd.read_csv('data\\appearances.csv', encoding='utf-8')
    appearances_df =  appearances_df.drop('player_current_club_id', axis = 1)
    

    club_games_df = pd.read_csv('data\\club_games.csv', encoding='utf-8')
    club_games_df =  club_games_df.drop(['own_position', 'own_manager_name','opponent_position', 'opponent_manager_name'], axis = 1)

    clubs_df = pd.read_csv('data\\clubs.csv', encoding='utf-8')
    clubs_df = clubs_df[['club_id', 'name', 'domestic_competition_id', 'average_age', 'last_season']]

    competitions_df = pd.read_csv('data\\competitions.csv', encoding='utf-8')
    competitions_df = competitions_df[['competition_id', 'name', 'type', 'country_name', 'domestic_league_code']]

    games_df = pd.read_csv('data\\games.csv', encoding='utf-8')
    games_df = games_df[['game_id', 'competition_id', 'season', 'date', 'home_club_id', 'away_club_id', 'home_club_goals', 'away_club_goals']]

    players_df = pd.read_csv('data\\players.csv', encoding='utf-8')
    
    # Dropping columns
    columns_to_drop = ['first_name', 'last_name', 'player_code', 'city_of_birth', 'country_of_birth', 'agent_name', 'image_url', 'url', 'current_club_domestic_competition_id', 'current_club_name', 'highest_market_value_in_eur']
    players_df.drop(columns_to_drop, axis=1, inplace=True)

    # Filling missing values
    players_df['market_value_in_eur'] = players_df['market_value_in_eur'].fillna(-1)
    players_df['height_in_cm'] = players_df['height_in_cm'].fillna(-1)

    # Converting columns to numeric
    players_df['market_value_in_eur'] = pd.to_numeric(players_df['market_value_in_eur'], errors='coerce', downcast='integer')
    players_df['height_in_cm'] = pd.to_numeric(players_df['height_in_cm'], errors='coerce', downcast='integer')

        
    return appearances_df, club_games_df, clubs_df, competitions_df, games_df, players_df


def init_df_football():
    appearances_df, club_games_df, clubs_df, competitions_df, games_df, players_df = clean_csv_data()
    dataframes_dict = {"appearences": appearances_df, "club_games": club_games_df, 'clubs': clubs_df,'players':players_df, 'games': games_df, 'competitions': competitions_df}

    for collection_name, df in dataframes_dict.items():
        collection = mongo.db[collection_name]
        records = df.to_dict(orient='records')
        collection.insert_many(records)
    return jsonify({'response': "Se ha añadido con éxito."}), 200
