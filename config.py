import os
from flask import Flask
from flask_moment import Moment

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True
SECRET_KEY = "fyyur"

# Connect to the database
SQLALCHEMY_TRACK_MODIFICATIONS = False




# TODO IMPLEMENT DATABASE URL
DATABASE_NAME = "fyyurapp"
username = 'postgres'
password = '123456'
url = 'localhost:5432'
SQLALCHEMY_DATABASE_URI = "postgresql://{}:{}@{}/{}".format(username, password, url, DATABASE_NAME)

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


# TODO: connect to a local postgresql database

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
