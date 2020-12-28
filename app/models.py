from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import enum

class Account(enum.Enum):
    USER_ACCOUNT = 1
    STAFF_ACCOUNT = 2
    MANAGER_ACCOUNT = 3
    CONTROLLER_ACCOUNT = 4

class User(db.Model, UserMixin):
    username = db.Column(db.String(), primary_key=True, index=True)
    password = db.Column(db.String(), index=True, nullable=False)

    acc_type = Account.USER_ACCOUNT

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

class Staff(db.Model, UserMixin):
    username = db.Column(db.String(), primary_key=True, index=True)
    password = db.Column(db.String(), index=True, nullable=False)

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
    username = db.Column(db.String(), primary_key=True, index=True)
    password = db.Column(db.String(), index=True, nullable=False)

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
    username = db.Column(db.String(), primary_key=True, index=True)
    password = db.Column(db.String(), index=True, nullable=False)

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
