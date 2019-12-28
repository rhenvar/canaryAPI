from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class DataAccessLayer:
    def __init__(self, app):
        self.db = SQLAlchemy(app)
        self.engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)
        self.engine.execute('CREATE TABLE IF NOT EXISTS readings (device_uuid TEXT, type TEXT, value INTEGER, date_created INTEGER)')
        self.Session = sessionmaker(bind = self.engine)
