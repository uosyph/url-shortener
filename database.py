from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import getcwd

app = Flask(__name__)
app.url_map.strict_slashes = False


cwd = getcwd()

app.config["SECRET_KEY"] = "thisissecret"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{cwd}/shorten.db"

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(36), primary_key=True)
    username = db.Column(db.String(16), unique=True)
    password = db.Column(db.String(255))
    token = db.Column(db.String(255), unique=True)


class Url(db.Model):
    __tablename__ = "urls"
    short_url = db.Column(db.String(16), primary_key=True)
    long_url = db.Column(db.String(2048))
    creation_date = db.Column(db.String(16))
    expiration_date = db.Column(db.String(16))
    is_permanent = db.Column(db.Boolean)
    user_id = db.Column(db.String(36))


class Stat(db.Model):
    __tablename__ = "stats"
    id = db.Column(db.Integer, primary_key=True)
    short_url = db.Column(db.String(16))
    entry_time = db.Column(db.String(19))
    response_time = db.Column(db.String(6))
    platform = db.Column(db.String(64))
    browser = db.Column(db.String(64))
    ip = db.Column(db.String(39))
    city = db.Column(db.String(56))
    region = db.Column(db.String(56))
    country = db.Column(db.String(56))
    latitude = db.Column(db.String(22))
    longitude = db.Column(db.String(22))
    distance = db.Column(db.String(22))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
