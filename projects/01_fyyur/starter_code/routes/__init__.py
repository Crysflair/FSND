import datetime
from flask import Blueprint, render_template

rt = Blueprint('rt', __name__)

@rt.route('/', methods=['GET', 'DELETE'])
def index():
    return render_template('pages/home.html')

# Helper

def divide_shows(shows):
    past = [s for s in shows if s.start_time < datetime.now()]
    upcoming = [s for s in shows if s.start_time >= datetime.now()]
    return past, upcoming


def num_upcoming_shows(shows):
    return len(divide_shows(shows)[1])