from flask import Flask
from flask_cors import CORS

from models import setup_db

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    app = Flask(__name__)
    db = setup_db(app)
    db.create_all()

    cors = CORS(app, origins='*')

    @app.after_request
    def after_request(response):
        # These can also be specified in `CORS()`
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    return app
