# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template
from flask_moment import Moment
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
import shared



# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#


app = Flask(__name__)
app.config.from_object('config')
shared.create_SQLAlchemy(app)


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        f = "EEEE MMMM, d, y 'at' h:mm a"
    elif format == 'medium':
        f = "EE MM, dd, y h:mm a"
    else:
        f = 'short'
    return babel.dates.format_datetime(date, format=f, locale='en_US')


app.jinja_env.filters['datetime'] = format_datetime


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')


moment = Moment(app)
mig = Migrate(app, shared.db)
shared.init_genre()

from routes import *
app.register_blueprint(rt)


if __name__ == '__main__':
    app.run()
