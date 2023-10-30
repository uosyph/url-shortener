from flask import request, jsonify
from functools import wraps
from jwt import decode
from re import match
import datetime

from database import *
from shortener import *


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "x-access-token" in request.headers:
            provided_token = request.headers["x-access-token"]
        else:
            return f(user=None, *args, **kwargs)

        try:
            token = decode(
                provided_token, app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            user = User.query.filter_by(id=token["id"]).first()
        except:
            return jsonify({"error": "Token is invalid!"}), 401

        return f(user, *args, **kwargs)

    return decorated


@app.route("/api/shorten", methods=["POST"])
@token_required
def api_shorten(user):
    try:
        data = request.get_json()
        if "url" not in data and user is not None:
            return (
                jsonify(
                    {
                        "error": "Missing JSON fields.",
                        "required_fields": "url:str",
                        "optional_fields": "exp_date:str(%d-%m-%Y.%H:%M), is_permanent:boolean",
                    }
                ),
                400,
            )
        elif "url" not in data and user is None:
            return jsonify({"error": "Missing required JSON field: url:str."}), 400
        elif len(data["url"]) == 0:
            return jsonify({"error": "URL is empty!"}), 400
        elif len(data["url"]) > 2048:
            return jsonify({"error": "URL too long!"}), 400
        elif len(data["url"]) < 6:
            return jsonify({"error": "URL already short!!!"}), 400
        elif not match(
            r"^((http|https)://)?([A-Za-z0-9]+(?:-[A-Za-z0-9]+)*\.)+[A-Za-z]{2,}$",
            data["url"],
        ):
            return jsonify({"error": "Doesn't look like a URL to me :|"}), 400
        elif user is None:
            short_url = Shortener().shorten_url(data["url"])
            return (
                jsonify({"massage": "Shortenend URL successfully!", "url": short_url}),
                200,
            )
        elif user is not None:
            if "is_permanent" in data and data["is_permanent"].title() not in [
                "True",
                "False",
            ]:
                return (
                    jsonify({"error": "'is_permanent' only accepts True or False."}),
                    400,
                )
            elif (
                "is_permanent" in data
                and "exp_date" in data
                and data["is_permanent"].title() == "True"
            ):
                return (
                    jsonify(
                        {
                            "error": "You can Not set an expiration date to a permanent URL."
                        }
                    ),
                    400,
                )
            elif "exp_date" in data:
                if Shortener().check_datetime_format(data["exp_date"]) is False:
                    return (
                        jsonify(
                            {
                                "error": "'exp_date' only accepts the '%d-%m-%Y.%H:%M' format."
                            }
                        ),
                        400,
                    )

                current_time = datetime.datetime.now()
                exp_date_min = datetime.datetime.strptime(
                    (current_time + datetime.timedelta(minutes=5)).strftime(
                        "%d-%m-%Y.%H:%M"
                    ),
                    "%d-%m-%Y.%H:%M",
                )
                exp_date_max = datetime.datetime.strptime(
                    (current_time + datetime.timedelta(days=365 * 50)).strftime(
                        "%d-%m-%Y.%H:%M"
                    ),
                    "%d-%m-%Y.%H:%M",
                )
                exp_date = datetime.datetime.strptime(
                    data["exp_date"],
                    "%d-%m-%Y.%H:%M",
                )

                if exp_date < exp_date_min or exp_date > exp_date_max:
                    return (
                        jsonify(
                            {
                                "error": "Expiration date must be between 5 minutes from now to 50 years in the future"
                            }
                        ),
                        400,
                    )
                else:
                    short_url = Shortener().shorten_url(
                        data["url"],
                        expiration_date=exp_date.strftime("%d-%m-%Y.%H:%M"),
                        user_id=user.id,
                    )
                    return (
                        jsonify(
                            {
                                "massage": "Shortenend URL successfully!",
                                "url": short_url,
                            }
                        ),
                        200,
                    )
            else:
                short_url = Shortener().shorten_url(data["url"], user_id=user.id)
                return (
                    jsonify(
                        {"massage": "Shortenend URL successfully!", "url": short_url}
                    ),
                    200,
                )
    except:
        return jsonify({"error": "No JSON data provided."}), 400


@app.route("/api/get", methods=["GET"])
@token_required
def api_get(user):
    if user is None:
        return jsonify({"error": "Token is missing!"}), 401

    try:
        data = request.get_json()
        if "url" in data:
            if len(data["url"]) == 0:
                return jsonify({"error": "URL is empty!"}), 400
            elif len(data["url"]) > 12:
                return jsonify({"error": "Well that's not a so short, ain't!"}), 400
            elif len(data["url"]) < 4:
                return jsonify({"error": "Oh, now it's too short :|"}), 400
            else:
                url = Url.query.filter_by(
                    short_url=data["url"], user_id=user.id
                ).first()
                if url is not None:
                    return (
                        jsonify(
                            {
                                "short_url": url.short_url,
                                "long_url": url.long_url,
                                "creation_date": url.creation_date,
                                "expiration_date": url.expiration_date,
                                "is_permanent": url.is_permanent,
                            }
                        ),
                        200,
                    )
                else:
                    return jsonify({"error": "URL doesn't exist."})
    except:
        urls = db.session.query(Url).where(Url.user_id == user.id)
        if urls.count() <= 0:
            return jsonify({"massage": "You don't have any URLs"}), 200
        elif urls.count() > 0:
            json_urls = []
            for url in urls:
                json_url = {
                    "short_url": url.short_url,
                    "long_url": url.long_url,
                    "creation_date": url.creation_date,
                    "expiration_date": url.expiration_date,
                    "is_permanent": url.is_permanent,
                }
                json_urls.append(json_url)

            return jsonify(json_urls), 200
        else:
            return (
                jsonify(
                    {
                        "error": "Error occurred.",
                        "usage": "Run without anything to get all URLs, or to get particular url info Use the JSON field: url:str.",
                    }
                ),
                400,
            )


@app.route("/api/update", methods=["PUT"])
@token_required
def api_update(user):
    if user is None:
        return jsonify({"error": "Token is missing!"}), 401

    return


@app.route("/api/delete", methods=["DELETE"])
@token_required
def api_delete(user):
    if user is None:
        return jsonify({"error": "Token is missing!"}), 401

    return


@app.route("/api/stats", methods=["GET"])
@token_required
def api_stats(user):
    if user is None:
        return jsonify({"error": "Token is missing!"}), 401

    return


if __name__ == "__main__":
    app.run(debug=True)
