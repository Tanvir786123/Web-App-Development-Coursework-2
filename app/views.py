from flask import render_template, flash
from app import app, db, admin
from flask_admin.contrib.sqla import ModelView
from .forms import *
from .models import *

admin.add_view(ModelView(Staff, db.session))

@app.route('/', methods=['GET', 'POST'])
def index():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        flash('Succesfully received form data. %s and %s '%(login_form.username.data, login_form.password.data))
    return render_template('index.html',
                            title='Cafè Noir',
                            form=login_form)
