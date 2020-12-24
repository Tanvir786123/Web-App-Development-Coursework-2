from flask import render_template, flash, redirect, url_for
from app import app, db, admin
from flask_admin.contrib.sqla import ModelView
from .forms import *
from .models import *
from flask_login import login_user, logout_user
from flask_admin.menu import MenuLink

admin.add_view(ModelView(Staff, db.session))
admin.add_view(ModelView(Controller, db.session))
admin.add_view(ModelView(Manager, db.session))

admin.add_link(MenuLink(name='Logout', category='', url="/logout"))

@app.route('/', methods=['GET', 'POST'])
def index():
    logout_user()
    default_admin_credentials()
    init_manager()
    login_form = LoginForm()
    if login_form.validate_on_submit():
        admin = Controller.query.filter_by(username=login_form.username.data)\
                                .filter_by(password=login_form.password.data)\
                                .all()
        if admin:
            login_user(Controller(login_form.username.data,\
                                  login_form.password.data))
            return redirect(url_for('admin.index'))
        else:
            manager = Manager.query.filter_by(username=login_form.username.data\
                                  ).filter_by(password=login_form.password.data\
                                  ).all()
            if manager:
                login_user(Manager(login_form.username.data,\
                                      login_form.password.data))
                flash('You are a manager')
    return render_template('index.html',
                            title='Cafè Noir',
                            form=login_form)

def default_admin_credentials():
    rows = Controller.query.count()
    if rows == 0:
        admin = Controller(username='admin', password='admin')
        db.session.add(admin)
        db.session.commit()

def init_manager():
    rows = Manager.query.count()
    if rows == 0:
        manager = Manager(username='alan123', password='alan123')
        db.session.add(manager)
        db.session.commit()

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
