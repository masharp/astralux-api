#!flask/bin/python
## http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
## https://realpython.com/blog/python/flask-by-example-part-2-postgres-sqlalchemy-and-alembic/
## curl -u USERNAME:PASSWORD -H "Content-Type: application/json" -X POST -d '{"name":"Astralux-FA199"}' http://localhost:5000/api/v1.0/moonlets
## curl -u USERNAME:PASSWORD -H "Content-Type: application/json" -X PUT -d '{"timestamp": "05/21/16", "moonlet": 520200, "action":"purchase"}' http://localhost:5000/api/v1.0/users/admin

import os
import json
from datetime import datetime
from random import randint

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

### Basic Error Message Generator ###
def make_error_response(message = 'Internal Error!', code = 500):
    return make_response(jsonify({ 'error': message }), code)

### Basic HTTP AUTH ###
@auth.get_password
def get_password(username):
    if username == app.config['MASTER_USERNAME']: return app.config['MASTER_PASSWORD']
    return None

### HTTP GET ROUTES ###
@app.route('/api/moonlets', methods=['GET'])
@auth.login_required
def get_moonlets():
    from models import Moonlet

    try:
        results = Moonlet.query.all() # query database via sqlalchemy
        results = [ item.serialize() for item in results ] # use class method to serialize each item


        return jsonify({ 'moonlets': results }), 201 # return as json

    except Exception as error:
        print error
        return make_error_response('Unable to retrieve moonlets from database!', 500)

@app.route('/api/moonlets/<int:moonlet_id>/<string:moonlet_name>', methods=['GET'])
@auth.login_required
def get_moonlet(moonlet_id, moonlet_name):
    from models import Moonlet

    try:
        result = Moonlet.query.filter_by(id = moonlet_id).first() # query for moonlet
        if result is None: return make_error_response('Moonlet not found!', 404) # returns None if unfound
        result = result.serialize()

        return jsonify({ 'moonlet': result }), 201

    except Exception as error:
        print error
        return make_error_response()

@app.route('/api/moonlets/sale', methods=['GET'])
@auth.login_required
def get_sales():
    from models import Moonlet
    try:
        results = Moonlet.query.filter(Moonlet.on_sale == True).all()
        if results is None: return make_error_response('No moonlets are on sale!', 404)# returns None if unfound
        results = [ item.serialize() for item in results ] # use class method to serialize each item

        return jsonify({ 'moonlets': results }), 201 # return as json

    except Exception as error:
        print error
        return make_error_response()

@app.route('/api/moonlets/limited', methods=['GET'])
@auth.login_required
def get_limited():
    from models import Moonlet

    try:
        results = Moonlet.query.filter(Moonlet.limited == True).all()
        if results is None: return make_error_response('No moonlets are limited!', 404) # returns None if unfound
        results = [ item.serialize() for item in results ] # use class method to serialize each item

        return jsonify({ 'moonlets': results }), 201 # return as json

    except Exception as error:
        print error
        return make_error_response()

@app.route('/api/users', methods=['GET'])
@auth.login_required
def get_users():
    from models import User

    try:
        results = User.query.all() # query database via sqlalchemy
        results = [ item.serialize() for item in results ] # use class method to serialize each item

        return jsonify({ 'users': results }), 201 # return as json

    except Exception as error:
        print error
        return make_error_response()

@app.route('/api/users/<string:username>', methods=['GET'])
@auth.login_required
def get_user(username):
    from models import User

    try:
        result = User.query.filter_by(username = username).first()
        if result is None: return make_error_response('User not found!', 404) # returns None if unfound
        result = result.serialize() # use class method to serialize each item

        return jsonify({ 'user': result }), 201 # return as json

    except Exception as error:
        print error
        return make_error_response()

### HTTP PUT ROUTES ###
@app.route('/api/moonlets/<int:moonlet_id>', methods=['PUT'])
@auth.login_required
def update_moonlet(moonlet_id):
    return jsonify({ 'update': moonlet_id })

# currently only updates a user's email
@app.route('/api/users/<string:username>', methods=['PUT'])
@auth.login_required
def update_user(username):
    if not request.json or not 'email' in request.json:
        abort(400)

    from models import User

    newEmail = str(request.json['email'])
    simpleEmailAuth = newEmail.split('@')

    if len(simpleEmailAuth) != 2: return make_error_response('Invalid email address!', 404)

    try:
        user = User.query.filter_by(username = username).first()
        if user is None: return make_error_response('User or moonlet not found!', 404)
        user.email = newEmail

        db.session.merge(user)
        db.session.commit()

        return(jsonify({ 'message': 'User email updated'})), 201

    except Exception as error:
        print error
        return make_error_response()

# updates a user's refunds
@app.route('/api/users/refund/<string:username>', methods=['PUT'])
@auth.login_required
def update_user_refund(username):
    if not request.json or not 'transaction' in request.json:
        abort(400)

    from models import User

    now = str(datetime.utcnow())
    timestamp = request.json.get('timestamp', now)
    transactionID = int(request.json['transaction'])
    transactionType = 'refund'

    try:
        user = User.query.filter_by(username = username).first()

        if user is None: return make_error_response('User or moonlet not found!', 404) # returns None if unfound

        temp = user.serialize()
        pastTransactions = temp['transactions']
        refundTransaction = None

        for x in pastTransactions['history']:
            currentID = int(x['id'])
            if currentID == transactionID and x['transaction'] != 'refund':
                refundTransaction = x

        if refundTransaction is None:
            return make_error_response('Transaction not found!', 404)

        item = str(refundTransaction['moonlet'])
        amount = int(refundTransaction['amount'])
        price = int(refundTransaction['price'])
        transactionID = refundTransaction['id']

        newTransaction = {
            'timestamp': timestamp,
            'transaction': transactionType,
            'moonlet': item,
            'amount': amount,
            'price': price,
            'id': transactionID
        }

        ## update user's current account balance
        updatedBalance = temp['balance'] + price

        ## update transaction history with this transaction
        updatedTransactions = temp['transactions']
        updatedTransactions['history'].append(newTransaction)

        ## update the user's moonlets with this transaction
        updatedMoonlets = temp['moonlets']
        updatedMoonlets[item] -= amount

        user.balance = updatedBalance
        user.moonlets = updatedMoonlets
        user.transactions = updatedTransactions

        db.session.merge(user) ## added .merge() because it wasn't updating in .commit() without it
        db.session.commit()

        return jsonify({ 'message': 'User updated!' }), 201

    except Exception as error:
        print error
        return make_error_response()

# Updates a user's purchases
@app.route('/api/users/purchase/<string:username>', methods=['PUT'])
@auth.login_required
def update_user_purchase(username):
    if not request.json or not 'moonlet' in request.json or not 'price' in request.json:
        abort(400)

    from models import User, Moonlet

    now = str(datetime.utcnow())
    item = str(request.json['moonlet'])
    amount = int(request.json.get('amount', 1))
    price = int(request.json['price']) * amount
    timestamp = request.json.get('timestamp', now)
    transactionType = 'purchase'
    transactionID = randint(1000, 9999) + randint(9999, 999999)

    newTransaction = {
        'timestamp': timestamp,
        'transaction': transactionType,
        'moonlet': item,
        'price': price,
        'id': transactionID,
        'amount': amount
    }

    try:
        user = User.query.filter_by(username = username).first()
        moonlet = Moonlet.query.filter_by(id = item).first()

        if user is None or moonlet is None: return make_error_response('User or moonlet not found!', 404) # returns None if unfound

        temp = user.serialize()

        ## update user's current account balance
        updatedBalance = temp['balance'] - price

        ## update transaction history with this transaction
        updatedTransactions = temp['transactions']
        updatedTransactions['history'].append(newTransaction)

        ## update the user's moonlets with this transaction
        updatedMoonlets = temp['moonlets']

        if item in updatedMoonlets:
            updatedMoonlets[item] += amount
        else:
            updatedMoonlets[item] = amount

        user.balance = updatedBalance
        user.moonlets = updatedMoonlets
        user.transactions = updatedTransactions

        db.session.merge(user) ## added .merge() because it wasn't updating in .commit() without it
        db.session.commit()

        return jsonify({ 'message': 'User updated!' }), 201

    except Exception as error:
        print error
        return make_error_response()

### HTTP POST ROUTES ###
@app.route('/api/moonlets', methods=['POST'])
@auth.login_required
def create_moonlet():
    if not request.json or not 'name' in request.json:
        abort(400)

    from models import Moonlet
    newName = request.json['name']

    try:
        moonlet = Moonlet.query.filter_by(display_name = newName).first()

        if moonlet is not None: return make_error_response('Moonlet already exists!', 404)

        newMoonlet = Moonlet( # create a new table item out of the posted json or defaults
            name = newName,
            idNum = randint(100000, 999999),
            desc = request.json.get('description', 'A newly discovered moonlet!'),
            classif = request.json.get('classification', 'AA-Zeus'),
            color = request.json.get('color', 'Grey'),
            inv = request.json.get('inventory', 100),
            price = request.json.get('price', 1000),
            disc = request.json.get('discount', 10),
            sale = request.json.get('sale', False),
            ltd = request.json.get('limited', False),
            src = request.json.get('src', '/assets/moonlets/generic.jpg')
        )

        db.session.add(newMoonlet)
        db.session.commit()

        return jsonify({ 'message': 'New moonlet saved to database!' }), 201

    except Exception as error:
        print error
        return make_error_response()

@app.route('/api/users', methods=['POST'])
@auth.login_required
def create_user():
    if not request.json or not 'username' in request.json:
        abort(400)

    from models import User
    username = request.json['username']

    try:
        user = User.query.filter_by(username = username).first()

        if user is not None: return make_error_response('User already exists', 404)
        user = User(
            usr = username,
            email = request.json.get('email', ''),
            platform = request.json.get('platform', ''),
            name = request.json.get('name', 'J. Doe'),
            balance = request.json.get('balance', 10000),
            moonlets = { },
            transactions = { 'history': [] },
            cart = { }
        )
        db.session.add(user)
        db.session.commit()

        return jsonify({ 'messsage': 'New user saved to database!'}), 201

    except Exception as error:
        print error
        return make_error_response()

#### HTTP DELETE ROUTES ###
@app.route('/api/moonlets/<int:moonlet_id>', methods=['DELETE'])
@auth.login_required
def delete_moonlet():
    return jsonify({ 'delete': moonlet_id })

@app.route('/api/users/<string:username>', methods=['DELETE'])
@auth.login_required
def delete_user(username):
    from models import User

    try:
        user = User.query.filter_by(username = username).first()
        if user is None: return make_error_response('User does not exist!', 404)
        user.close()

        db.session.delete(user)
        db.session.commit()

        return jsonify({ 'messsage': 'User successfully deleted!'}), 201

    except Exception as error:
        print error
        return make_error_response()

### ERROR HANDLERS ###
@app.errorhandler(405)
def not_allowed(error):
    return make_error_response('Request Not Allowed', 405)

@app.errorhandler(404)
def not_found(error):
    return make_error_response('Not Found', 404)

@app.errorhandler(400)
def bad_request(error):
    return make_error_response('Bad Request', 400)

@auth.error_handler
def unauthorized():
    return make_error_response('Unauthorized Access', 403)

if __name__ == '__main__':
    app.run(threaded = True)
