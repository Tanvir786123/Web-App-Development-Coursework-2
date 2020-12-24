from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    username = db.Column(db.String(), primary_key=True, index=True)
    password = db.Column(db.String(), index=True, nullable=False)

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

class Staff(db.Model, UserMixin):
    username = db.Column(db.String(), primary_key=True, index=True)
    password = db.Column(db.String(), index=True, nullable=False)

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

class Manager(db.Model, UserMixin):
    username = db.Column(db.String(), primary_key=True, index=True)
    password = db.Column(db.String(), index=True, nullable=False)

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

class Controller(db.Model, UserMixin):
    username = db.Column(db.String(), primary_key=True, index=True)
    password = db.Column(db.String(), index=True, nullable=False)

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
