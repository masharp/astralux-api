## Model module that includes SQL Alchemy models for both the moonlets and
## user tables.


from app import db
from sqlalchemy.dialects.postgresql import JSON

## Model representing a single moonlet
class Moonlet(db.Model):
    __tablename__ = 'moonlets'

    id = db.Column(db.Integer, primary_key = True, unique = True) # id key
    display_name = db.Column(db.String(), unique = True) # name of moonlet
    description = db.Column(db.String()) # description of moonlet
    classification = db.Column(db.String()) # type of moonlet
    color = db.Column(db.String()) # color of moonlet
    inventory = db.Column(db.Integer) # amount in inventory
    price = db.Column(db.Integer) # current price of moonlet
    discount = db.Column(db.Integer) # discount integer if on sale (whole number representing a percentage)
    on_sale = db.Column(db.Boolean) # if the moonlet is on sale
    limited = db.Column(db.Boolean) # if there is limited quantity (selling out or rare)
    img_src = db.Column(db.String()) # local server url for the display image

    ## method runs the first time a moonlet is created
    def __init__(self, idNum, name, desc, classif, color, inv, price, disc, sale, ltd, src):
        self.id = idNum
        self.display_name = name
        self.description = desc
        self.classification = classif
        self.color = color
        self.inventory = inv
        self.price = price
        self.discount = disc
        self.on_sale = sale
        self.limited = ltd
        self.img_src = src

    ## method represents the object when queried
    def __repr__(self):
        return '<id {}>'.format(self.id)

    ## extra property to serialize for JSON transmission
    ## converts it's sql property to a JSON property
    def serialize(self):
        return {
            'id': self.id,
            'display_name': self.display_name,
            'description': self.description,
            'classification': self.classification,
            'color': self.color,
            'inventory': self.inventory,
            'price': self.price,
            'discount': self.discount,
            'on_sale': self.on_sale,
            'limited': self.limited,
            'img_src': self.img_src
        }

    ## class method to close the session used to query
    def close(args):
        db.session.close()

## Model representing a single user
class User(db.Model):
    __tablename__ = 'users'

    username = db.Column(db.String(), primary_key = True, unique = True) # user name
    email = db.Column(db.String()) # email of user
    platform = db.Column(db.String()) # external OAuth platform (Facebook, etc.)
    display_name = db.Column(db.String()) # name of user
    balance = db.Column(db.Integer) # account coin balance
    moonlets = db.Column(JSON) # moonlet inventory
    transactions = db.Column(JSON) # transaction history
    cart = db.Column(JSON) # saved cart

    ## method runs the first time a moonlet is created
    def __init__(self, usr, email, platform, name, balance, moonlets, transactions, cart):
        self.username = usr
        self.email = email
        self.platform = platform
        self.display_name = name
        self.balance = balance
        self.moonlets = moonlets
        self.transactions = transactions
        self.cart = cart

    ## method represents the object when queried
    def __repr__(self):
        return '<user {}>'.format(self.username)

    ## extra property to serialize for JSON transmission
    ## converts it's sql property to a JSON property
    def serialize(self):
        return {
            'username': self.username,
            'display_name': self.display_name,
            'email': self.email,
            'platform': self.platform,
            'balance': self.balance,
            'moonlets': self.moonlets,
            'transactions': self.transactions,
            'cart': self.cart
        }

    ## class method to close the session used to query
    def close(args):
        db.session.close()
