from src.database.Database import mongo


def calcular_clubes_ordenados():
    # Encontrar valores máximos y mínimos
    max_win_percentage = mongo.db.clubs.find_one(sort=[("win_percentage", -1)])["win_percentage"]
    min_win_percentage = mongo.db.clubs.find_one(sort=[("win_percentage", 1)])["win_percentage"]
    max_club_players_value = mongo.db.clubs.find_one(sort=[("club_players_value", -1)])["club_players_value"]
    min_club_players_value = mongo.db.clubs.find_one(sort=[("club_players_value", 1)])["club_players_value"]

    # Función de normalización
    def normalize(value, min_value, max_value):
        return (value - min_value) / (max_value - min_value)

    # Consulta para obtener los documentos y aplicar la normalización
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