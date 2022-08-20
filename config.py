import os
from flask import Flask

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
SQLALCHEMY_TRACK_MODIFICATIONS = False




# TODO IMPLEMENT DATABASE URL
DATABASE_NAME = "fyyurapp"
username = 'postgres'
password = '123456'
url = 'localhost:5432'
SQLALCHEMY_DATABASE_URI = "postgresql://{}:{}@{}/{}".format(username, password, url, DATABASE_NAME)

app = Flask(__name__)
