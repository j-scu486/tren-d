from app import db
import datetime

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
    image_url = db.Column(db.String(50), unique=True)
    item = db.relationship('CartItem', backref="product", lazy=True)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

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