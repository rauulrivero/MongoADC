from src.database.Database import mongo
import pandas as pd
from flask import jsonify

def init_df_football():
    appearances_df, club_games_df, clubs_df, competitions_df, games_df, players_df = clean_csv_data()
    dataframes_dict = {"appearences": appearances_df, "club_games": club_games_df, 'clubs': clubs_df,'players':players_df, 'games': games_df, 'competitions': competitions_df}

    for collection_name, df in dataframes_dict.items():
        collection = mongo.db[collection_name]
        records = df.to_dict(orient='records')
        collection.insert_many(records)
    return jsonify({'response': "Se ha añadido con éxito."}), 200


def clean_csv_data():

    competition_ids = ['ES1', 'IT1', 'FR1', 'L1', 'GB1', 'CIT', 'SUC', 'USC', 'EL', 'SCI', 'CL', 'CDR', 'FAC', 'GBCS', 'DFL', 'FRCH']

    appearances_df = pd.read_csv('data\\appearances.csv', encoding='utf-8')
    appearances_df =  appearances_df.drop('player_current_club_id', axis = 1)
    appearances_df = appearances_df[appearances_df['competition_id'].isin(competition_ids)]

    club_games_df = pd.read_csv('data\\club_games.csv', encoding='utf-8')
    club_games_df =  club_games_df.drop(['own_position', 'own_manager_name','opponent_position', 'opponent_manager_name'], axis = 1)

    clubs_df = pd.read_csv('data\\clubs.csv', encoding='utf-8')
    clubs_df = clubs_df[['club_id', 'name', 'domestic_competition_id', 'average_age', 'last_season']]
    clubs_df = clubs_df[clubs_df['domestic_competition_id'].isin(competition_ids)]

    clubs_df = add_win_rate(club_games_df, clubs_df)

    competitions_df = pd.read_csv('data\\competitions.csv', encoding='utf-8')
    competitions_df = competitions_df[['competition_id', 'name', 'type', 'country_name', 'domestic_league_code']]
    competitions_df = competitions_df[competitions_df['competition_id'].isin(competition_ids)]


    games_df = pd.read_csv('data\\games.csv', encoding='utf-8')
    games_df = games_df[['game_id', 'competition_id', 'season', 'date', 'home_club_id', 'away_club_id', 'home_club_goals', 'away_club_goals']]
    games_df = games_df[games_df['competition_id'].isin(competition_ids)]

    players_df = pd.read_csv('data\\players.csv', encoding='utf-8')
    
    columns_to_drop = ['first_name', 'last_name', 'player_code', 'city_of_birth', 'country_of_birth', 'agent_name', 'image_url', 'url', 'current_club_domestic_competition_id', 'current_club_name', 'highest_market_value_in_eur']
    players_df.drop(columns_to_drop, axis=1, inplace=True)

    players_df['market_value_in_eur'] = players_df['market_value_in_eur'].fillna(-1)
    players_df['height_in_cm'] = players_df['height_in_cm'].fillna(-1)

    players_df['market_value_in_eur'] = pd.to_numeric(players_df['market_value_in_eur'], errors='coerce', downcast='integer')
    players_df['height_in_cm'] = pd.to_numeric(players_df['height_in_cm'], errors='coerce', downcast='integer')

        
    return appearances_df, club_games_df, clubs_df, competitions_df, games_df, players_df


def add_win_rate(club_games_df, clubs_df):
    win_stats = club_games_df.groupby('club_id').agg(total_wins=('is_win', 'sum'), total_games=('is_win', 'count')).reset_index()

    win_stats['win_percentage'] = (win_stats['total_wins'] / win_stats['total_games']) * 100

    clubs_df = clubs_df.merge(win_stats, on='club_id', how='left')
    
    return clubs_df