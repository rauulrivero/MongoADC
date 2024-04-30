from src.database.Database import mongo

def agrupar_equipos_por_liga():
    
    pipeline = [
    {"$group": {"_id": "$domestic_competition_id", "equipos": {"$push": {"club_id": "$club_id", "name": "$name"}}}}
    ]


    result = mongo.db.clubs.aggregate(pipeline)
   
    equipos_por_liga = {}
    for item in result:
        liga = item["_id"]
        equipos = item["equipos"]
        equipos_por_liga[liga] = equipos

    return equipos_por_liga


def get_competitions():
    competition_codes = ["ES1", "IT1", "L1", "FR1", "GB1"]
    competitions = mongo.db.competitions.find({"competition_id": {"$in": competition_codes}}, {"_id": 0, "name": 1, "competition_id": 1})
    return list(competitions)

def get_teams_by_competition_id_service(competition_id):
    teams = mongo.db.clubs.find({"domestic_competition_id": competition_id}, {"_id": 0, "club_id": 1, "name": 1})
    return list(teams)