import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

SQLALCHEMY_TRACK_MODIFICATIONS = False


class DatabaseURI:

    # Just change the names of your database and credentials and all to connect to your local system
    DATABASE_NAME = "fyyur"
    username = 'ferax'
    password = 'abc'
    url = 'localhost:5432'
    global SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_DATABASE_URI = "postgres://{}:{}@{}/{}".format(
        username, password, url, DATABASE_NAME)

