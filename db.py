from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, validates

class DataAccessLayer:
    def __init__(self, app):
        if app.config['TESTING']:
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_database.db'
        else:
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

        self.db = SQLAlchemy(app)
        self.engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)
        self.engine.execute('CREATE TABLE IF NOT EXISTS readings (device_uuid TEXT, type TEXT, value INTEGER, date_created INTEGER)')
        self.Session = sessionmaker(bind = self.engine)
