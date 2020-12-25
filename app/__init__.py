from flask import Flask
from flask_admin import Admin, AdminIndexView
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db, render_as_batch=True)

login_manager = LoginManager(app)

execute_once = False

# Create customized model view class
class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('index'))

# Create customized index view class
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated

admin = Admin(app, template_mode='bootstrap4', index_view=MyAdminIndexView())

from app import views, models

# Create user loader function
@login_manager.user_loader
def load_user(username):
    admin = models.Controller.query.filter_by(username=username).first()
    manager = models.Manager.query.filter_by(username=username).first()
    staff = models.Staff.query.filter_by(username=username).first()
    user = models.User.query.filter_by(username=username).first()
    if admin:
        return admin
    elif manager:
        return manager
    elif staff:
        return staff
    elif user:
        return user
    else:
        return None
