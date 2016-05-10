#!flask/bin/python
#http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask

from flask import Flask
from flask import jsonify, make_response, request, abort, url_for
from flask.ext.httpauth import HTTPBasicAuth

app = Flask(__name__)
auth = HTTPBasicAuth()

################ Basic HTTP AUTH ##########################
## NOTE: Obfuscate username and password in production
@auth.get_password
def get_password(username):
    if username == 'abcdefg':
        return 'xyz'
    return None

################ Public URI ################################
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

#################### HTTP GET ROUTES #################
@app.route('/api/v1.0/moonlets', methods=['GET'])
@auth.login_required
def get_moonlets():
    return jsonify({ 'moonlets': 13123123 })

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

#################### HTTP PUT ROUTES ######################
# TODO: Add exhaustive bug checking with aborts
@app.route('/api/v1.0/moonlets/<int:moonlet_id>', methods=['PUT'])
@auth.login_required
def update_moonlet(moonlet_id):
    return jsonify({ 'update': moonlet_id })

#################### HTTP POST ROUTES ######################
@app.route('/api/v1.0/moonlets', methods=['POST'])
@auth.login_required
def create_moonlet():
    if not request.json or not 'name' in request.json:
        abort(400)

    moonlet = {
        'id': 1231232131,
        'name': request.json['name'],
        'description': request.json.get('description', "A new Moonlet!"),
        'price': request.json.get('price', 0.0),
        'inventory': request.json.get('inventory', 10),
        'sale': False,
        'sale_price': 0.0
    }
    return jsonify({ 'moonlet': moonlet }), 201

#################### HTTP DELETE ROUTES ######################
@app.route('/api/v1.0/moonlets/<int:moonlet_id>', methods=['DELETE'])
@auth.login_required
def delete_moonlet():
    return jsonify({ 'delete': moonlet_id })

################## ERROR HANDLERS ###########################
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
    app.run(debug = True)
