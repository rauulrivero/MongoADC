from src.database.Database import mongo


def get_win_percentage_by_club_id():
    pipeline = [
        {"$group": {"_id": "$club_id", 
                    "total_wins": {"$sum": "$is_win"},
                    "total_games": {"$sum": 1}}},
        {"$project": {"_id": 1,
                      "total_wins": 1,
                      "total_games": 1,
                      "win_percentage": {"$multiply": [{"$divide": ["$total_wins", "$total_games"]}, 100]}}}
    ]
    result = mongo.db.club_games.aggregate(pipeline)
    return list(result)