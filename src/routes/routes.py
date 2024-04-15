from flask import Blueprint, render_template
from src.services.CrudServices import add_event_by_season

api = Blueprint('api', __name__)


@api.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@api.route('/add_event_by_season/<team1>/<team2>/<season>', methods=['POST'])
def add_event_by_season_route(team1, team2, season):
    return add_event_by_season(team1, team2, season)

