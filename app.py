from db import DataAccessLayer
from flask import Flask, render_template, request, Response
from flask.json import jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, validates
from sqlalchemy.sql import func, functions
import configmodule
import json
import sqlite3
import time
import pdb

# Setup python flask configuration
app = Flask(__name__, instance_relative_config = True)
app.config.from_object('configmodule.Config')
if environ.get('DEVELOPMENT_SETTINGS'):
    app.config.from_pyfile('DEVELOPMENT_SETTINGS')
if environ.get('TESTING_SETTINGS'):
    app.config.from_pyfile('testing.cfg') 

dal = DataAccessLayer(app=app)

def validate_request(request_body, sensor_type = True, additional_params = []):
    try: 
        body_data = json.loads(request_body)
    except ValueError as ve:
        raise ve 
    except Exception as e:
        raise e 

    # Type expected by default, omit if optional
    if sensor_type:
        try:
            sensor_type = body_data['type']  
            if not type(sensor_type) is str:
                raise ValueError('type must be a string')
            if not sensor_type in ['temperature', 'humidity']:
                raise ValueError('Type must be temperature or humidity')
        except KeyError as ke:
            raise ke 
        except ValueError as ve:
            raise ve

    missing_params = additional_params - body_data.keys()
    if 0 < len(missing_params):
        raise KeyError('Missing key(s): %s' % str(missing_params))
    
    for key in additional_params:
        try:
            val = body_data[key]
            if not type(val) is int:
                raise ValueError('%s must be an int' % key)
        except ValueError as ve: 
            raise ve

# Readings Model
class SensorData(dal.db.Model):
    __tablename__ = "readings"

    device_uuid =  dal.db.Column(dal.db.Text, primary_key = True)
    sensor_type =  dal.db.Column('type', dal.db.Text, primary_key = True)
    value =        dal.db.Column(dal.db.Integer, primary_key = True)
    date_created = dal.db.Column(dal.db.Integer, primary_key = True, default = int(time.time()))

    def __init__(self, data):
        self.device_uuid = data['device_uuid']
        self.sensor_type = data['type']
        self.value = data['value']
        self.date_created = data['date_created']

    @validates('value')
    def validate_value(self, key, value):
        assert value >= 0 and value <= 100 
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

    dal = DataAccessLayer(app=app)
   
    if request.method == 'POST':
        pdb.set_trace()
        try:
            validate_request(request.data, additional_params = ['value'])
        except KeyError as ke:
            return str(ke), 422
        except ValueError as ve:
            return str(ve), 422
        except Exception as e:
            return str(e), 400

        body_data = json.loads(request.data)
        body_data['device_uuid'] = device_uuid

        try:
            reading = SensorData(body_data)
        except AssertionError:
            return 'Invalid value for sensor type, temperature and humidity may have values between 0 and 100', 422

        try:
            dal.db.session.add(reading)
            dal.db.session.commit()
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
        try:
            validate_request(request.data if request.data else '{}', sensor_type = False)
        except KeyError as ke:
            return str(ke), 422
        except ValueError as ve:
            return str(ve), 422
        except Exception as e:
            return str(e), 400
        body_data = json.loads(request.data) if request.data else {}

        query = SensorData.query.filter(SensorData.device_uuid == device_uuid) 
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

    try:
        validate_request(request.data)
    except KeyError as ke:
        return str(ke), 422
    except ValueError as ve:
        return str(ve), 422
    except Exception as e:
        return str(e), 400

    dal = DataAccessLayer(app=app)
    session = dal.Session()
    subquery = session.query(func.min(SensorData.value)).filter(SensorData.device_uuid == device_uuid)
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
        validate_request(request.data)
    except KeyError as ke:
        return str(ke), 422
    except ValueError as ve:
        return str(ve), 422
    except Exception as e:
        return str(e), 400


    session = dal.Session()
    subquery = session.query(func.max(SensorData.value)).filter(SensorData.device_uuid == device_uuid)
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
        validate_request(request.data)
    except KeyError as ke:
        return str(ke), 422
    except ValueError as ve:
        return str(ve), 422
    except Exception as e:
        return str(e), 400

    subquery = SensorData.query.filter(SensorData.device_uuid == device_uuid, SensorData.sensor_type == body_data.get('type'))
    if body_data.get('start', None):
        subquery = subquery.filter(SensorData.date_created >= body_data.get('start'))
    if body_data.get('end', None):
        subquery = subquery.filter(SensorData.date_created <= body_data.get('end'))

    count = subquery.count()
    query = SensorData.query.filter(SensorData.device_uuid == device_uuid).filter(SensorData.sensor_type == body_data.get('type'))
    if body_data.get('start', None):
        query = query.filter(SensorData.date_created >= body_data.get('start'))
    if body_data.get('end', None):
        query = query.filter(SensorData.date_created <= body_data.get('end'))

    # Compute median value for even number of records
    row = None
    if 0 == count % 2:
        query = query.order_by(SensorData.value).limit(2).offset((count - 1) / 2)
        couple = query.all()
        couple[0].value = (couple[0].value + couple[1].value) / 2.0
        row = couple[0]
    # Standard median computation
    else:
        query = query.order_by(SensorData.value).limit(1).offset(count / 2)
        row = query.first()

    return jsonify({'value': row.value}), 200

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

    try:
        validate_request(request.data)
    except KeyError as ke:
        return str(ke), 422
    except ValueError as ve:
        return str(ve), 422
    except Exception as e:
        return str(e), 400

    session = dal.Session()
    query = session.query(func.avg(SensorData.value)).filter(SensorData.device_uuid == device_uuid).filter(SensorData.sensor_type == body_data.get('type'))
    if body_data.get('start', None):
        query = query.filter(SensorData.date_created >= body_data.get('start'))
    if body_data.get('end', None):
        query = query.filter(SensorData.date_created <= body_data.get('end'))

    row = query.first()
    return jsonify({ 'value': row[0] }), 200

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

    try:
        validate_request(request.data)
    except KeyError as ke:
        return str(ke), 422
    except ValueError as ve:
        return str(ve), 422
    except Exception as e:
        return str(e), 400

    session = dal.Session()
    query = session.query(SensorData.value, func.count(SensorData.value).label('total')).filter(SensorData.device_uuid == device_uuid).filter(SensorData.sensor_type == body_data.get('type')).group_by(SensorData.value).order_by(desc('total'))
    if body_data.get('start', None):
        query = query.filter(SensorData.date_created >= body_data.get('start'))
    if body_data.get('end', None):
        query = query.filter(SensorData.date_created <= body_data.get('end'))

    row = query.first()
    return jsonify({ 'value': row[0] }), 200

@app.route('/devices/<string:device_uuid>/readings/quartiles/', methods = ['GET'])
def request_device_readings_quartiles(device_uuid):
    """
    This endpoint allows clients to GET the 1st and 3rd quartile
    sensor reading value for a device.

    Mandatory Query Parameters:
    * type -> The type of sensor value a client is looking for
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    """

    try:
        validate_request(request.data, ['start', 'end'])
    except KeyError as ke:
        return str(ke), 422
    except ValueError as ve:
        return str(ve), 422
    except Exception as e:
        return str(e), 400


    body_data = json.loads(request.data)
    sensor_type = body_data['type']
    start = body_data['start']
    end = body_data['end']

    subquery = SensorData.query.filter(SensorData.device_uuid == device_uuid, SensorData.sensor_type == body_data.get('type'))
    if body_data.get('start', None):
        subquery = subquery.filter(SensorData.date_created >= body_data.get('start'))
    if body_data.get('end', None):
        subquery = subquery.filter(SensorData.date_created <= body_data.get('end'))

    count = subquery.count()
    query = SensorData.query.order_by(SensorData.value).filter(SensorData.device_uuid == device_uuid).filter(SensorData.sensor_type == body_data.get('type'))
    if body_data.get('start', None):
        query = query.filter(SensorData.date_created >= body_data.get('start'))
    if body_data.get('end', None):
        query = query.filter(SensorData.date_created <= body_data.get('end'))

    # Quartile calculation using Turkey's hinges 
    q1_row = None
    q3_row = None
    
    # four equal groups or even groups summing to odd (including median)
    if 0 == count % 4 or 3 == count % 4:
        q1_query = query.limit(2).offset((count - 1) // 4)
        q3_query = query.limit(2).offset((count // 2) + (count - 1) // 4)  

        q1_couple = q1_query.all()
        q1_couple[0].value = (q1_couple[0].value + q1_couple[1].value) / 2.0
        q1_row = q1_couple[0]

        q3_couple = q3_query.all()
        q3_couple[0].value = (q3_couple[0].value + q3_couple[1].value) / 2.0
        q3_row = q3_couple[0]
    # two odd groups
    else:
        q1_query = query.limit(1).offset(count // 4)
        q3_query = query.limit(1).offset((count // 2) + (count // 4))

        q1_row = q1_query.first()
        q3_row = q3_query.first()

    return jsonify({'quartile_1': q1_row.value, 'quartile_3': q3_row.value}), 200


if __name__ == '__main__':
    app.run()
