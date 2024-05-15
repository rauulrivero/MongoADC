from src.database.Database import mongo
from src.services.mongo_service import MongoServices
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
    

def cluster_defenders(data):

    # Select relevant features for clustering
    features = ['player_value', 'player_yellow_cards_per_minute', 'ratio_goals_per_game', 'ratio_assists_per_game']

    # Prepare data for clustering
    X = [[player[feat] for feat in features] for player in data]

    # Normalize data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Define the number of clusters
    num_clusters = 50

    # Apply k-means algorithm
    kmeans = KMeans(n_clusters=num_clusters, random_state=0)
    kmeans.fit(X_scaled)

    # Get cluster labels assigned to each player
    labels = kmeans.labels_

    # Calculate score for each cluster based on some metric (e.g., mean of features)
    cluster_scores = {}
    for i in range(num_clusters):
        cluster_indices = [index for index, label in enumerate(labels) if label == i]
        cluster_data = [X_scaled[index] for index in cluster_indices]
        cluster_mean = sum(cluster_data) / len(cluster_data)
        cluster_scores[i] = sum(cluster_mean)  # Score = sum of feature means

    # Sort clusters by score
    sorted_clusters = sorted(cluster_scores.items(), key=lambda x: x[1], reverse=True)

    # Assign a ranking to clusters (the best cluster will have the highest number)
    cluster_ranking = {cluster[0]: rank for rank, cluster in enumerate(sorted_clusters)}

    # Assign ranking to each player
    for player in data:
        player_cluster = kmeans.predict(scaler.transform([[player[feat] for feat in features]]))[0]
        player['cluster_rank'] = cluster_ranking[player_cluster]

    # Sort players by cluster ranking
    data_sorted = sorted(data, key=lambda x: x['cluster_rank'])

    # Return players sorted by cluster ranking
    return pd.DataFrame(data_sorted)


def cluster_goalkeepers(data):

    # Select relevant features for clustering
    features = ['player_value', 'player_minutes']

    # Prepare data for clustering
    X = [[player[feat] for feat in features] for player in data]

    # Normalize data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Define the number of clusters
    num_clusters = 50

    # Apply k-means algorithm
    kmeans = KMeans(n_clusters=num_clusters, random_state=0)
    kmeans.fit(X_scaled)

    # Get cluster labels assigned to each player
    labels = kmeans.labels_

    # Calculate score for each cluster based on some metric (e.g., mean of features)
    cluster_scores = {}
    for i in range(num_clusters):
        cluster_indices = [index for index, label in enumerate(labels) if label == i]
        cluster_data = [X_scaled[index] for index in cluster_indices]
        cluster_mean = sum(cluster_data) / len(cluster_data)
        cluster_scores[i] = sum(cluster_mean)  # Score = sum of feature means

    # Sort clusters by score
    sorted_clusters = sorted(cluster_scores.items(), key=lambda x: x[1], reverse=True)

    # Assign a ranking to clusters (the best cluster will have the highest number)
    cluster_ranking = {cluster[0]: rank for rank, cluster in enumerate(sorted_clusters)}

    # Assign ranking to each player
    for player in data:
        player_cluster = kmeans.predict(scaler.transform([[player[feat] for feat in features]]))[0]
        player['cluster_rank'] = cluster_ranking[player_cluster]

    # Sort players by cluster ranking
    data_sorted = sorted(data, key=lambda x: x['cluster_rank'])

    # Return players sorted by cluster ranking
    return pd.DataFrame(data_sorted)

def cluster_forwards_midfielders(data):

    # Select relevant features for clustering
    features = ['player_value', 'ratio_goals_per_game', 'ratio_assists_per_game']

    # Prepare data for clustering
    X = [[player[feat] for feat in features] for player in data]

    # Normalize data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Define the number of clusters
    num_clusters = 50

    # Apply k-means algorithm
    kmeans = KMeans(n_clusters=num_clusters, random_state=0)
    kmeans.fit(X_scaled)

    # Get cluster labels assigned to each player
    labels = kmeans.labels_

    # Calculate score for each cluster based on some metric (e.g., mean of features)
    cluster_scores = {}
    for i in range(num_clusters):
        cluster_indices = [index for index, label in enumerate(labels) if label == i]
        cluster_data = [X_scaled[index] for index in cluster_indices]
        cluster_mean = sum(cluster_data) / len(cluster_data)
        cluster_scores[i] = sum(cluster_mean)  # Score = sum of feature means

    # Sort clusters by score
    sorted_clusters = sorted(cluster_scores.items(), key=lambda x: x[1], reverse=True)

    # Assign a ranking to clusters (the best cluster will have the highest number)
    cluster_ranking = {cluster[0]: rank for rank, cluster in enumerate(sorted_clusters)}

    # Assign ranking to each player
    for player in data:
        player_cluster = kmeans.predict(scaler.transform([[player[feat] for feat in features]]))[0]
        player['cluster_rank'] = cluster_ranking[player_cluster]

    # Sort players by cluster ranking
    data_sorted = sorted(data, key=lambda x: x['cluster_rank'])

    # Return players sorted by cluster ranking
    return pd.DataFrame(data_sorted)


def insert_clusters():
    midfielder_data, forward_data, defender_data, goalkeeper_data = MongoServices.get_players_by_position()  
    cluster_goalkeepers = cluster_goalkeepers(goalkeeper_data)
    cluster_defenders = cluster_defenders(defender_data)
    cluster_forwards = cluster_forwards_midfielders(forward_data)
    cluster_midfielders = cluster_forwards_midfielders(midfielder_data)
    data = pd.concat([cluster_goalkeepers, cluster_defenders, cluster_forwards, cluster_midfielders])

    dataframes_dict = {"players_cluster": data}
    for collection_name, df in dataframes_dict.items():
        collection = mongo.db[collection_name]
        records = df.to_dict(orient='records')
        collection.insert_many(records)

    return {'response': "Successfully added."}

# It needs to search in the players_cluster collection for the player_id and return the cluster_rank
def get_player_rank(player_id):
    print(player_id)
    player = mongo.db.players_cluster.find_one({"player_id": int(player_id)})
    if player is None:
        return "Player with the provided ID not found."
    else:
        return player['cluster_rank']

