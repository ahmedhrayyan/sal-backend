import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    EMAIL_PATTERN = "^([\w\.\-]+)@([\w\-]+)((\.(\w){2,3})+)$"
    PHONE_PATTERN = "^\+(?:[0-9]){6,14}[0-9]$"

    UPLOAD_FOLDER = "uploads"
    ALLOWED_EXTENSIONS = {'png', 'jpg'}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024


class ProductionConfig(Config):
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

    MAIL_SERVER = 'smtp.sal22.tech'
    MAIL_PORT = 25
    MAIL_USERNAME = os.environ['MAIL_USERNAME']
    MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
    MAIL_DEFAULT_SENDER = MAIL_USERNAME
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = 'test'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'tests/test.db')

    # Dummy data, emails will not be sent as long as TESTING is True
    MAIL_DEFAULT_SENDER = 'any'
