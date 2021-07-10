from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()


def setup_db(app):
    '''
    setup_db(app)

    binds a flask application and a SQLAlchemy service
    '''

    db.app = app
    db.init_app(app)

    # do not use migrations in test environment
    if app.config['TESTING'] is True:
        db.create_all()
    else:
        Migrate(app, db)
