from app import database
from sqlalchemy.dialects.postgresql import JSON

class Moonlets(database.Model):
    __tablename__ = 'moonlets'

    id = database.Column(database.Integer, primary_key = True) # id key
    updated = database.Column(database.DateTime) # date of last update
    display_name = database.Column(database.String(), unique = True) # name of moonlet
    description = database.Column(database.String()) # description of moonlet
    classification = database.Column(database.String()) # type of moonlet
    color = database.Column(database.String()) # color of moonlet
    inventory = database.Column(database.Integer) # amount in inventory
    price = database.Column(database.Integer) # current price of moonlet
    discount = database.Column(database.Integer) # discount integer if on sale (whole number representing a percentage)
    on_sale = database.Column(database.Boolean) # if the moonlet is on sale
    limited = database.Column(database.Boolean) # if there is limited quantity (selling out or rare)
    img_src = database.Column(database.String()) # local server url for the display image

    ## method runs the first time a moonlet is created
    def __init__(self, updated, name, desc, classif, color, inv, price, disc, sale, ltd, src):
        self.updated = updated
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
        return '<id {}'.format(self.id)
