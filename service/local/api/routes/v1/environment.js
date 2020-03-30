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
    //throw new Error({ error: 'Cannot connected with DB', code: error.code, message: 'error.sqlMessage' })
    throw new Error('Cannot connect with DB');
  }

  console.log('connected with DB');
});


router.get('/temperature', function(req, res) {
    var query = 'select timestamp, temperature from environment where device_id="1" order by timestamp desc limit 10;';

    con_db.query(query, (err, rows, fields) => {
        if (err) {
            console.log('err: ', err);
        }

        array = []

        for (i in rows) {
            var timestamp = rows[i].timestamp;
            var row = {timestamp: timestamp, value: rows[i].temperature};
            array.push(row);
        }

        var data = {"temperature": array};
        res.header('content-type', 'application/json; charset=utf-8');
        res.send(JSON.stringify(data, null, 1));
    });

});



router.get('/humidity', function(req, res) {
    var query = 'select timestamp, humidity from environment where device_id="1" order by timestamp desc limit 10;';

    con_db.query(query, (err, rows, fields) => {
        if (err) {
            console.log('err: ', err);
        }

        array = []

        for (i in rows) {
            var timestamp = rows[i].timestamp;
            var row = {timestamp: timestamp, value: rows[i].humidity};
            array.push(row);
        }

        var data = {"humidity": array};
        res.header('content-type', 'application/json; charset=utf-8');
        res.send(JSON.stringify(data, null, 1));
    });

});


router.get('/pressure', function(req, res) {
    var query = 'select timestamp, pressure from environment where device_id="1" order by timestamp desc limit 10;';

    con_db.query(query, (err, rows, fields) => {
        if (err) {
            console.log('err: ', err);
        }

        array = []

        for (i in rows) {
            var timestamp = rows[i].timestamp;
            var row = {timestamp: timestamp, value: rows[i].pressure};
            array.push(row);
        }

        var data = {"pressure": array};
        res.header('content-type', 'application/json; charset=utf-8');
        res.send(JSON.stringify(data, null, 1));
    });

});


router.get('/light', function(req, res) {
    var query = 'select timestamp, light from environment where device_id="1" order by timestamp desc limit 10;';

    con_db.query(query, (err, rows, fields) => {
        if (err) {
            console.log('err: ', err);
        }

        array = []

        for (i in rows) {
            var timestamp = rows[i].timestamp;
            var row = {timestamp: timestamp, value: rows[i].light};
            array.push(row);
        }

        var data = {"light": array};
        res.header('content-type', 'application/json; charset=utf-8');
        res.send(JSON.stringify(data, null, 1));
    });

});


router.get('/co2', function(req, res) {
    var query = 'select timestamp, co2 from environment where device_id="1" order by timestamp desc limit 10;';

    con_db.query(query, (err, rows, fields) => {
        if (err) {
            console.log('err: ', err);
        }

        array = []

        for (i in rows) {
            var timestamp = rows[i].timestamp;
            var row = {timestamp: timestamp, value: rows[i].co2};
            array.push(row);
        }

        var data = {"co2": array};
        res.header('content-type', 'application/json; charset=utf-8');
        res.send(JSON.stringify(data, null, 1));
    });

});


router.get('/water_level', function(req, res) {
    var query = 'select timestamp, water_level from environment where device_id="1" order by timestamp desc limit 10;';

    con_db.query(query, (err, rows, fields) => {
        if (err) {
            console.log('err: ', err);
        }

        array = []

        for (i in rows) {
            var timestamp = rows[i].timestamp;
            var row = {timestamp: timestamp, value: rows[i].water_level};
            array.push(row);
        }

        var data = {"water_level": array};
        res.header('content-type', 'application/json; charset=utf-8');
        res.send(JSON.stringify(data, null, 1));
    });

});

       
module.exports = router;
