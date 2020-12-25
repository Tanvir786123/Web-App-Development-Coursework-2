from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Length

class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')

class SignUpForm(Form):
    username = StringField('Username', validators=[DataRequired(),
                            Length(min=5)])
    password = PasswordField('New password', validators=[DataRequired(),
                              EqualTo('confirmed_password',
                              message='Passwords must match.'),
                              Length(min=5)])
    confirmed_password = PasswordField('Confirm password',
                                        validators=[DataRequired()])
