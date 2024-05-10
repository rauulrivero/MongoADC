from src.database.Database import mongo
from src.services.mongo_service import MongoServices
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
    

def clusterizar_defensas(data):

    # Seleccionar características relevantes para la clusterización
    caracteristicas = ['player_value', 'player_yellow_cards_per_minute', 'ratio_goals_per_game', 'ratio_assists_per_game']

    # Preparar los datos para la clusterización
    X = [[player[car] for car in caracteristicas] for player in data]

    # Normalizar los datos
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Definir el número de clusters
    num_clusters = 50

    # Aplicar el algoritmo de k-means
    kmeans = KMeans(n_clusters=num_clusters, random_state=0)
    kmeans.fit(X_scaled)

    # Obtener las etiquetas de cluster asignadas a cada jugador
    labels = kmeans.labels_

    # Calcular el puntaje de cada cluster basado en alguna métrica (por ejemplo, la media de las características)
    cluster_scores = {}
    for i in range(num_clusters):
        cluster_indices = [index for index, label in enumerate(labels) if label == i]
        cluster_data = [X_scaled[index] for index in cluster_indices]
        cluster_mean = sum(cluster_data) / len(cluster_data)
        cluster_scores[i] = sum(cluster_mean)  # Puntaje = suma de las medias de las características

    # Ordenar los clusters por puntaje
    sorted_clusters = sorted(cluster_scores.items(), key=lambda x: x[1], reverse=True)

    # Asignar un ranking a los clusters (el mejor cluster será el número más alto)
    cluster_ranking = {cluster[0]: rank for rank, cluster in enumerate(sorted_clusters)}

    # Asignar el ranking a cada jugador
    for player in data:
        player_cluster = kmeans.predict(scaler.transform([[player[car] for car in caracteristicas]]))[0]
        player['cluster_rank'] = cluster_ranking[player_cluster]

    # Ordenar los jugadores por ranking de cluster
    data_sorted = sorted(data, key=lambda x: x['cluster_rank'])

    # Imprimir los jugadores ordenados por ranking de cluster
    return pd.DataFrame(data_sorted)


def clusterizar_porteros(data):

    # Seleccionar características relevantes para la clusterización
    caracteristicas = ['player_value', 'player_minutes']

    # Preparar los datos para la clusterización
    X = [[player[car] for car in caracteristicas] for player in data]

    # Normalizar los datos
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Definir el número de clusters
    num_clusters = 50

    # Aplicar el algoritmo de k-means
    kmeans = KMeans(n_clusters=num_clusters, random_state=0)
    kmeans.fit(X_scaled)

    # Obtener las etiquetas de cluster asignadas a cada jugador
    labels = kmeans.labels_

    # Calcular el puntaje de cada cluster basado en alguna métrica (por ejemplo, la media de las características)
    cluster_scores = {}
    for i in range(num_clusters):
        cluster_indices = [index for index, label in enumerate(labels) if label == i]
        cluster_data = [X_scaled[index] for index in cluster_indices]
        cluster_mean = sum(cluster_data) / len(cluster_data)
        cluster_scores[i] = sum(cluster_mean)  # Puntaje = suma de las medias de las características

    # Ordenar los clusters por puntaje
    sorted_clusters = sorted(cluster_scores.items(), key=lambda x: x[1], reverse=True)

    # Asignar un ranking a los clusters (el mejor cluster será el número más alto)
    cluster_ranking = {cluster[0]: rank for rank, cluster in enumerate(sorted_clusters)}

    # Asignar el ranking a cada jugador
    for player in data:
        player_cluster = kmeans.predict(scaler.transform([[player[car] for car in caracteristicas]]))[0]
        player['cluster_rank'] = cluster_ranking[player_cluster]

    # Ordenar los jugadores por ranking de cluster
    data_sorted = sorted(data, key=lambda x: x['cluster_rank'])

    # Imprimir los jugadores ordenados por ranking de cluster
    return pd.DataFrame(data_sorted)

def clusterizar_delanteros_centrocampistas(data):

    # Seleccionar características relevantes para la clusterización
    caracteristicas = ['player_value', 'ratio_goals_per_game', 'ratio_assists_per_game']

     # Preparar los datos para la clusterización
    X = [[player[car] for car in caracteristicas] for player in data]

    # Normalizar los datos
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Definir el número de clusters
    num_clusters = 50

    # Aplicar el algoritmo de k-means
    kmeans = KMeans(n_clusters=num_clusters, random_state=0)
    kmeans.fit(X_scaled)

    # Obtener las etiquetas de cluster asignadas a cada jugador
    labels = kmeans.labels_

    # Calcular el puntaje de cada cluster basado en alguna métrica (por ejemplo, la media de las características)
    cluster_scores = {}
    for i in range(num_clusters):
        cluster_indices = [index for index, label in enumerate(labels) if label == i]
        cluster_data = [X_scaled[index] for index in cluster_indices]
        cluster_mean = sum(cluster_data) / len(cluster_data)
        cluster_scores[i] = sum(cluster_mean)  # Puntaje = suma de las medias de las características

    # Ordenar los clusters por puntaje
    sorted_clusters = sorted(cluster_scores.items(), key=lambda x: x[1], reverse=True)

    # Asignar un ranking a los clusters (el mejor cluster será el número más alto)
    cluster_ranking = {cluster[0]: rank for rank, cluster in enumerate(sorted_clusters)}

    # Asignar el ranking a cada jugador
    for player in data:
        player_cluster = kmeans.predict(scaler.transform([[player[car] for car in caracteristicas]]))[0]
        player['cluster_rank'] = cluster_ranking[player_cluster]

    # Ordenar los jugadores por ranking de cluster
    data_sorted = sorted(data, key=lambda x: x['cluster_rank'])

    # Imprimir los jugadores ordenados por ranking de cluster
    return pd.DataFrame(data_sorted)


def insert_cluster():
    centrocampista_data, delantero_data, defensa_data, portero_data = MongoServices.get_players_by_position()  
    cluster_porteros = clusterizar_porteros(portero_data)
    cluster_defensas = clusterizar_defensas(defensa_data)
    cluster_delanteros = clusterizar_delanteros_centrocampistas(delantero_data)
    cluster_centrocampistas = clusterizar_delanteros_centrocampistas(centrocampista_data)
    data = pd.concat([cluster_porteros, cluster_defensas, cluster_delanteros, cluster_centrocampistas])

    dataframes_dict = {"players_cluster": data}
    for collection_name, df in dataframes_dict.items():
        collection = mongo.db[collection_name]
        records = df.to_dict(orient='records')
        collection.insert_many(records)

    return {'response': "Se ha añadido con éxito."}

#tiene que buscar en loa colección de players_cluster el player_id y devolver el cluster_rank
def get_player_rank(player_id):
    print(player_id)
    player = mongo.db.players_cluster.find_one({"player_id": int(player_id)})
    if player is None:
        return "No se ha encontrado el jugador con el ID proporcionado."
    else:
        return player['cluster_rank']