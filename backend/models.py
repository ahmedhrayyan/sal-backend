import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Text
from flask_migrate import Migrate

db = SQLAlchemy()


def setup_db(app, database_uri=None, test_env=False):
    '''
    setup_db(app)
        binds a flask application and a SQLAlchemy service
    '''
    # I have put database uri in the config file for privacy reasons
    if database_uri:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_uri

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)

    # do not use migrations in test environment
    if test_env is True:
        db.create_all()
    else:
        migrate = Migrate(app, db)
