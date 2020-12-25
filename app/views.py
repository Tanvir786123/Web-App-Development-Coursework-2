from flask import render_template, flash, redirect, url_for, make_response,\
                  request
from app import app, db, admin, execute_once
from flask_admin.contrib.sqla import ModelView
from .forms import *
from .models import *
from flask_login import login_user, logout_user
from flask_admin.menu import MenuLink

admin.add_view(ModelView(Controller, db.session))
admin.add_view(ModelView(Manager, db.session))
admin.add_view(ModelView(Staff, db.session))
admin.add_view(ModelView(User, db.session))

admin.add_link(MenuLink(name='Logout', category='', url="/logout"))

@app.route('/', methods=['GET', 'POST'])
def index():
    init_admin()
    init_manager()
    login_form = LoginForm()
    if login_form.validate_on_submit():
        admin = Controller.query.filter_by(username=login_form.username.data)\
                                .first()
        manager = Manager.query.filter_by(username=login_form.username.data)\
                               .first()
        staff = Staff.query.filter_by(username=login_form.username.data)\
                           .first()
        user = User.query.filter_by(username=login_form.username.data)\
                         .first()
        if admin and admin.verify_password(login_form.password.data):
            login_user(admin, remember=login_form.remember_me.data)
            return redirect(url_for('admin.index'))
        elif manager and manager.verify_password(login_form.password.data):
            login_user(manager, remember=login_form.remember_me.data)
            flash('You are a manager')
        elif staff and staff.verify_password(login_form.password.data):
            login_user(staff, remember=login_form.remember_me.data)
            flash('You are a staff member')
        elif user and user.verify_password(login_form.password.data):
            login_user(user, remember=login_form.remember_me.data)
            flash('You are a user')
        else:
            flash("Incorrect username or password")
    return render_template('index.html', title='Cafè Noir', form=login_form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    sign_up_form = SignUpForm()
    if sign_up_form.validate_on_submit():
        admin = Controller.query.filter_by(username=sign_up_form.username.data)\
                                .first()
        manager = Manager.query.filter_by(username=sign_up_form.username.data)\
                               .first()
        staff = Staff.query.filter_by(username=sign_up_form.username.data)\
                           .first()
        user = User.query.filter_by(username=sign_up_form.username.data)\
                         .first()
        if admin or manager or staff or user:
            flash('This username has been taken, please try again.')
            return render_template('signup.html', title='Cafè Noir',
                                    form=sign_up_form,
                                    status=0)
        else:
            flash('Sign up was successfull.')
            return render_template('signup.html', title='Cafè Noir',
                                    form=sign_up_form,
                                    status=1)
    return render_template('signup.html', title='Cafè Noir', form=sign_up_form,
                            status=0)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

def init_admin():
    rows = Controller.query.count()
    if rows == 0:
        admin = Controller('admin', '79A4BD7FB9')
        db.session.add(admin)
        db.session.commit()

def init_manager():
    rows = Manager.query.count()
    if rows == 0:
        manager = Manager('alan123', '79A4BD7FB9')
        db.session.add(manager)
        db.session.commit()
