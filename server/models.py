from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class Restaurant(db.Model, SerializerMixin):
    __tablename__ = 'restaurants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    
    restaurant_pizzas = db.relationship('RestaurantPizza', back_populates='restaurant', cascade="all, delete-orphan")

    def to_dict(self, exclude=None):
        if exclude is None:
            exclude = []
        restaurant_dict = {
            "id": self.id,
            "name": self.name,
            "address": self.address,
        }
        if 'restaurant_pizzas' not in exclude:
            restaurant_dict['restaurant_pizzas'] = [rp.to_dict(exclude=['restaurant']) for rp in self.restaurant_pizzas]
        return restaurant_dict

class Pizza(db.Model, SerializerMixin):
    __tablename__ = 'pizzas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)

    restaurant_pizzas = db.relationship('RestaurantPizza', back_populates='pizza', cascade="all, delete-orphan")

    def to_dict(self, exclude=None):
        if exclude is None:
            exclude = []
        pizza_dict = {
            "id": self.id,
            "name": self.name,
            "ingredients": self.ingredients,
        }
        if 'restaurant_pizzas' not in exclude:
            pizza_dict['restaurant_pizzas'] = [rp.to_dict(exclude=['pizza']) for rp in self.restaurant_pizzas]
        return pizza_dict

class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = 'restaurant_pizzas'

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)

    pizza = db.relationship('Pizza', back_populates='restaurant_pizzas')
    restaurant = db.relationship('Restaurant', back_populates='restaurant_pizzas')

    @validates('price')
    def validate_price(self, key, price):
        if price < 1 or price > 30:
            raise ValueError("Price must be between 1 and 30")
        return price

    def to_dict(self):
        return {
            "id": self.id,
            "price": self.price,
            "pizza_id": self.pizza_id,
            "restaurant_id": self.restaurant_id,
            "pizza": self.pizza.to_dict(exclude=['restaurant_pizzas']),
            "restaurant": self.restaurant.to_dict(exclude=['restaurant_pizzas']),
        }
