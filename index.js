/**
 * Node module that exports the Express HTTP router for the application. Handles
 * all server-side HTTP page requests and includes a REST layer for client-side AJAX requests.
 */

'use strict';

/* HTTP Routing */
const express = require('express');
const router = express.Router();
const dotenv = require('dotenv'); dotenv.config();

/* query all products */
router.get('/api/v1.0/moonlets', (request, response) => {

});

/* query a specific product */
router.get('/api/v1.0/moonlets/:moonlet_id', (request, response) => {
  const moonlet_id = request.params.moonlet_id;

});

/* add a new moonlet */
router.post('/api/v1.0/moonlets/:moonlet_id', (request, response) => {
  const moonlet_id = request.params.moonlet_id;
});

/* update a moonlet */
router.put('/api/v1.0/moonlets/:moonlet_id', (request, response) => {
  const moonlet_id = request.params.moonlet_id;
});

/* remove a moonlet */
router.delete('/api/v1.0/moonlets/:moonlet_id', (request, response) => {
  const moonlet_id = request.params.moonlet_id;
});

/* query all products on sale */
router.get('/api/v1.0/moonlets/sale', (request, response) => {

});

/* query all products with limited quantity */
router.get('/api/v1.0/moonlets/limited', (request, response) => {

});

module.exports = router;
