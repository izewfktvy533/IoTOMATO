#!/usr/bin/env node

const express = require('express');
const router = express.Router();

router.use('/environment', require('./environment.js'));
//router.use('/soil',        require('./soil.js'));

module.exports = router;

