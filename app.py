#!flask/bin/python
## http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
## https://realpython.com/blog/python/flask-by-example-part-2-postgres-sqlalchemy-and-alembic/
## curl -u USERNAME:PASSWORD -H "Content-Type: application/json" - POST -d '{"name":"Astralux-FA199"}' http://localhost:5000/api/v1.0/moonlets

import os

from flask import Flask
from flask import jsonify, make_response, request, abort, url_for
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.sqlalchemy import SQLAlchemy

### Database Models ###

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS']) ## load environment settings
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
auth = HTTPBasicAuth()
db = SQLAlchemy(app)

### Basic HTTP AUTH ###
@auth.get_password
def get_password(username):
    if username == 'master':
        return app.config['MASTER_PASSWORD']
    return None

### Public URI ###
## NOTE: Exposes the public URI for each item in place of the product id
## NOTE: used in conjuncture with - return jsonify({'moonlets': [make_public_moonlet(moonlet) for moonlet in moonlets]})
def make_public_moonlet(moonlet):
    new_moonlet = {}

    for field in moonlet:
        if field == 'id':
            new_moonlet['uri'] = url_for('get_moonlets', moonlet_id = moonlet['id'], _eternal = True)
        else:
            new_moonlet[field] == moonlet[field]
    return new_moonlet

### HTTP GET ROUTES ###
@app.route('/api/v1.0/moonlets', methods=['GET'])
@auth.login_required
def get_moonlets():
    from models import Moonlet

    try:
        results = Moonlet.query.all() # query database via sqlalchemy
        results = [ item.serialize() for item in results ] # use class method to serialize each item
        return jsonify({ 'moonlets': results }), 201 # return as json

    except Exception as error:
        print error
        return make_response(jsonify({ 'error': 'Unable to retrieve moonlets from database!' }), 500)

@app.route('/api/v1.0/moonlets/<int:moonlet_id>', methods=['GET'])
@auth.login_required
def get_moonlet(moonlet_id):
    return jsonify({ 'moonlet': moonlet_id })

@app.route('/api/v1.0/moonlets/sale', methods=['GET'])
@auth.login_required
def get_sales():
    return jsonify({ 'sale': 123123 })

@app.route('/api/v1.0/moonlets/limited', methods=['GET'])
@auth.login_required
def get_limited():
    return jsonify({ 'limited': 123123 })

### HTTP PUT ROUTES ###
# TODO: Add exhaustive bug checking with aborts
@app.route('/api/v1.0/moonlets/<int:moonlet_id>', methods=['PUT'])
@auth.login_required
def update_moonlet(moonlet_id):
    return jsonify({ 'update': moonlet_id })

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

#### HTTP DELETE ROUTES ###
@app.route('/api/v1.0/moonlets/<int:moonlet_id>', methods=['DELETE'])
@auth.login_required
def delete_moonlet():
    return jsonify({ 'delete': moonlet_id })

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
