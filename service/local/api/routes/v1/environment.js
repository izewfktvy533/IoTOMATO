#!/usr/bin/env node

const express = require('express');
const mysql   = require('mysql');
const router = express.Router();
const con_db  = mysql.createConnection({
  host: process.env.MYSQL_HOST,
  user: process.env.MYSQL_USER,
  password: process.env.MYSQL_PASSWORD,
  database: 'iotomato',
  timezone: 'jst'
});

con_db.connect(error => {
  if (error) {
    throw new Error('cannot connect with DB');
  }

  console.log('connected with DB');
});

router.get('/temperature', function(req, res) {
  const sensorType = 'temperature';
  console.log({ sensorType });
  responseSensorData(res, sensorType);
});

router.get('/humidity', function(req, res) {
  const sensorType = 'humidity';
  responseSensorData(res, sensorType);
});

router.get('/pressure', function(req, res) {
  const sensorType = 'pressure';
  responseSensorData(res, sensorType);
});

router.get('/light', function(req, res) {
  const sensorType = 'light';
  responseSensorData(res, sensorType);
});

router.get('/co2', function(req, res) {
  const sensorType = 'co2';
  responseSensorData(res, sensorType);
});

router.get('/water_level', function(req, res) {
  const sensorType = 'water_level'
  responseSensorData(res, sensorType);
});

function responseSensorData(res, sensorType) {
  const query = `select timestamp, ${sensorType} from environment where device_id="1" order by timestamp desc limit 10;`
  console.log({ query });
  con_db.query(query, (err, rows, fields) => {
    if (err) {
      throw new Error('query is wrong');
    }

    const array = [];
    rows.forEach(row => {
      array.push({ timestamp: row.timestamp, value: row.temperature });
    });
    console.log('debug: array');
    console.log(array);

    const data = {'temperature': array};
    res.header('content-type', 'application/json; charset=utf-8');
    res.send(JSON.stringify(data, null, 1));
  });
}

module.exports = router;
