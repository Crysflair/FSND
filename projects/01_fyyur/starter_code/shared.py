from flask_sqlalchemy import SQLAlchemy

db = None
def create_SQLAlchemy(app):
    global db
    db = SQLAlchemy(app)


genre_name, genre_choice = None, None

def init_genre():
    from models import Genre
    global genre_name, genre_choice
    genre_name = {g.id: g.description for g in Genre.query.order_by('id').all()}
    genre_choice = [(i, genre_name[i]) for i in genre_name.keys()]