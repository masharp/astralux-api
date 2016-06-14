## Central Flask application script. Includes all routes for the REST API,
## error handlers, and business logic. Authenticates route calls via simple HTTP
## username:password auth. Imports SQLAlchemy ORM models in order to interact with
## PostgreSQL datastore.
##
## TODO: Decompose business logic and import via functions

#!flask/bin/python

import os, types, json
from datetime import datetime
from random import randint
from modules.make_error_response import make_error_response

from flask import Flask
from flask import jsonify, request, abort, url_for
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
        abort(500)

@app.route('/api/moonlets/<int:moonlet_id>', methods=['GET'])
@auth.login_required
def get_moonlet(moonlet_id):
    from models import Moonlet

    try:
        result = Moonlet.query.filter_by(id = moonlet_id).first() # query for moonlet
        if result is None: return make_error_response('User or Moonlet Not Found', 404)

        result = result.serialize()
        return jsonify({ 'moonlet': result }), 201

    except Exception as error:
        print error
        abort(500)

@app.route('/api/moonlets/sale', methods=['GET'])
@auth.login_required
def get_sales():
    from models import Moonlet

    try:
        results = Moonlet.query.filter(Moonlet.on_sale == True).all()
        if results is None: return make_error_response('User or Moonlet Not Found', 404) # returns None if unfound

        results = [ item.serialize() for item in results ] # use class method to serialize each item
        return jsonify({ 'moonlets': results }), 201 # return as json

    except Exception as error:
        print error
        abort(500)

@app.route('/api/moonlets/limited', methods=['GET'])
@auth.login_required
def get_limited():
    from models import Moonlet

    try:
        results = Moonlet.query.filter(Moonlet.limited == True).all()
        if results is None: return make_error_response('User or Moonlet Not Found', 404) # returns None if unfound

        results = [ item.serialize() for item in results ] # use class method to serialize each item
        return jsonify({ 'moonlets': results }), 201 # return as json

    except Exception as error:
        print error
        abort(500)

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
        abort(500)

@app.route('/api/users/<string:username>', methods=['GET'])
@auth.login_required
def get_user(username):
    from models import User

    try:
        result = User.query.filter_by(username = username).first()
        if result is None: return make_error_response('User or Moonlet Not Found', 404) # returns None if unfound

        result = result.serialize() # use class method to serialize each item
        return jsonify({ 'user': result }), 201 # return as json

    except Exception as error:
        print error
        abort(500)

### HTTP PUT ROUTES ###
@app.route('/api/moonlets/<int:moonlet_id>', methods=['PUT'])
@auth.login_required
def update_moonlet(moonlet_id):

    from models import Moonlet

    if not request.json or not 'update' in request.json:
        abort(400)

    update = request.json['update']

    try:
        moonlet = Moonlet.query.filter_by(id = moonlet_id).first()
        if moonlet is None: return make_error_response('User or Moonlet Not Found', 404)

        #check the update object for the field that need updated, then type check and update
        if 'img_src' in update:
            new_src = update['img_src']

            if not isinstance(new_src, types.UnicodeType):
                return make_error_response('Update.img_source must be a string!', 400)

            moonlet.img_src = new_src

        if 'color' in update:
            new_color = update['color']

            if not isinstance(new_color, types.UnicodeType):
                return make_error_response('Update.color must be a string!', 400)

            moonlet.color = new_color

        if 'price' in update:
            new_price = update['price']

            if not isinstance(new_price, types.IntType):
                return make_error_response('Update.price must be an int!', 400)

            moonlet.price = new_price

        if 'discount' in update:
            new_discount = update['discount']

            if not isinstance(new_discount, types.IntType):
                return make_error_response('Update.discount must be an int!', 400)

            moonlet.discount = new_discount

        if 'inventory' in update:
            new_inv = update['inventory']

            if not isinstance(new_inv, types.IntType):
                return make_error_response('Update.inventory must be an int!', 400)

            moonlet.inventory = new_inv

        if 'description' in update:
            new_desc = update['description']

            if not isinstance(new_desc, types.UnicodeType):
                return make_error_response('Update.description must be a string!', 400)

            moonlet.description = new_desc

        if 'classification' in update:
            new_class = update['classification']

            if not isinstance(new_class, types.UnicodeType):
                return make_error_response('Update.classification must be a string!', 400)

            moonlet.classification = new_class

        if 'limited' in update:
            new_limited = update['limited']

            if not isinstance(new_limited, types.BooleanType):
                return make_error_response('Update.limited must be a bool!', 400)

            moonlet.limited = new_limited

        if 'sale' in update:
            new_sale = update['sale']

            if not isinstance(new_sale, types.BooleanType):
                return make_error_response('Update.featured must be a bool!', 400)

            moonlet.on_sale = new_sale

        db.session.commit()
        moonlet.close()

        return(jsonify({ 'message': 'Moonlet updated!'})), 201

    except Exception as error:
        print error
        abort(500)

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
        if user is None: return make_error_response('User or Moonlet Not Found', 404)

        user.email = newEmail

        db.session.commit()
        user.close()

        return(jsonify({ 'message': 'User email updated'})), 201

    except Exception as error:
        print error
        abort(500)

# update a user's cart
@app.route('/api/users/cart/<string:username>', methods=['PUT'])
@auth.login_required
def update_user_cart(username):
    from models import User

    if not request.json or not 'cart' in request.json:
        abort (400)

    cart = request.json['cart']

    try:
        user = User.query.filter_by(username = username).first()
        if user is None: return make_error_response('User or Moonlet Not Found', 404)

        user.cart = { 'current': cart }

        db.session.commit()
        user.close()

        return jsonify({ 'message': 'Cart updated!' }), 201
    except Exception as error:
        print error
        abort(500)

# updates a user's refunds
@app.route('/api/users/refund/<string:username>', methods=['PUT'])
@auth.login_required
def update_user_refund(username):
    if not request.json or not 'transaction' in request.json:
        abort(400)

    from models import User, Moonlet

    # set up a new transction refund
    now = str(datetime.utcnow())
    transactionID = int(request.json['transaction'])

    newTransaction = {
        'timestamp': now,
        'transaction': 'refund',
        'moonlets': [],
        'price': 0,
        'id': transactionID
    }

    try:
        user = User.query.filter_by(username = username).first()
        if user is None: return make_error_response('User or Moonlet Not Found', 404) # returns None if unfound

        ## pull out fields to be modified
        temp = user.serialize()
        currentTransactions = temp['transactions']['history']
        currentBalance = temp['balance']
        currentMoonlets = temp['moonlets']['inventory']

        ## new variables to represent clean state
        newHistory = [] # new history array to be updated to user store after refund item removed for history
        newMoonlets = [] # new moonelts array to be updated to remove a moonlet if refund = 0
        newBalance = 0

        refundAmount = 0
        refundTransaction = None

        # find the transaction to be refunded
        for x in currentTransactions:
            currentID = int(x['id'])

            if currentID == transactionID and x['transaction'] != 'refund':
                refundTransaction = x
            else:
                newHistory.append(x) # add other transactions to the new history array

        # if empty, transaction not found, if more than 1 transaction, transaction already refunded
        if refundTransaction is None: return make_error_response('Transaction not found!', 404)

        # calculate cost of transaction and finish construction of transaction object
        for y in refundTransaction['moonlets']:
            item = str(y['item'])
            identity = int(item)
            price = int(y['price'])
            amount = int(y['amount'])
            newTransaction['moonlets'].append(y)
            refundAmount += price * amount # amount of item * price of item

            ## remove current moonlet from user's moonlet inventory
            for i in currentMoonlets:
                if item in i:
                    if int(i[item] - amount) > 0:
                        i[item] -= amount
                    elif int(i[item] - amount) == 0:
                        currentMoonlets.remove(i)

            ## Reflect new refund in moonlet inventory
            moonlet = Moonlet.query.filter_by(id = identity).first()
            tempInventory = moonlet.inventory
            tempInventory = tempInventory + amount
            moonlet.inventory = tempInventory

        ## Finish transaction object and assign clean states
        for z in currentMoonlets: newMoonlets.append(z)
        newTransaction['price'] = refundAmount
        newBalance = currentBalance + refundAmount # update user's balance entry after refund
        newHistory.append(newTransaction) # update user's transaction entries

        # Update user's database entry with new values
        user.moonlets = { 'inventory': newMoonlets }
        user.transactions = { 'history': newHistory }
        user.balance = newBalance

        db.session.commit()

        # return the transction created by the refund to be used by the view
        return jsonify({ 'message': 'Refund Made!', 'transaction': newTransaction }), 201

    except Exception as error:
        print error
        abort(500)

# Updates a user's purchases - compares request transaction to user's stored cart
# TODO: Add a check against PUT request and database information
@app.route('/api/users/purchase/<string:username>', methods=['PUT'])
@auth.login_required
def update_user_purchase(username):
    from models import User, Moonlet

    now = str(datetime.utcnow())
    transactionID = randint(100000, 999999) + randint(999999, 99999999)

    newTransaction = {
        'timestamp': now,
        'transaction': 'purchase',
        'id': transactionID,
        'moonlets': [],
        'price': 0
    }

    try:
        user = User.query.filter_by(username = username).first()
        if user is None: return make_error_response('User or Moonlet Not Found', 404) # returns None if unfound

        # pull out information to be modified
        temp = user.serialize()
        currentCart = temp['cart']['current']
        currentTransactions = temp['transactions']['history']
        currentMoonlets = temp['moonlets']['inventory']
        currentBalance = temp['balance']

        ## new variables to represent clean state
        newTransactions = []
        newMoonlets = []
        newBalance = 0

        transactionCost = 0 # cost of this transaction

        # calculate cost of transaction and finish construction of transaction object
        for c in currentCart:
            item = str(c['item'])
            identity = int(item)
            price = int(c['price'])
            amount = int(c['amount'])
            newTransaction['moonlets'].append(c)
            transactionCost += price * amount # amount of item * price of item
            found = False

            ## add current moonlet to user's moonlet inventory
            for x in currentMoonlets:
                if item in x:
                    a = x[item] + amount
                    currentMoonlets.remove(x)
                    currentMoonlets.append({ item: a })
                    found = True
            if found == False: newMoonlets.append({ item: amount })

            ## Reflect new purchase in each moonlets inventory
            moonlet = Moonlet.query.filter_by(id = identity).first()
            tempInventory = moonlet.inventory
            tempInventory = tempInventory - amount
            moonlet.inventory = tempInventory

        ## Finish new transaction and assign clean states
        ## transfer past transactions and new moonlets
        for y in currentTransactions: newTransactions.append(y)
        for z in currentMoonlets: newMoonlets.append(z)
        print newMoonlets
        newTransaction['price'] = transactionCost
        newBalance = currentBalance - transactionCost  # update user's balance entry after transaction
        newTransactions.append(newTransaction) # update user's transaction entries

        ## Update user's database entry with new values
        user.moonlets = { 'inventory': newMoonlets }
        user.transactions = { 'history': newTransactions }
        user.balance = newBalance
        user.cart = { 'current': [] }

        db.session.merge(user)
        db.session.commit()

        return jsonify({ 'message': 'Purchase Made!', 'transaction': newTransaction }), 201

    except Exception as error:
        print error
        abort(500)

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
        if moonlet is not None: return make_error_response('Moonlet already exists!', 400)

        newMoonlet = Moonlet( # create a new table item out of the posted json or defaults
            name = newName,
            idNum = randint(10000000, 99999999),
            desc = request.json.get('description', 'A newly discovered moonlet!'),
            classif = request.json.get('classification', 'AA-Zeus'),
            color = request.json.get('color', 'Grey'),
            inv = request.json.get('inventory', 100),
            price = request.json.get('price', 1000),
            disc = request.json.get('discount', 10),
            sale = request.json.get('on_sale', False),
            ltd = request.json.get('limited', False),
            src = request.json.get('img_src', '/assets/moonlets/generic.png')
        )

        db.session.add(newMoonlet)
        db.session.commit()
        moonlet.close()

        return jsonify({ 'message': 'New moonlet saved to database!' }), 201

    except Exception as error:
        print error
        abort(500)

@app.route('/api/users', methods=['POST'])
@auth.login_required
def create_user():
    if not request.json or not 'username' in request.json:
        abort(400)

    from models import User

    username = request.json['username']

    try:
        user = User.query.filter_by(username = username).first()
        if user is not None: return make_error_response('User already exists', 400)

        user = User(
            usr = username,
            email = request.json.get('email', ''),
            platform = request.json.get('platform', ''),
            name = request.json.get('name', 'J. Doe'),
            balance = request.json.get('balance', 10000),
            moonlets = { 'inventory': [] },
            transactions = { 'history': [] },
            cart = { 'current': [] }
        )

        ## serialize new user to return with confirmation
        userJSON = user.serialize()

        db.session.add(user)
        db.session.commit()
        user.close()

        return jsonify({ 'messsage': 'New user saved to database!', 'user': userJSON }), 201

    except Exception as error:
        print error
        abort(500)

#### HTTP DELETE ROUTES ###
@app.route('/api/moonlets/<int:moonlet_id>', methods=['DELETE'])
@auth.login_required
def delete_moonlet(moonlet_id):

    from models import Moonlet

    try:
        moonlet = Moonlet.query.filter_by(id = moonlet_id).first()
        if moonlet is None: return make_error_response('User or Moonlet Not Found', 404)
        moonlet.close() # internal session closure to remove conflict

        db.session.delete(moonlet)
        db.session.commit()

        return jsonify({ 'messsage': 'Moonlet successfully deleted!'}), 201

    except Exception as error:
        print error
        abort(500)

@app.route('/api/users/<string:username>', methods=['DELETE'])
@auth.login_required
def delete_user(username):
    from models import User

    try:
        user = User.query.filter_by(username = username).first()
        if user is None: return make_error_response('User or Moonlet Not Found', 404)
        user.close() # internal session closure to remove conflict

        db.session.delete(user)
        db.session.commit()

        return jsonify({ 'messsage': 'User successfully deleted!'}), 201

    except Exception as error:
        print error
        abort(500)

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

@app.errorhandler(500)
def internal_error(error):
    return make_error_response('Internal Error', 500)

@auth.error_handler
def unauthorized():
    return make_error_response('Unauthorized Access', 403)

if __name__ == '__main__':
    app.run(threaded = True)
