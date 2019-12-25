from flask import Flask, render_template, request, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, validates
from sqlalchemy.sql import func
from flask.json import jsonify
import json
import sqlite3
import time
import pdb

# Setup python flask
app = Flask(__name__)

# Set the db that we want and open the connection
database = None
if app.config['TESTING']:
    database = 'test_database.db'
    conn = sqlite3.connect('test_database.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_database.db'
else:
    database = 'database.db'
    conn = sqlite3.connect('database.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
conn.row_factory = sqlite3.Row
cur = conn.cursor()
db = SQLAlchemy(app)

# Setup the SQLite DB
conn = sqlite3.connect(database)
conn.execute('CREATE TABLE IF NOT EXISTS readings (device_uuid TEXT, type TEXT, value INTEGER, date_created INTEGER)')
conn.close()

# Setup SqlAlchemy session
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)
Session = sessionmaker(bind = engine)


# Readings Model
class SensorData(db.Model):
    __tablename__ = "readings"

    device_uuid =  db.Column(db.Text, primary_key = True)
    sensor_type =  db.Column('type', db.Text, primary_key = True)
    value =        db.Column(db.Integer, primary_key = True)
    date_created = db.Column(db.Integer, primary_key = True, default = int(time.time()))

    def __init__(self, data):
        self.device_uuid = data['device_uuid']
        self.sensor_type = data['type']
        self.value = data['value']
        self.date_created = data['date_created']

    @validates('value')
    def validate_value(self, key, value):
        assert value > 0 and value < 100 
        return value

    def as_dict(self):
        reading_dict = {}
        for c in self.__table__.columns:
            if 'type' == c.name:
                reading_dict['type'] =  getattr(self, 'sensor_type')
            else:
                reading_dict[c.name] = getattr(self, c.name)
        return reading_dict

@app.route('/devices/<string:device_uuid>/readings/', methods = ['POST', 'GET'])
def request_device_readings(device_uuid):
    """
    This endpoint allows clients to POST or GET data specific sensor types.

    POST Parameters:
    * type -> The type of sensor (temperature or humidity)
    * value -> The integer value of the sensor reading
    * date_created -> The epoch date of the sensor reading.
        If none provided, we set to now.

    """
    try:
        body_data = json.loads(request.data)
    except:
        return 'Bad request', 400
   
    if request.method == 'POST':

        body_data['device_uuid'] = device_uuid

        try:
            reading = SensorData(body_data)
        except AssertionError:
            return 'Invalid value for sensor type, temperature and humidity may have values between 0 and 100', 422

        try:
            db.session.add(reading)
            db.session.commit()
            return 'success', 201
        except e:
            return 'Error saving reading to database %s' % e.msg, 500 

    else:

        """
        Optional Query Parameters:
        * start -> The epoch start time for a sensor being created
        * end -> The epoch end time for a sensor being created
        * type -> The type of sensor value a client is looking for
        """
        query = SensorData.query.filter(device_uuid == device_uuid) 
        if body_data.get('type', None):
            query = query.filter(SensorData.sensor_type == body_data.get('type'))
        if body_data.get('start', None):
            query = query.filter(SensorData.date_created >= body_data.get('start'))
        if body_data.get('end', None):
            query = query.filter(SensorData.date_created <= body_data.get('end'))

        rows = query.all()
        return jsonify([row.as_dict() for row in rows]), 200

# Returns single sensor reading dictionary: { date_created, device_uuid, type, value }
@app.route('/devices/<string:device_uuid>/readings/min/', methods = ['GET'])
def request_device_readings_min(device_uuid):
    """
    This endpoint allows clients to GET the min sensor reading for a device.

    Mandatory Query Parameters:
    * type -> The type of sensor value a client is looking for

    Optional Query Parameters
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    """
    #if app.config['TESTING']:
    #    conn = sqlite3.connect('test_database.db')
    #else:
    #    conn = sqlite3.connect('database.db')
    #conn.row_factory = sqlite3.Row
    #cur = conn.cursor()

    try:
        body_data = json.loads(request.data)
    except:
        return 'Bad request', 400

    if not body_data.get('type', None):
        return 'Missing type parameter', 422

    session = Session()
    subquery = session.query(func.min(SensorData.value)).filter(device_uuid == device_uuid)
    if body_data.get('start', None):
        subquery = subquery.filter(SensorData.date_created >= body_data.get('start'))
    if body_data.get('end', None):
        subquery = subquery.filter(SensorData.date_created <= body_data.get('end'))

    min_val = subquery.first()[0]

    query = SensorData.query.filter(SensorData.device_uuid == device_uuid, SensorData.value == min_val)
    if body_data.get('start', None):
        query = query.filter(SensorData.date_created >= body_data.get('start'))
    if body_data.get('end', None):
        query = query.filter(SensorData.date_created <= body_data.get('end'))
    query = query.order_by(SensorData.date_created.desc())

    row = query.first()
    return jsonify(row.as_dict()), 200

@app.route('/devices/<string:device_uuid>/readings/max/', methods = ['GET'])
def request_device_readings_max(device_uuid):
    """
    This endpoint allows clients to GET the max sensor reading for a device.

    Mandatory Query Parameters:
    * type -> The type of sensor value a client is looking for

    Optional Query Parameters
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    """

    try:
        body_data = json.loads(request.data)
    except:
        return 'Bad request', 400

    if not body_data.get('type', None):
        return 'Missing type parameter', 422

    session = Session()
    subquery = session.query(func.max(SensorData.value)).filter(device_uuid == device_uuid)
    if body_data.get('start', None):
        subquery = subquery.filter(SensorData.date_created >= body_data.get('start'))
    if body_data.get('end', None):
        subquery = subquery.filter(SensorData.date_created <= body_data.get('end'))

    min_val = subquery.first()[0]

    query = SensorData.query.filter(SensorData.device_uuid == device_uuid, SensorData.value == min_val)
    if body_data.get('start', None):
        query = query.filter(SensorData.date_created >= body_data.get('start'))
    if body_data.get('end', None):
        query = query.filter(SensorData.date_created <= body_data.get('end'))
    query = query.order_by(SensorData.date_created.desc())

    row = query.first()
    return jsonify(row.as_dict()), 200
    return 'Endpoint is not implemented', 501

@app.route('/devices/<string:device_uuid>/readings/median/', methods = ['GET'])
def request_device_readings_median(device_uuid):
    """
    This endpoint allows clients to GET the median sensor reading for a device.

    Mandatory Query Parameters:
    * type -> The type of sensor value a client is looking for

    Optional Query Parameters
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    """

    try:
        body_data = json.loads(request.data)
    except:
        return 'Bad request', 400

    if not body_data.get('type', None):
        return 'Missing type parameter', 422

    session = Session()
    subquery = session.query(func.max(SensorData.value)).filter(device_uuid == device_uuid)
    if body_data.get('start', None):
        subquery = subquery.filter(SensorData.date_created >= body_data.get('start'))
    if body_data.get('end', None):
        subquery = subquery.filter(SensorData.date_created <= body_data.get('end'))

    count = subquery.count()

    """
    """
    pdb.set_trace()
    query = SensorData.query.percentile_cont(0.5)
    rows = query.all()

    return 'Endpoint is not implemented', 501

@app.route('/devices/<string:device_uuid>/readings/mean/', methods = ['GET'])
def request_device_readings_mean(device_uuid):
    """
    This endpoint allows clients to GET the mean sensor readings for a device.

    Mandatory Query Parameters:
    * type -> The type of sensor value a client is looking for

    Optional Query Parameters
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    """

    return 'Endpoint is not implemented', 501

@app.route('/devices/<string:device_uuid>/readings/mode/', methods = ['GET'])
def request_device_readings_mode(device_uuid):
    """
    This endpoint allows clients to GET the mode sensor reading value for a device.

    Mandatory Query Parameters:
    * type -> The type of sensor value a client is looking for

    Optional Query Parameters
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    """

    return 'Endpoint is not implemented', 501

#@app.route('/devices/<string:device_uuid>/readings/quartiles/', methods = ['GET'])
#def request_device_readings_mode(device_uuid):
    """
    This endpoint allows clients to GET the 1st and 3rd quartile
    sensor reading value for a device.

    Mandatory Query Parameters:
    * type -> The type of sensor value a client is looking for
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    """

    return 'Endpoint is not implemented', 501


if __name__ == '__main__':
    app.run()
