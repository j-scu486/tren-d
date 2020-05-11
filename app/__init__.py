from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_redis import FlaskRedis
import redis

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
admin = Admin(app, name='TREN-D', template_mode='bootstrap3')
r = redis.StrictRedis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'], db=app.config['REDIS_DB'])

from app import routes, models
from app.routes import cart_length

# Context Processor
@app.context_processor
def cart_l():
    return dict(cart_l=cart_length)

# Flask-Admin

class ProductAdmin(ModelView):
    column_filters = ['product_category']

admin.add_view(ModelView(models.Category, db.session))
admin.add_view(ProductAdmin(models.Product, db.session))
admin.add_view(ModelView(models.Order, db.session))