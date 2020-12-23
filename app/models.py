from app import db

class Staff(db.Model):
    username = db.Column(db.String(), primary_key=True, index=True)
    password = db.Column(db.String(), index=True, nullable=False)
