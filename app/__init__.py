from flask import Flask, url_for, redirect
from flask_admin import Admin, AdminIndexView
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, AnonymousUserMixin
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
import logging

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db, render_as_batch=True)

login_manager = LoginManager(app)
login_manager.session_protection = "strong"

logging.basicConfig(filename="system.log", level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s"
                            +" %(threadName)s : %(message)s\n")

app.logger.disabled = True
log = logging.getLogger('werkzeug')
log.disabled = True

# Create customized model view class
class MyModelView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated == False:
            return False
        elif current_user.account_type() == models.Account.CONTROLLER_ACCOUNT:
            return True
        else:
            return False

# Create customized index view class
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if current_user.is_authenticated == False:
            return False
        elif current_user.account_type() == models.Account.CONTROLLER_ACCOUNT:
            return True
        else:
            return False

admin = Admin(app, template_mode='bootstrap4', index_view=MyAdminIndexView())

from app import views, models

admin.add_view(MyModelView(models.User, db.session))
admin.add_view(MyModelView(models.Staff, db.session))
admin.add_view(MyModelView(models.Manager, db.session))
admin.add_view(MyModelView(models.Controller, db.session))
admin.add_view(MyModelView(models.Product, db.session))
admin.add_view(MyModelView(models.Basket, db.session))
admin.add_view(MyModelView(models.Transaction, db.session))

admin.add_link(MenuLink(name='Logout', category='', url="/logout"))

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
