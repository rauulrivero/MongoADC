from flask import Blueprint, render_template
from src.services.CrudServices import create_team

api = Blueprint('api', __name__)


@api.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@api.route('/create_team/<team>', methods=['POST'])
def create_team_route(team):
    return create_team(team)

