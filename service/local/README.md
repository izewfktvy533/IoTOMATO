# Serivce

apt install python3-dev default-libmysqlclient-dev



## DB
CREATE TABLE environment (device_id VARCHAR(3) NOT NULL, timestamp TIMESTAMP NOT NULL, temperature FLOAT, humidity FLOAT UNSIGNED, pressure FLOAT UNSIGNED, light INT UNSIGNED, co2 INT UNSIGNED, water_level INT UNSIGNED);

CREATE TABLE soil (device_id VARCHAR(3) NOT NULL, timestamp TIMESTAMP NOT NULL, vwc FLOAT UNSIGNED, ec FLOAT, temperature FLOAT);
