class Config(object):
    ENV = 'Production'
    FLASK_DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    ENV = 'Development'
    DEBUG = True

class TestingConfig(Config):
    ENV = 'Testing'
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_database.db'

