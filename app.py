#!flask/bin/python
## http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
## https://realpython.com/blog/python/flask-by-example-part-2-postgres-sqlalchemy-and-alembic/
## curl -u USERNAME:PASSWORD -H "Content-Type: application/json" - POST -d '{"name":"Astralux-FA199"}' http://localhost:5000/api/v1.0/moonlets

## TODO: Add 'discovered' date to moonlet model
## TODO: Finish http method ROUTES

import os

from flask import Flask
from flask import jsonify, make_response, request, abort, url_for
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cors import CORS

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS']) ## load environment settings
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CORS_HEADERS'] = 'Content-Type'
auth = HTTPBasicAuth()
cors = CORS(app, resources = r'/api/*', supports_credentials = True)
db = SQLAlchemy(app)

### Basic HTTP AUTH ###
@auth.get_password
def get_password(username):
    if username == 'master':
        return app.config['MASTER_PASSWORD']
    return None

### Public URIs ###
def make_public_moonlet(moonlet):
    new_moonlet = {}

    for field in moonlet:
        if field == 'id':
            new_moonlet['uri'] = url_for('get_moonlet', moonlet_id = moonlet['id'], _external = True)
        else:
            new_moonlet[field] = moonlet[field]
    return new_moonlet

def make_public_user(user):
    user['uri'] = url_for('get_user', username = user['username'], _external = True)

    return user

### HTTP GET ROUTES ###
@app.route('/api/v1.0/moonlets', methods=['GET'])
@auth.login_required
def get_moonlets():
    from models import Moonlet

    try:
        results = Moonlet.query.all() # query database via sqlalchemy
        results = [ item.serialize() for item in results ] # use class method to serialize each item
        results = [ make_public_moonlet(moonlet) for moonlet in results ] # give a uri for each moonlet instead of an id
        return jsonify({ 'moonlets': results }), 201 # return as json

    except Exception as error:
        print error
        return make_response(jsonify({ 'error': 'Unable to retrieve moonlets from database!' }), 500)

@app.route('/api/v1.0/moonlets/<int:moonlet_id>', methods=['GET'])
@auth.login_required
def get_moonlet(moonlet_id):
    from models import Moonlet

    try:
        result = Moonlet.query.filter_by(id = moonlet_id).first() # query for moonlet

        if result is None:
            return make_response(jsonify({ 'error': 'Moonlet not found!' }), 404) # returns None if unfound
        else:
            result = result.serialize()
            result = make_public_moonlet(result)
            return jsonify({ 'moonlet': result }), 201

    except Exception as error:
        print error
        return make_response(jsonify({ 'error': 'Unable to retrieve that moonlet!' }), 500)

@app.route('/api/v1.0/moonlets/sale', methods=['GET'])
@auth.login_required
def get_sales():
    from models import Moonlet
    try:
        results = Moonlet.query.filter(Moonlet.on_sale == True).all()

        if results is None:
            return make_response(jsonify({ 'error': 'No moonlets are on sale!' }), 404) # returns None if unfound
        else:
            results = [ item.serialize() for item in results ] # use class method to serialize each item
            results = [ make_public_moonlet(moonlet) for moonlet in results ] # give a uri for each moonlet instead of an id
            return jsonify({ 'moonlets': results }), 201 # return as json

    except Exception as error:
        print error
        return make_response(jsonify({ 'error': 'Unable to retrieve moonlets!' }), 500)

@app.route('/api/v1.0/moonlets/limited', methods=['GET'])
@auth.login_required
def get_limited():
    from models import Moonlet

    try:
        results = Moonlet.query.filter(Moonlet.limited == True).all()

        if results is None:
            return make_response(jsonify({ 'error': 'No moonlets are limited!' }), 404) # returns None if unfound
        else:
            results = [ item.serialize() for item in results ] # use class method to serialize each item
            results = [ make_public_moonlet(moonlet) for moonlet in results ] # give a uri for each moonlet instead of an id
            return jsonify({ 'moonlets': results }), 201 # return as json

    except Exception as error:
        print error
        return make_response(jsonify({ 'error': 'Unable to retrieve moonlets!' }), 500)

@app.route('/api/v1.0/users', methods=['GET'])
@auth.login_required
def get_users():
    from models import User

    try:
        results = User.query.all() # query database via sqlalchemy
        results = [ item.serialize() for item in results ] # use class method to serialize each item
        results = [ make_public_user(user) for user in results ] # give a uri for each moonlet instead of an id
        return jsonify({ 'users': results }), 201 # return as json

    except Exception as error:
        print error
        return make_response(jsonify({ 'error': 'Unable to retrieve users from database!' }), 500)

@app.route('/api/v1.0/users/<string:username>', methods=['GET'])
@auth.login_required
def get_user(username):
    from models import User

    try:
        result = User.query.filter_by(username = username).first()

        if results is None:
            return make_response(jsonify({ 'error': 'User not found!' }), 404) # returns None if unfound
        else:
            result = result.serialize() # use class method to serialize each item
            result = make_public_user(result) # give a uri for each moonlet instead of an id
            return jsonify({ 'user': result }), 201 # return as json
    except Exception as error:
        print error
        return make_response(jsonify({ 'error': 'Unable to retrieve user' }), 500)

### HTTP PUT ROUTES ###
# TODO: Add exhaustive bug checking with aborts
@app.route('/api/v1.0/moonlets/<int:moonlet_id>', methods=['PUT'])
@auth.login_required
def update_moonlet(moonlet_id):
    return jsonify({ 'update': moonlet_id })

@app.route('/api/v1.0/users/<string:username>', methods=['PUT'])
@auth.login_required
def update_user(username):
    return jsonify({ 'update': username })

### HTTP POST ROUTES ###
@app.route('/api/v1.0/moonlets', methods=['POST'])
@auth.login_required
def create_moonlet():
    from models import Moonlet

    if not request.json or not 'name' in request.json:
        abort(400)

    try:
        moonlet = Moonlet( # create a new table item out of the posted json or defaults
            name = request.json['name'],
            desc = request.json.get('description', "A newly discovered moonlet!"),
            classif = request.json.get('classification', 'AA-Zeus'),
            color = request.json.get('color', 'Grey'),
            inv = request.json.get('inventory', 100),
            price = request.json.get('price', 1000),
            disc = request.json.get('discount', 10),
            sale = request.json.get('sale', False),
            ltd = request.json.get('limited', False),
            src = request.json.get('src', '/assets/moonlets/generic.jpg')
        )
        db.session.add(moonlet)
        db.session.commit()
        return jsonify({ 'message': 'New moonlet saved to database!' }), 201

    except Exception as error:
        print error
        return make_response(jsonify({ 'error': 'Unable to add moonlet to database!'}), 500)

@app.route('/api/v1.0/users', methods=['POST'])
@auth.login_required
def create_user():
    from models import User

    if not request.json or not 'username' in request.json or not 'email' in request.json:
        abort(400)

    try:
        user = User(
            usr = request.json['username'],
            email = request.json['email'],
            platform = request.json.get('platform', 'Unknown'),
            name = request.json.get('name', 'J. Doe'),
            balance = request.json.get('balance', 2000),
            moonlets = { 'moonlets': [] }
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({ 'messsage': 'New user saved to database'}), 201

    except Exception as error:
        print error
        return make_response(jsonify({ 'error': 'Unable to add user to database!'}), 500)

#### HTTP DELETE ROUTES ###
@app.route('/api/v1.0/moonlets/<int:moonlet_id>', methods=['DELETE'])
@auth.login_required
def delete_moonlet():
    return jsonify({ 'delete': moonlet_id })

@app.route('/api/v1.0/users/<string:username>', methods=['DELETE'])
@auth.login_required
def delete_user(username):
    return jsonify({ 'delete': username })

### ERROR HANDLERS ###
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({ 'error': 'Not Found'}), 404)

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({ 'error': 'Bad Request'}), 400)

@auth.error_handler
def unauthorized():
    return make_response(jsonify({ 'error': 'Unauthorized Access'}), 403)

if __name__ == '__main__':
    app.run()
