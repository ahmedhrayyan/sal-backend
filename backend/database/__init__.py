import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()


def setup_db(app, database_uri=None, test_env=False):
    '''
    setup_db(app)
        binds a flask application and a SQLAlchemy service
    '''

    if database_uri:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    else:
        try:
            DATABASE_URL = os.environ['DATABASE_URL']
            app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
        except KeyError:
            raise KeyError('DATABASE_URL expected in environ')

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)

    # do not use migrations in test environment
    if test_env is True:
        db.create_all()
    else:
        Migrate(app, db)
