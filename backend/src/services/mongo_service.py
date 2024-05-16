class MongoServices:

    def __init__(self, mongo):
        self.mongo = mongo

    # MANEJO DE USUARIOS

    def create_user(self, name, email, password):
        user = {
            "name": name,
            "email": email,
            "password": password
        }
        self.mongo.db.users.insert_one(user)

    def user_exists(self, email):
        user = self.mongo.db.users.find_one({"email": email})
        return user is not None

    def get_user(self, email):
        user = self.mongo.db.users.find_one({"email": email})
        return user
    def group_teams_by_league(self):
        pipeline = [
            {"$group": {"_id": "$domestic_competition_id", "equipos": {"$push": {"club_id": "$club_id", "name": "$name"}}}}
        ]

        result = self.mongo.db.clubs.aggregate(pipeline)

        equipos_por_liga = {}
        for item in result:
            liga = item["_id"]
            equipos = item["equipos"]
            equipos_por_liga[liga] = equipos

        return equipos_por_liga
    

    # MANEJO DE DATOS

    def get_competitions(self):
        competition_codes = ["ES1", "IT1", "L1", "FR1", "GB1"]
        competitions = self.mongo.db.competitions.find({"competition_id": {"$in": competition_codes}}, {"_id": 0, "name": 1, "competition_id": 1})
        return list(competitions)

    def get_teams_by_competition_id_service(self, competition_id, season=2023):
        teams = self.mongo.db.clubs.find({"domestic_competition_id": competition_id, "last_season" : season}, {"_id": 0, "club_id": 1, "name": 1})
        return list(teams)

    
    def get_seasons(self):
        seasons = self.mongo.db.player_lineup.distinct("season")
        return seasons
    
    def get_teams_by_season(self, competition_id, season):
            # Colección de juegos para encontrar clubes participantes
        coleccion_juegos = self.mongo.db.games

        # Buscar juegos en la liga y temporada especificada
        juegos = coleccion_juegos.find({"season": season, "competition_id": competition_id}, 
                                    {"_id": 0, "home_club_id": 1, "away_club_id": 1})

       
        # Obtener lista única de club_id
        club_ids = set()
        for juego in juegos:
            club_ids.add(juego["home_club_id"])
            club_ids.add(juego["away_club_id"])


        # Colección de clubs para obtener los nombres de los equipos
        coleccion_clubs = self.mongo.db.clubs


        # Buscar nombres de los equipos basándonos en los club_ids obtenidos
        
        clubs = coleccion_clubs.find({"club_id": {"$in": list(club_ids)}}, 
                                        {"_id": 0, "club_id": 1, "name": 1})

        return list(clubs)
    

    def get_players_by_position(self):
        # Crear diccionarios vacíos para cada posición de jugador.
        midfielders = {}
        forwards = {}
        defenders = {}
        goalkeepers = {}

        # Consultar todos los documentos en la colección.
        players_collection = self.mongo.db.players_data
        players_cursor = players_collection.find()

        # Iterar sobre los documentos de la colección y llenar los diccionarios correspondientes.
        for player in players_cursor:
            player['ratio_goals_per_game'] = player['player_goals'] / player['player_games'] if player['player_games'] > 0 else 0
            player['ratio_assists_per_game'] = player['player_assists'] / player['player_games'] if player['player_games'] > 0 else 0
            position = player["player_position"]
            player_id = player["player_id"]

            # Asigna el documento de jugador al diccionario correspondiente según su posición.
            if position == "Midfield":
                midfielders[player_id] = player
            elif position == "Attack":
                forwards[player_id] = player
            elif position == "Defender":
                defenders[player_id] = player
            elif position == "Goalkeeper":
                goalkeepers[player_id] = player

        return list(midfielders.values()), list(forwards.values()), list(defenders.values()), list(goalkeepers.values())
        

    def get_players(self):
        players = self.mongo.db.players_data.find({}, {"_id": 0, "player_name": 1, "player_id": 1})
        return list(players)