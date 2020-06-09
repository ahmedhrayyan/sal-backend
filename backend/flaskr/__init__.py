from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from database import setup_db


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    if test_config is None:
        # load config file if it exists
        app.config.from_pyfile('config.py', silent=True)
    setup_db(app)

    @app.route('/')
    def index():
        return jsonify({'message': 'Hello World!'})

    return app
