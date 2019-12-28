import json
import pytest
import sqlite3
import time
import unittest
import pdb

from app import app

class SensorRoutesTestCases(unittest.TestCase):

    def setUp(self):
        # Setup the SQLite DB
        conn = sqlite3.connect('test_database.db')
        conn.execute('DROP TABLE IF EXISTS readings')
        conn.execute('CREATE TABLE IF NOT EXISTS readings (device_uuid TEXT, type TEXT, value INTEGER, date_created INTEGER)')
        
        self.device_uuid = 'test_device'

        # Setup some sensor data
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (self.device_uuid, 'temperature', 22, int(time.time()) - 100))
        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (self.device_uuid, 'temperature', 22, int(time.time()) - 60))
        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (self.device_uuid, 'temperature', 50, int(time.time()) - 50))
        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (self.device_uuid, 'temperature', 100, int(time.time())))

        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    ('other_uuid', 'temperature', 22, int(time.time())))

        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (self.device_uuid, 'humidity', 22, int(time.time()) - 100))
        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (self.device_uuid, 'humidity', 50, int(time.time()) - 50))
        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (self.device_uuid, 'humidity', 100, int(time.time())))

        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    ('other_uuid', 'temperature', 22, int(time.time())))
        conn.commit()

        self.client = app.test_client

    def test_device_readings_get(self):
        # Given a device UUID
        # When we make a request with the given UUID
        request = self.client().get('/devices/{}/readings/'.format(self.device_uuid))

        # Then we should receive a 200
        self.assertEqual(request.status_code, 200)

        # And the response data should have six sensor readings
        self.assertTrue(len(json.loads(request.data)) == 7)

    def test_device_readings_post(self):
        # Given a device UUID
        # When we make a request with the given UUID to create a reading
        request = self.client().post('/devices/{}/readings/'.format(self.device_uuid), data=
            json.dumps({
                'type': 'temperature',
                'value': 100 
            }))

        # Then we should receive a 201
        self.assertEqual(request.status_code, 201)

        # And when we check for readings in the db
        conn = sqlite3.connect('test_database.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('select * from readings where device_uuid="{}"'.format(self.device_uuid))
        rows = cur.fetchall()

        # We should have all eight 
        self.assertTrue(len(rows) == 8)

    def test_device_readings_get_temperature(self):
        response = self.client().get('/devices/{}/readings/'.format(self.device_uuid), data=
            json.dumps({
                'type': 'temperature'
            }))

        # Then we should receive a 200
        self.assertEqual(response.status_code, 200)
        readings = json.loads(response.data)

        self.assertTrue(len(readings) == 4)

        temperature = True
        for reading in readings:
            if "temperature" != reading.get('type'):
                temperature = False
                break

        self.assertEqual(temperature, True)

    def test_device_readings_get_humidity(self):
        response = self.client().get('/devices/{}/readings/'.format(self.device_uuid), data=
            json.dumps({
                'type': 'humidity'
            }))

        # Then we should receive a 200
        self.assertEqual(response.status_code, 200)
        readings = json.loads(response.data)

        self.assertTrue(len(readings) == 3)

        humidity = True
        for reading in readings:
            if 'humidity' != reading.get('type'):
                humidity = False
                break

        self.assertEqual(humidity, True)

    def test_device_readings_get_past_dates(self):
        start = int(time.time()) - 50 
        end = int(time.time()) 
        response = self.client().get('/devices/{}/readings/'.format(self.device_uuid), data=
            json.dumps({
                'start': start,
                'end': end
            }))

        self.assertEqual(response.status_code, 200)
        readings = json.loads(response.data)
        self.assertEqual(len(readings), 4)

        in_range = True
        for reading in readings:
            date = reading.get('date_created')
            if date < start or date > end:
                in_range = False

        self.assertEqual(in_range, True)

    def test_device_readings_min(self):
        response = self.client().get('/devices/{}/readings/min/'.format(self.device_uuid), data=
            json.dumps({
                'type': 'temperature'
            }))

        self.assertEqual(response.status_code, 200)

        reading = json.loads(response.data)

        self.assertEqual(len(reading), 1)

        self.assertEqual(reading.get('value'), 22)


    def test_device_readings_max(self):
        response = self.client().get('/devices/{}/readings/max/'.format(self.device_uuid), data=
            json.dumps({
                'type': 'temperature'
            }))

        self.assertEqual(response.status_code, 200)

        reading = json.loads(response.data)

        self.assertEqual(len(reading), 1)

        self.assertEqual(reading.get('value'), 100)

    def test_device_readings_median(self):
        response = self.client().get('/devices/{}/readings/median/'.format(self.device_uuid), data=
            json.dumps({
                'type': 'temperature'
            }))

        self.assertEqual(response.status_code, 200)

        reading = json.loads(response.data)

        self.assertEqual(len(reading), 1)

        self.assertEqual(reading.get('value'), 36)

    def test_device_readings_mean(self):
        response = self.client().get('/devices/{}/readings/mean/'.format(self.device_uuid), data=
            json.dumps({
                'type': 'temperature'
            }))

        self.assertEqual(response.status_code, 200)

        reading = json.loads(response.data)

        self.assertEqual(len(reading), 1)

        self.assertEqual(reading.get('value'), 48.5)

    def test_device_readings_mode(self):
        response = self.client().get('/devices/{}/readings/mode/'.format(self.device_uuid), data=
            json.dumps({
                'type': 'temperature'
            }))

        self.assertEqual(response.status_code, 200)

        reading = json.loads(response.data)

        self.assertEqual(len(reading), 1)

        self.assertEqual(reading.get('value'), 22)

    def test_device_readings_quartiles(self):
        response = self.client().get('/devices/{}/readings/quartiles/'.format(self.device_uuid), data=
            json.dumps({
                'type': 'temperature',
                'start': 1,
                'end': int(time.time())
            }))

        self.assertEqual(response.status_code, 200)

        reading = json.loads(response.data)

        self.assertEqual(len(reading), 2)

        self.assertEqual(reading.get('quartile_1'), 22)
        self.assertEqual(reading.get('quartile_3'), 75)
        
