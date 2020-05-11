from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import datetime

class AdminUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    image = db.Column(db.String(50))
    product_list = db.relationship('Product', backref="product_category", lazy=True)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '<{}>'.format(self.name)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    category = db.Column(db.Integer, db.ForeignKey('category.id'))
    size =db.Column(db.String(1))
    color = db.Column(db.String(10))
    stock = db.Column(db.Integer)
    description = db.Column(db.String(100), nullable=True)
    price = db.Column(db.Integer)
    available = db.Column(db.Boolean)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime, nullable=True)
    image_url = db.Column(db.String(50))
    item = db.relationship('CartItem', backref="product", lazy=True)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def reduce_qty(self, quantity):
        self.stock = self.stock - quantity
        self.save()
    
    def __repr__(self):
        return '<Product: {}>'.format(self.name)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50)) 
    email = db.Column(db.String(50))
    address = db.Column(db.String(50))
    postal_code = db.Column(db.String(50))
    city = db.Column(db.String(50))
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime)
    paid = db.Column(db.Boolean, default=False)
    order_item = db.relationship('CartItem', backref="order", lazy=True)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def mark_paid(self):
        self.paid = True

    def __repr__(self):
        return '<Order ID: {}>'.format(self.id)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    quantity = db.Column(db.Integer)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '{}'.format(self.product)