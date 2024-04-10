from flask import request, jsonify, Blueprint, current_app
from src.services.ApiQueryService import ApiQueryService

api = Blueprint('api', __name__)
apiQueryService = ApiQueryService("3")

@api.route('/', methods=['GET'])
def index():
    return jsonify({'response': 'Welcome to my API!'}), 200

@api.route('/show_formed_year/<team>', methods=['GET'])
def show_team(team):

    response = apiQueryService.make_request("/searchteams.php", t=team)

    response = response["teams"][0]["intFormedYear"]

    return jsonify({'response': f" El año de formación del {team} es {response}"}), 200

