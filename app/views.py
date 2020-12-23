from flask import render_template, flash
from app import app
from .forms import *

@app.route('/', methods=['GET', 'POST'])
def index():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        flash('Succesfully received form data. %s and %s '%(login_form.username.data, login_form.password.data))
    return render_template('index.html',
                            title='Caffè Noir',
                            form=login_form)
