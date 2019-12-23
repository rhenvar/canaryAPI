from flask import Flask, render_template, request, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, validates
from flask.json import jsonify
import json
import sqlite3
import time
import pdb

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)
Session = sessionmaker(bind = engine)


# Create Session factory

# Setup the SQLite DB
conn = sqlite3.connect('database.db')
conn.execute('CREATE TABLE IF NOT EXISTS readings (device_uuid TEXT, type TEXT, value INTEGER, date_created INTEGER)')
conn.close()

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
        pdb.set_trace()
        if "temperature" != self.sensor_type and "humidity" != self.sensor_type:
            assert value <= 0 or value >= 100 
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

    Optional Query Parameters:
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    * type -> The type of sensor value a client is looking for
    """

    # Set the db that we want and open the connection
    if app.config['TESTING']:
        conn = sqlite3.connect('test_database.db')
    else:
        conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
   
    if request.method == 'POST':
        # Grab the post parameters

        post_data = json.loads(request.data)
        post_data['device_uuid'] = device_uuid
        # Only Temperature and humidity sensors are allowed with values between 0 and 100
        #sensor_type = post_data.get('type')
        #value = post_data.get('value')
        #date_created = post_data.get('date_created', int(time.time()))

        ## Insert data into db
        #cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
        #            (device_uuid, sensor_type, value, date_created))
        #
        #conn.commit()

        try:
            reading = SensorData(post_data)
        except AssertionError:
            return 'Invalid value for sensor type, only temperature and humidity may have values between 0 and 100', 422

        try:
            db.session.add(reading)
            db.session.commit()
            return 'success', 201
        except e:
            return 'Error saving reading to database %s' % e.msg, 500 

    else:
        # Execute the query
        # cur.execute('select * from readings where device_uuid="{}"'.format(device_uuid))
        # rows = cur.fetchall()

        # Return the JSON
        # return jsonify([dict(zip(['device_uuid', 'type', 'value', 'date_created'], row)) for row in rows]), 200
        
        rows = SensorData.query.filter(device_uuid==device_uuid) 
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
    if app.config['TESTING']:
        conn = sqlite3.connect('test_database.db')
    else:
        conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    get_data = json.loads(request.data)
    sensor_type = get_data.get('type', None)
    if not sensor_type:
        return 'missing type parameter', 422 

    start_date = get_data.get('start', int(time.time()))
    end_date = get_data.get('end', int(time.time()))

    # Insert data into db
    cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                (device_uuid, sensor_type, value, date_created))
    
    conn.commit()

    return 'Endpoint is not implemented', 501

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
