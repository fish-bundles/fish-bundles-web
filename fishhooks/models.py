from fishhooks.app import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True)
    name = db.Column(db.String(200), unique=True)
    email = db.Column(db.String(255), unique=True)
    location = db.Column(db.String(1200))
