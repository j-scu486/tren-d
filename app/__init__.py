from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
admin = Admin(app, name='TREN-D', template_mode='bootstrap3')

from app import routes, models

# Flask-Admin

class ProductAdmin(ModelView):
    column_filters = ['product_category']

admin.add_view(ModelView(models.Category, db.session))
admin.add_view(ProductAdmin(models.Product, db.session))
admin.add_view(ModelView(models.Order, db.session))