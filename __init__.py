# app/__init__.py

from flask import Flask
from flask_restful import Api
from flask_pymongo import PyMongo
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)
api = Api(app)
mongo = PyMongo(app)

from app import routes
