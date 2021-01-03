from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship, backref
import enum

class Account(enum.Enum):
    USER_ACCOUNT = 1
    STAFF_ACCOUNT = 2
    MANAGER_ACCOUNT = 3
    CONTROLLER_ACCOUNT = 4

class Product(db.Model):
    product_id = db.Column(db.Integer, primary_key=True, index=True)
    product_name = db.Column(db.String(255))
    product_description = db.Column(db.String(255))
    product_price = db.Column(db.Float)
    product_quantity = db.Column(db.Integer)
    product_reorder_level = db.Column(db.Integer)
    product_thumbnail_link = db.Column(db.String(255))
    product_thumbnail_type = db.Column(db.Integer)
    purchases = db.relationship('User', secondary='transaction_table')

    def __repr__(self):
        return str(self.product_id) + " " + str(self.product_name)

class User(db.Model, UserMixin):
    username = db.Column(db.String(255), primary_key=True, index=True)
    password = db.Column(db.String(255), index=True, nullable=False)
    email = db.Column(db.String(255), unique=True)
    products_bought = db.relationship('Product', secondary='transaction_table')

    acc_type = Account.USER_ACCOUNT

    def __init__(self, username, password, email, active=True):
        self.username = username
        self.password = generate_password_hash(password)
        self.email = email
        self.active = active

    def is_active(self):
        return self.active

    def get_id(self):
        return self.username

    def verify_password(self, pwd):
        return check_password_hash(self.password, pwd)

    def account_type(self):
        return self.acc_type

    def generate_new_password_hash(self, new_pass):
        return generate_password_hash(new_pass)

class Transaction(db.Model):
    __tablename__ = 'transaction_table'
    transaction_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'),
                           primary_key=True, index=True)
    user_id = db.Column(db.String(255), db.ForeignKey('user.username'),
                        primary_key=True, index=True)
    quantity = db.Column(db.Integer)
    sub_cost = db.Column(db.Integer)
    date = db.Column(db.DateTime)

    user = relationship(User, backref=backref("user_assoc"))
    product = relationship(Product, backref=backref("product_assoc"))

class Basket(db.Model):
    owner_id = db.Column(db.Integer, db.ForeignKey('user.username'),
                         primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'),
                           primary_key=True)
    product_name = db.Column(db.String(255))
    product_description = db.Column(db.String(255))
    product_price = db.Column(db.Float)
    product_thumbnail_type = db.Column(db.Integer)
    quantity = db.Column(db.Integer)

    def __repr__(self):
        return str(self.owner_id) + " " + str(self.product_id) + " "\
                   + str(self.quantity)

class Staff(db.Model, UserMixin):
    username = db.Column(db.String(255), primary_key=True, index=True)
    password = db.Column(db.String(255), index=True, nullable=False)

    acc_type = Account.STAFF_ACCOUNT

    def __init__(self, username, password, active=True):
        self.username = username
        self.password = generate_password_hash(password)
        self.active = active

    def is_active(self):
        return self.active

    def get_id(self):
        return self.username

    def verify_password(self, pwd):
        return check_password_hash(self.password, pwd)

    def account_type(self):
        return self.acc_type

    def generate_new_password_hash(self, new_pass):
        return generate_password_hash(new_pass)

class Manager(db.Model, UserMixin):
    username = db.Column(db.String(255), primary_key=True, index=True)
    password = db.Column(db.String(255), index=True, nullable=False)

    acc_type = Account.MANAGER_ACCOUNT

    def __init__(self, username, password, active=True):
        self.username = username
        self.password = generate_password_hash(password)
        self.active = active

    def is_active(self):
        return self.active

    def get_id(self):
        return self.username

    def verify_password(self, pwd):
        return check_password_hash(self.password, pwd)

    def account_type(self):
        return self.acc_type

    def generate_new_password_hash(self, new_pass):
        return generate_password_hash(new_pass)

class Controller(db.Model, UserMixin):
    username = db.Column(db.String(255), primary_key=True, index=True)
    password = db.Column(db.String(255), index=True, nullable=False)

    acc_type = Account.CONTROLLER_ACCOUNT

    def __init__(self, username, password, active=True):
        self.username = username
        self.password = generate_password_hash(password)
        self.active = active

    def is_active(self):
        return self.active

    def get_id(self):
        return self.username

    def verify_password(self, pwd):
        return check_password_hash(self.password, pwd)

    def account_type(self):
        return self.acc_type

    def generate_new_password_hash(self, new_pass):
        return generate_password_hash(new_pass)
