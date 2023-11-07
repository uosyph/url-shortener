"""
URL Shortener Web Application

This web application provides a URL shortening service that allows users to generate short URLs for long web addresses.
It includes functionality for creating, managing, and resolving short URLs.
The short URLs can have optional expiration dates, and users can register and log in to manage their URLs.

Author: Yousef Saeed
"""

from flask import abort, request, session, render_template, redirect, url_for
from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash
from jwt import encode
from re import match
from uuid import uuid4
from functools import wraps
from pycountry import countries
from humanize.time import precisedelta
from calendar import month_name
from time import time
import datetime

from database import *
from shortener import *
from analyzer import *


analyzer = Analyzer()


def measure_response_time(f):
    """
    Redirect to the original URL associated with a short URL.

    Args:
        short_url (str): The short URL to resolve.

    Returns:
        redirect: Redirects to the original URL if found, or a 404 error if not found.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        start_time = time()
        response = f(*args, **kwargs)
        total_elapsed_time = time() - start_time
        analyzer.response_time = total_elapsed_time
        return response

    return wrapper


@app.before_request
def clear_trailing():
    """
    Remove trailing slashes from URL paths before processing.

    If a URL path ends with a '/', this function redirects to the same URL without the trailing '/'.

    Returns:
        redirect: A redirect to the URL without the trailing slash.
    """

    rp = request.path
    if rp != "/" and rp.endswith("/"):
        return redirect(rp[:-1])


@app.route("/<short_url>")
@measure_response_time
def redirect_url(short_url):
    """
    Decorator to measure the response time of a view function.

    Args:
        f (function): The view function to be measured.

    Returns:
        function: The wrapped view function.
    """

    url = Url.query.filter_by(short_url=short_url).first()
    if url is not None:
        analyzer.short_url = short_url
        analyzer.user_agent = request.headers.get("User-Agent")
        analyzer.track()
        if not match("^(http|https)://", url.long_url):
            return redirect(f"https://{url.long_url}")
        else:
            return redirect(url.long_url)
    else:
        abort(404)


@app.route("/", methods=["GET", "POST"])
def index():
    """
    Display the main index page with URL shortening functionality.

    Handles the URL shortening form, user registration, and login.

    Returns:
        render_template: Renders the index.html template with relevant data.
    """

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
            msg = (
                "Ooh, that URL is a bit too long for us. Try shortening it a bit, yeah?"
            )
        elif len(long_url) < 6:
            msg = (
                "That URL is already pretty short! Any shorter and it might disappear!"
            )
        elif not match(
            r"^((http|https)://)?([A-Za-z0-9]+(?:-[A-Za-z0-9]+)*\.)+[A-Za-z]{2,}$",
            long_url,
        ):
            msg = "Hmm, that doesn't look like a valid URL to us. Can you double-check it?"
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
                        msg = "Uh oh, your link's expiration date needs to be between 5 minutes and 50 years from now. Can you fix that and try again?"
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
        msg = "Hey there! It looks like you forgot to fill out the form. Could you please give that another go?"

    return render_template(
        "index.html",
        msg=msg,
        short_url=short_url,
        exp_date_min=exp_date_min,
        exp_date_max=exp_date_max,
    )


@app.route("/unshorten", methods=["GET", "POST"])
def unshorten():
    """
    Display the unshorten page to expand a short URL into its original form.

    Returns:
        render_template: Renders the unshorten.html template with relevant data.
    """

    msg = ""
    long_url = None

    if request.method == "POST" and "url" in request.form:
        short_url = request.form["url"].split("/")[-1]
        url = Url.query.filter_by(short_url=short_url).first()
        if url is not None:
            long_url = url.long_url
        else:
            msg = "Uh-oh, that URL doesn't seem to exist. It might have been deleted or expired."
    elif request.method == "POST":
        msg = "Hey there, you need to give me a URL to unshorten! Otherwise, I'm just sitting here twiddling my thumbs."

    return render_template(
        "unshorten.html",
        msg=msg,
        long_url=long_url,
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Handle user registration and account creation.

    Returns:
        render_template: Renders the register.html template with relevant data.
    """

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
            msg = "Your username needs to be between 3 and 16 letters long."
        elif len(password) < 6 or len(password) > 28:
            msg = "Your password needs to be between 6 and 28 letters long."
        elif confirm_password != password:
            msg = "Your passwords don't match! Try typing them again."
        elif user:
            msg = "That username is already taken. Try a different one?"
        elif not username or not password or not confirm_password:
            msg = "It looks like you forgot to fill out a few fields."
        elif not match(r"^[a-zA-Z0-9]+$", username):
            msg = "Your username can only contain letters and numbers. Try a different one?"
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
            msg = "Welcome to the club! 🥳 Your account has been successfully created."
            return redirect(url_for("index"))
    elif request.method == "POST":
        msg = "Hey there! Can you please fill out the form before you continue? We need a little bit of info from you so we can create your account."

    return render_template("register.html", msg=msg)


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Handle user login and session creation.

    Returns:
        render_template: Renders the login.html template with relevant data.
    """

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
            msg = "Account not found! 🕵️‍♂️"
        elif not username or not password:
            msg = "Please fill out the form, friend!"
        elif user:
            if check_password_hash(user.password, password):
                session["loggedin"] = True
                session["id"] = user.id
                session["username"] = user.username
                msg = "Welcome back, buddy! 🎉 You're logged in."
                return redirect(url_for("index"))
            else:
                msg = "Wrong password! Try again?"

    elif request.method == "POST":
        msg = "Please fill out the form, my dude!"

    return render_template("login.html", msg=msg)


@app.route("/logout")
def logout():
    """
    Log out the current user and clear their session.

    Returns:
        redirect: Redirects to the index page after logging out.
    """

    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("username", None)
    return redirect(url_for("index"))


@app.route("/account", methods=["GET", "POST"])
def account():
    """
    Display the user account page and manage user account settings.

    Returns:
        render_template: Renders the account.html template with relevant data.
    """

    if "loggedin" in session and session["loggedin"]:
        msg = ""
        tab = "profile"
        user_token = User.query.filter_by(id=session["id"]).first().token

        if (
            request.method == "POST"
            and "new-username" in request.form
            and request.form["action"] == "update_username"
        ):
            username = request.form["new-username"]
            user = User.query.filter_by(username=username).first()
            current_user = User.query.filter_by(id=session["id"]).first()

            if len(username) < 3 or len(username) > 16:
                msg = "Your username must be between 3 and 16 letters. Try again?"
            elif not user:
                current_user.username = username
                db.session.commit()
                session["username"] = current_user.username
                msg = "Your username has been successfully updated! 🥳"
            else:
                if username == current_user.username:
                    msg = "You can't change your username to the same one you already have. 🙄"
                else:
                    msg = "That username is not available. Try a different one."
            tab = "profile"
        elif (
            request.method == "POST"
            and "old-password" in request.form
            and "new-password" in request.form
            and "confirm-new-password" in request.form
            and request.form["action"] == "update_password"
        ):
            old_password = request.form["old-password"]
            new_password = request.form["new-password"]
            confirm_new_password = request.form["confirm-new-password"]

            user = User.query.filter_by(id=session["id"]).first()

            if check_password_hash(user.password, old_password):
                if len(new_password) < 6 or len(new_password) > 28:
                    msg = "Your password must be between 6 and 28 letters. Try again?"
                elif confirm_new_password != new_password:
                    msg = "Your passwords don't match. Try again."
                elif new_password == old_password:
                    msg = "You can't change your password to the same one you already have. 🤦‍♂️"
                else:
                    hashed_password = generate_password_hash(new_password)
                    user.password = hashed_password
                    db.session.commit()
                    msg = "Your password has been successfully updated! 🥳"
            else:
                msg = "Your password is wrong. Try again?"
            tab = "security"
        elif request.method == "POST" and request.form["action"] == "gen_token":
            user = User.query.filter_by(id=session["id"]).first()
            token = encode(
                {"id": user.id},
                app.config["SECRET_KEY"],
            )
            user.token = token
            db.session.commit()
            user_token = token
            msg = "Token generated successfully! 🪄"
            tab = "authn"
            return render_template(
                "account.html", msg=msg, tab=tab, user_token=user_token
            )
        elif request.method == "POST" and request.form["action"] == "del_token":
            user = User.query.filter_by(id=session["id"]).first()
            user.token = None
            db.session.commit()
            user_token = None
            msg = "Token deleted successfully!"
            tab = "authn"
            return render_template(
                "account.html", msg=msg, tab=tab, user_token=user_token
            )
        elif request.method == "POST" and request.form["action"] == "delete":
            user = User.query.filter_by(id=session["id"]).first()
            db.session.delete(user)
            db.session.commit()
            msg = "Your account is gone! 🪓 We hope you enjoyed your time with us."
            return logout()
        elif request.method == "POST":
            msg = "Hey there! Please fill out the form."

        return render_template("account.html", msg=msg, tab=tab, user_token=user_token)
    else:
        abort(401)


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    """
    Display the user dashboard for managing shortened URLs.

    Returns:
        render_template: Renders the dashboard.html template with relevant data.
    """

    if "loggedin" in session and session["loggedin"]:
        msg = ""
        current_time = datetime.datetime.now()
        exp_date_min = (current_time + datetime.timedelta(minutes=5)).strftime(
            "%Y-%m-%dT%H:%M"
        )
        exp_date_max = (current_time + datetime.timedelta(days=365 * 50)).strftime(
            "%Y-%m-%dT%H:%M"
        )

        urls = (
            db.session.query(Url)
            .where(Url.user_id == session["id"])
            .order_by(desc(Url.creation_date))
        )
        if urls.count() <= 0:
            return render_template("dashboard.html")

        if (
            request.method == "POST"
            and request.form["action"] == "save_url"
            and request.form["value"] != ""
        ):
            if "is_permanent" in request.form:
                url = Url.query.filter_by(
                    short_url=request.form["value"], user_id=session["id"]
                ).first()
                url.is_permanent = True
                url.expiration_date = None
                db.session.commit()
                msg = f'<span class="go-url" id="text-glow">{request.form["value"]}</span> is now permanent <span id="text-glow">∞ ✨</span>'
            elif "exp_date" in request.form and request.form["exp_date"] != "":
                url = Url.query.filter_by(
                    short_url=request.form["value"], user_id=session["id"]
                ).first()
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
                    msg = "The expiration date must be between 5 minutes from now and 50 years in the future."
                else:
                    url.is_permanent = False
                    url.expiration_date = exp_date.strftime("%d-%m-%Y.%H:%M")
                    db.session.commit()
                    msg = f'The expiration date for <span class="go-url" id="text-glow">{request.form["value"]}</span> has been set to <span id="text-glow">{exp_date.strftime("%d-%m-%Y.%H:%M")}</span>'
        elif (
            request.method == "POST"
            and request.form["action"] == "del_url"
            and request.form["value"] != ""
        ):
            url = Url.query.filter_by(
                short_url=request.form["value"], user_id=session["id"]
            ).first()
            analyzer.short_url = url.short_url
            analyzer.delete()
            db.session.delete(url)
            db.session.commit()
            msg = "Your URL has been deleted!"
            if urls.count() <= 0:
                return render_template("dashboard.html", msg=msg)

        return render_template(
            "dashboard.html",
            msg=msg,
            urls=urls,
            analyzer=analyzer,
            countries=countries,
            datetime=datetime,
            precisedelta=precisedelta,
            month_name=month_name,
            exp_date_min=exp_date_min,
            exp_date_max=exp_date_max,
        )
    else:
        abort(401)


@app.errorhandler(404)
def page_not_found(e):
    """
    Handle a 404 Page Not Found error.

    Args:
        e: The error object.

    Returns:
        render_template: Renders the 404.html template for a 404 error.
    """

    return render_template("404.html"), 404


@app.errorhandler(401)
def unauthorized(e):
    """
    Handle an unauthorized (401) error.

    Args:
        e: The error object.

    Returns:
        redirect: Redirects to the index page for an unauthorized user.
    """

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
