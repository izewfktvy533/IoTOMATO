#!/usr/bin/env node

const express      = require('express');
const path         = require('path');
const favicon      = require('serve-favicon');
const logger       = require('morgan')
const cookieParser = require('cookie-parser');
const bodyParser   = require('body-parser');
const cors         = require('cors');
const router       = require('./routes/v1/');
const app = express();
const port = 8000;

app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');

app.use(cors());
app.use(logger('dev'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));
app.use('/iotomato/api/v1/', router);

app.listen(port)

