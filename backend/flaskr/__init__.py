from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    if test_config is None:
        app.config.from_pyfile('config', silent=True)

    @app.route('/')
    @cross_origin()
    def index():
        return jsonify({'message': 'Hello World!'})

    return app
