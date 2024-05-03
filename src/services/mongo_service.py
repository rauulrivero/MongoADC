class MongoServices:

    def __init__(self, mongo):
        self.mongo = mongo

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

    def get_competitions(self):
        competition_codes = ["ES1", "IT1", "L1", "FR1", "GB1"]
        competitions = self.mongo.db.competitions.find({"competition_id": {"$in": competition_codes}}, {"_id": 0, "name": 1, "competition_id": 1})
        return list(competitions)

    def get_teams_by_competition_id_service(self, competition_id, season=2023):
        teams = self.mongo.db.clubs.find({"domestic_competition_id": competition_id, "last_season" : season}, {"_id": 0, "club_id": 1, "name": 1})
        return list(teams)

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