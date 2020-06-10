from flask import Flask, jsonify, request, abort
from flask_cors import CORS, cross_origin
from database import setup_db, Answer, Question


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    if test_config is None:
        # load config file if it exists
        app.config.from_pyfile('config.py', silent=True)
    setup_db(app)

    # handling errors
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'not found',
            'error': 404
        }), 404

    return app
