# Canary Platform Homework

## Introduction
Imagine a system where hundreds of thousands of Canary like hardware devices are concurrently uploading temperature and humidty sensor data.

The API to facilitate this system accepts creation of sensor records, in addition to retrieval.

These `GET` and `POST` requests can be made at `/devices/<uuid>/readings/`.

Retreival of sensor data should return a list of sensor values such as:

```
    [{
        'date_created': <int>,
        'device_uuid': <uuid>,
        'type': <string>,
        'value': <int>
    }]
```

The API supports optionally querying by sensor type, in addition to a date range.

A client can also access metrics such as the min, max, median, mode and mean over a time range.

These metric requests can be made by a `GET` request to `/devices/<uuid>/readings/<metric>/`

When requesting min, max and median, a single sensor reading dictionary should be returned as seen above.

When requesting the mean or mode, the response should be:

```
    {
        'value': <mean/mode>
    }
```

Finally, the API also supports the retreival of the 1st and 3rd quartile over a specific date range.

This request can be made via a `GET` to `/devices/<uuid>/readings/quartiles/` and should return

```
    {
        'quartile_1': <int>,
        'quartile_3': <int>
    }
```

The API is backed by a SQLite database.

## Getting Started
This service requires Python3. To get started, create a virtual environment using Python3.

Then, install the requirements using `pip install -r requirements.txt`.

Finally, run the API via `python app.py`.

## Testing
Tests can be run via `pytest -v`.

## Tasks
Your task is to fork this repo and complete the following:

- [+] Add field validation. Only *temperature* and *humidity* sensors are allowed with values between *0* and *100*.
- [+] Add logic for query parameters for *type* and *start/end* dates.
- [+] Implement the min endpoint.
- [+] Implement the max endpoint.
- [+] Implement the median endpoint.
- [+] Implement the mean endpoint.
- [+] Implement the mode endpoint.
- [+] Implement the quartile endpoint.
- [+] Add and implement the stubbed out unit tests for your changes.
- [+] Update the README with any design decisions you made and why.

When you're finished, send your git repo link to Michael Klein at michael@canary.is. If you have any questions, please do not hesitate to reach out!

## Introduction
Imagine a system where hundreds of thousands of Canary like hardware devices are concurrently uploading temperature and humidty sensor data.

The API to facilitate this system accepts creation of sensor records, in addition to retrieval.

These `GET` and `POST` requests can be made at `/devices/<uuid>/readings/`.

Retreival of sensor data will return a list of sensor values such as:

```
    [{
        'date_created': <int>,
        'device_uuid': <uuid>,
        'type': <string>,
        'value': <int>
    }]
```

The API supports optionally querying by sensor type, in addition to a date range.

A client can also access metrics such as the min, max, median, mode and mean over a time range.

These metric requests can be made by a `GET` request to `/devices/<uuid>/readings/<metric>/`

When requesting min, max and median, a single sensor reading dictionary should be returned as seen above.

When requesting the mean or mode, the response will be:

```
    {
        'value': <mean/mode>
    }
```

Finally, the API also supports the retreival of the 1st and 3rd quartile over a specific date range.

This request can be made via a `GET` to `/devices/<uuid>/readings/quartiles/` and will return

```
    {
        'quartile_1': <int>,
        'quartile_3': <int>
    }
```

The API is backed by a SQLite database, a python Flask back-end, and SqlAlchemy ORM.

## Getting Started

First, you will need to create a python3 virtual environment and activate it
```
    $ python3 -m venv /venv/path
    $ source /venv/path/bin/activate
```

Next, clone the repository and install all requirements
```
    $ git clone https://github.com/rhenvar/canaryAPI.git && cd canaryAPI
    $ pip install -r requirements.txt
```

## Environment Configuration
The Canary API supports three basic environment configurations, and will behave different depending on your selection. 
By default, production settings will be used with ```database.db``` as the SQLite database instance


## Development Environment
To activate the development environment, source the development environment configuration:
``` $ source configure_development.sh ``` 

## Testing Environment
To activate the testing environment, and run tests against ```test_database.db```, source the testing environment configuration:
``` $ source configure_testing.sh ```

## Running Tests
After activating the testing environment, simply run ```pytest -v```

## Configuration
Various Python Flask settings can be applied and imported based on your needs. The different configurations are found in an 
inheritance heirarchy located in ```configmodule.py``` 
