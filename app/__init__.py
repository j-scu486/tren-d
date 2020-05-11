from flask import Flask, render_template, redirect, url_for, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_redis import FlaskRedis
import redis
import os

from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user
from .forms import LoginForm

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager()
# r = redis.StrictRedis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'], db=app.config['REDIS_DB'])
r = redis.from_url(os.environ.get("REDIS_URL"))

from app import routes, models
from app.routes import cart_length
from app.models import AdminUser

# Context Processor
@app.context_processor
def cart_l():
    return dict(cart_l=cart_length)

# Flask-Admin
login.init_app(app)

class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))
        
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated

class ProductAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

    column_filters = ['product_category']

admin = Admin(app, name="TREN-D", index_view=MyAdminIndexView())
admin.add_view(MyModelView(models.Category, db.session))
admin.add_view(ProductAdmin(models.Product, db.session))
admin.add_view(MyModelView(models.Order, db.session))

# Admin Login settings

@login.user_loader
def load_user(user_id):
    return AdminUser.query.get(user_id)

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = AdminUser.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            print('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('admin.index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/admin/logout')
def logout():
    logout_user()
    return 'Logged Out!'