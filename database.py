"""
Database Module

This module defines the database structure and configurations for the URL shortening service.
It uses SQLAlchemy to create and manage tables for users, URLs, and statistics.

Classes:
    - User: The model representing user data in the database.
    - Url: The model representing URL data in the database.
    - Stat: The model representing statistics data in the database.

Author: Yousef Saeed
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import getcwd, getenv
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.url_map.strict_slashes = False


cwd = getcwd()

app.config["SECRET_KEY"] = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{cwd}/{getenv('DB')}.db"

db = SQLAlchemy(app)


class User(db.Model):
    """
    User model for storing user data in the database.

    Attributes:
        id (str): Unique user identifier.
        username (str): User's username.
        password (str): User's hashed password.
        token (str): User's authentication token.
    """

    __tablename__ = "users"
    id = db.Column(db.String(36), primary_key=True)
    username = db.Column(db.String(16), unique=True)
    password = db.Column(db.String(255))
    token = db.Column(db.String(255), unique=True)


class Url(db.Model):
    """
    Url model for storing URL data in the database.

    Attributes:
        short_url (str): Shortened URL identifier.
        long_url (str): Original long URL.
        creation_date (str): Date and time when the URL was created.
        expiration_date (str): Date and time when the URL expires (if applicable).
        is_permanent (bool): Indicates whether the URL is permanent.
        user_id (str): User identifier associated with the URL.
    """

    __tablename__ = "urls"
    short_url = db.Column(db.String(16), primary_key=True)
    long_url = db.Column(db.String(2048))
    creation_date = db.Column(db.String(19))
    expiration_date = db.Column(db.String(16))
    is_permanent = db.Column(db.Boolean)
    user_id = db.Column(db.String(36))


class Stat(db.Model):
    """
    Stat model for storing statistics data in the database.

    Attributes:
        id (int): Unique statistics entry identifier.
        short_url (str): Shortened URL identifier.
        entry_time (str): Date and time of user entry.
        response_time (str): Response time of the server.
        platform (str): User's platform (OS).
        browser (str): User's browser and version.
        ip (str): User's IP address.
        city (str): User's city.
        region (str): User's region.
        country (str): User's country.
        latitude (str): User's latitude.
        longitude (str): User's longitude.
        distance (str): Distance between the client and server.
    """

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
