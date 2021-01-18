from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField\
                    ,IntegerField, DecimalField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, EqualTo, Length, NumberRange\
                               ,Regexp, InputRequired, ValidationError

class ReceiptForm(FlaskForm):
    receipt = BooleanField('Would you like a digital receipt?')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me?')

class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(),
                            Length(min=5)])
    email = EmailField('Email', validators=[DataRequired(), Length(min=7,
                                                                   max=255)])
    password = PasswordField('New password', validators=[DataRequired(),
                              EqualTo('confirmed_password',
                              message='Passwords must match.'),
                              Length(min=5)])
    confirmed_password = PasswordField('Confirm password',
                                        validators=[DataRequired()])

class AddStaffForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(),
                            Length(min=5)])
    password = PasswordField('New password', validators=[DataRequired(),
                              EqualTo('confirmed_password',
                              message='Passwords must match.'),
                              Length(min=5)])
    confirmed_password = PasswordField('Confirm password',
                                        validators=[DataRequired()])

class ChangeMyPasswordForm(FlaskForm):
    password = PasswordField('New password', validators=[DataRequired(),
                              EqualTo('confirmed_password',
                              message='Passwords must match.'),
                              Length(min=5)])
    confirmed_password = PasswordField('Confirm password',
                                        validators=[DataRequired()])

class AddProductsForm(FlaskForm):
    product_name = StringField('Product name', validators=[DataRequired(),
                                Length(min=5)])
    product_description = TextAreaField('Product description',
                                         validators=[DataRequired(),
                                         Length(min=5)])
    product_price = StringField('Produce price', validators=[InputRequired(),
                                 Regexp(regex="^\d*[0-9](?:\.[0-9]{1,2})?$",
                                        message="Product price must be \
                                                 formatted using one or two\
                                                 decimal places if a decimal\
                                                 was provided. If so, there \
                                                 must be a leading value prior\
                                                 to the decimal point. Also,\
                                                 please do not include any\
                                                 currency symbols.")])
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

    def validate_product_price(form, field):
        try:
            val = float(str(field.data))
            if val < 1 or val > 20:
                raise ValidationError('Price must be between £1.00 - £20.00.')
        except:
            raise ValidationError('Price must be between £1.00 - £20.00.')

class QuantityForm(FlaskForm):
    product_id = IntegerField('Product Id')
    quantity = IntegerField('Quantity', validators=[InputRequired()])
