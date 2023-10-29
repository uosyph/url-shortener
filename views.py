from flask import abort, request, session, render_template, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from jwt import encode
from re import match
from uuid import uuid4
import datetime

from database import *
from shortener import *


@app.route("/register", methods=["GET", "POST"])
def register():
    logout()

    msg = ""
    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
        and "confirm-password" in request.form
    ):
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm-password"]

        user = User.query.filter_by(username=username).first()

        if len(username) < 3 or len(username) > 16:
            msg = "Username must be between 3 and 16 letters!"
        elif len(password) < 6 or len(password) > 28:
            msg = "Password must be between 6 and 28 letters!"
        elif confirm_password != password:
            msg = "Passwords don't match!"
        elif user:
            msg = "Account already exists!"
        elif not username or not password or not confirm_password:
            msg = "Please fill out the form!"
        elif not match(r"^[a-zA-Z0-9]+$", username):
            msg = "Username must contain only characters and numbers!"
        else:
            hashed_password = generate_password_hash(password)

            new_user = User(
                id=str(uuid4()),
                username=username,
                password=hashed_password,
            )
            db.session.add(new_user)
            db.session.commit()
            user = User.query.filter_by(username=username).first()
            session["loggedin"] = True
            session["id"] = user.id
            session["username"] = user.username
            msg = "You have successfully registered!"
            return redirect(url_for("index"))
    elif request.method == "POST":
        msg = "Please fill out the form!"

    return render_template("register.html", msg=msg)


@app.route("/login", methods=["GET", "POST"])
def login():
    logout()

    msg = ""
    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
    ):
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if not user:
            msg = "Account doesn't exists!"
        elif not username or not password:
            msg = "Please fill out the form!"
        elif user:
            if check_password_hash(user.password, password):
                session["loggedin"] = True
                session["id"] = user.id
                session["username"] = user.username
                msg = "Logged in successfully!"
                return redirect(url_for("index"))
            else:
                msg = "Wrong password!"

    elif request.method == "POST":
        msg = "Please fill out the form!"

    return render_template("login.html", msg=msg)


@app.route("/logout")
def logout():
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("username", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
