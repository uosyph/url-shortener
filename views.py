from flask import abort, request, session, render_template, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from jwt import encode
from re import match
from uuid import uuid4
import datetime

from database import *
from shortener import *


@app.route("/", methods=["GET", "POST"])
def index():
    msg = ""
    short_url = None
    current_time = datetime.datetime.now()
    exp_date_min = (current_time + datetime.timedelta(minutes=5)).strftime(
        "%Y-%m-%dT%H:%M"
    )
    exp_date_max = (current_time + datetime.timedelta(days=365 * 50)).strftime(
        "%Y-%m-%dT%H:%M"
    )

    if request.method == "POST" and "url" in request.form:
        long_url = request.form["url"]

        if len(long_url) > 2048:
            msg = "URL too long!"
        elif len(long_url) < 6:
            msg = "URL already short!!!"
        elif not match(
            r"^((http|https)://)?([A-Za-z0-9]+(?:-[A-Za-z0-9]+)*\.)+[A-Za-z]{2,}$",
            long_url,
        ):
            msg = "Doesn't look like a URL to me :|"
        else:
            if "loggedin" in session and session["loggedin"]:
                if "is_permanent" in request.form:
                    short_url = Shortener().shorten_url(
                        long_url, is_permanent=True, user_id=session["id"]
                    )
                elif "exp_date" in request.form and request.form["exp_date"] != "":
                    exp_date = datetime.datetime.strptime(
                        Shortener().convert_datetime_format(request.form["exp_date"]),
                        "%d-%m-%Y.%H:%M",
                    )
                    exp_date_min_formatted = datetime.datetime.strptime(
                        Shortener().convert_datetime_format(exp_date_min),
                        "%d-%m-%Y.%H:%M",
                    )
                    exp_date_max_formatted = datetime.datetime.strptime(
                        Shortener().convert_datetime_format(exp_date_max),
                        "%d-%m-%Y.%H:%M",
                    )

                    if (
                        exp_date < exp_date_min_formatted
                        or exp_date > exp_date_max_formatted
                    ):
                        msg = "Expiration date must be between 5 minutes from now to 50 years in the future"
                    else:
                        short_url = Shortener().shorten_url(
                            long_url,
                            exp_date.strftime("%d-%m-%Y.%H:%M"),
                            user_id=session["id"],
                        )
                else:
                    short_url = Shortener().shorten_url(long_url, user_id=session["id"])
            else:
                short_url = Shortener().shorten_url(long_url)

    elif request.method == "POST":
        msg = "Please fill out the form!"

    return render_template(
        "index.html",
        msg=msg,
        short_url=short_url,
        exp_date_min=exp_date_min,
        exp_date_max=exp_date_max,
    )


@app.route("/<short_url>")
def redirect_url(short_url):
    url = Url.query.filter_by(short_url=short_url).first()
    if url is not None:
        if not match("^(http|https)://", url.long_url):
            return redirect(f"https://{url.long_url}")
        else:
            return redirect(url.long_url)
    else:
        abort(404)


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


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(401)
def unauthorized(e):
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)