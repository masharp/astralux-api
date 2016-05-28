## Python Module that exports the custom 'make_error_resonse' for request/server errors

from flask import make_response, jsonify

### Basic Error Message Generator ###
def make_error_response(message = 'Internal Error!', code = 500):
    return make_response(jsonify({ 'error': message }), code)
