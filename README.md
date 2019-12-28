# Canary Platform API 

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
The Canary API supports three basic environment configurations, and will behave differently depending on your selection. 
By default, production settings will be used with ```database.db``` as the SQLite database instance. Settings for production
can be found in the base Config class of ```configmodule.py```. Selecting Development or Testing will override these settings


## Development Environment
To activate the development environment, source the development environment configuration:

``` $ source configure_development.sh ``` 

This will by default use ```development_database.db``` 

## Testing Environment
To activate the testing environment, and run tests against ```test_database.db```, source the testing environment configuration:

``` $ source configure_testing.sh ```

## Running Tests
After activating the testing environment, simply run ```pytest -v```

## Configuration
Various Python Flask settings can be applied and imported based on your needs. The different configurations are found in an 
inheritance heirarchy located in ```configmodule.py```, with testing and development inheriting from Config. These same settings 
could be stored in .cfg or .env files managed outside the repository by contributors, but for the purposes of the project they 
are all readily available here. 

## Running the application
To start the Canary API, run:
``` $ python app.py ```

## Design Considerations
As a SQL backed API server, these use cases immediately brought SqlAlchemy to mind. By delegating query construction to a wrapper like SqlAlchemy, two immediate and major concerns were addressed: Security and Complexity. Version 1.3.x, used in this application,
is safe from traditional SQL Injection attacks, and its DSL greatly simplifies the querying process. 

Additionally, this abstraction coupled with a custom SensorData Model allows for validations to be performed in one place. 

## Limitations 
A major limitation to this implementation, as is often the case with back-end applications, is the bottleneck created by the database. SQLite
is simply not equipped to handle hundreds of thousands of records per second from many devices. An immediate solution could be to migrate
to MariaDB and index fields of interest, but this introduces storage and performance overhead as incides would be located on the same machine as the data. Additionally, schema changes would need to propagate to every layer starting with the table and ending with the 
client side application. 

## Future Considerations    
An important consideration to keep the Canary API performant would involve separating data ingest from the API. Currently,
both POST and GET are handled in the same Flask application. To keep response times low and reduce complexity, it would be wise to
decouple Canary API into two separate microservices: one for posting data, and one for getting data. This would also enable us to 
put several instances of each service behind two independent load balancers, respectively.

The nature of this data brings other databases to mind. One attractive alternative is TimeScaleDB. An extension of PostGre, it utilizes 'hypertables' to rapidly insert and retrieve time series data - typically from IoT ecosystems not unlike this one. This alternative would
allow us to preserve our ORM and SqlAlchemy back-end while dramatically improving performance. Plus it scales. More information here https://docs.timescale.com/latest/introduction. 

Another consideration would be to harness Kafka, a highly performant messaging broker system. Kafka is capable of ingesting 
throughputs considered unconscionable by many databases. The nature of this data - small in size but frequent in delivery - makes Kafka
an attractive alternative to SQLite. Its intermediary streaming applications can be used to compute several metrics quite easily
depending on available computing power and retention policy (nothing should stay in a Kafka topic forever). More information here https://kafka.apache.org/documentation/streams/. Finally, it can be connected and synchronized with a number of popular databases relatively easily https://docs.confluent.io/current/connect/index.html  

