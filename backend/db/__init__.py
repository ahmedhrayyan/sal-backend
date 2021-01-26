from os import environ
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()


def setup_db(app, test_env=False):
    '''
    setup_db(app)
        binds a flask application and a SQLAlchemy service
    '''

    db.app = app
    db.init_app(app)

    # do not use migrations in test environment
    if test_env is True:
        db.create_all()
    else:
        Migrate(app, db)