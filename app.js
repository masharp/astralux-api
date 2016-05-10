/**
 * Node Express Application that inludes our server-side middleware, route indexing,
 * and server-side error logging.
 */

'use strict';

/* Module Dependencies */
const express = require('express');
const logger = require('morgan');
const bodyParser = require('body-parser');
const compression = require('compression');
const dotenv = require('dotenv'); dotenv.config();
const debug = require('debug'); debug('astralux:server');

/* Route Controller */
const index = require('./index');

/* time in miliseconds const oneDay = 86400000; */
const oneMinute = 60000;
const oneHour = 3600000;

/* Express Application */
const app = express();
app.use(compression());

/* View Engine setup */
app.use(logger('dev'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));

/* HTTP page routing */
app.use('/api/v1.0/moonlets/', index);

/* Handle 400 errors with custom error page */
app.use((request, response) => {
  response.status(400);
  response.json({ message: 'Not Found', error: { status: 404 }});
});

/* Handle 500 errors with custom error page */
app.use((error, request, response) => {
  response.status(500);
  response.json({ message: 'Bad Request', error: { status: 500 }});
});

module.exports = app;
