from app import db
from random import randint

class Moonlet(db.Model):
    __tablename__ = 'moonlets'

    id = db.Column(db.Integer, primary_key = True) # id key
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
    def __init__(self, name, desc, classif, color, inv, price, disc, sale, ltd, src):
        self.id = randint(100000, 999999)
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
