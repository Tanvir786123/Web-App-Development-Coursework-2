from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, TextAreaField\
                    ,IntegerField
from wtforms.validators import DataRequired, EqualTo, Length, NumberRange\
                               ,Regexp, InputRequired

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

class AddStaffForm(Form):
    username = StringField('Username', validators=[DataRequired(),
                            Length(min=5)])
    password = PasswordField('New password', validators=[DataRequired(),
                              EqualTo('confirmed_password',
                              message='Passwords must match.'),
                              Length(min=5)])
    confirmed_password = PasswordField('Confirm password',
                                        validators=[DataRequired()])

class ChangeMyPasswordForm(Form):
    password = PasswordField('New password', validators=[DataRequired(),
                              EqualTo('confirmed_password',
                              message='Passwords must match.'),
                              Length(min=5)])
    confirmed_password = PasswordField('Confirm password',
                                        validators=[DataRequired()])

class AddProducts(Form):
    product_name = StringField('Product name', validators=[DataRequired(),
                                Length(min=5)])
    product_description = TextAreaField('Product description',
                                         validators=[DataRequired(),
                                         Length(min=5)])
    product_current_quantity = IntegerField('Current quantity',
                                             validators=[InputRequired(),
                                             NumberRange(min=1, message=\
                                                        'The current quantity\
                                                         must be at least one.'\
                                                        )])
    product_reorder_level = IntegerField('Reorder level',
                                          validators=[InputRequired(),
                                          NumberRange(min=1, message=\
                                          'The reorder level\
                                           must be at least one.'\
                                         )])
    product_thumbnail_link = StringField('Thumbnail link',
                                          validators=[DataRequired(),
                                          Regexp(regex="^.*\.(jpe?g|png|)$",
                                                 message="Thumbnail links must\
                                                          have their extension\
                                                          types lower-case,\
                                                          e.g. '.png', '.jpg'\
                                                          or .jpeg are the only\
                                                          file-types supported\
                                                          at this moment in\
                                                          time."),
                                          Length(min=5)])
