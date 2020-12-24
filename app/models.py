from app import db
from flask_login import UserMixin

class Staff(db.Model):
    username = db.Column(db.String(), primary_key=True, index=True)
    password = db.Column(db.String(), index=True, nullable=False)

class Manager(db.Model, UserMixin):
    username = db.Column(db.String(), primary_key=True, index=True)
    password = db.Column(db.String(), index=True, nullable=False)

    def __init__(self, username, password, active=True):
        self.username = username
        self.password = password
        self.active = active

    def is_active(self):
        return self.active

    def get_id(self):
        return self.username

class Controller(db.Model, UserMixin):
    username = db.Column(db.String(), primary_key=True, index=True)
    password = db.Column(db.String(), index=True, nullable=False)

    def __init__(self, username, password, active=True):
        self.username = username
        self.password = password
        self.active = active

    def is_active(self):
        return self.active

    def get_id(self):
        return self.username
