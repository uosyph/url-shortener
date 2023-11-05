from flask import request, jsonify
from functools import wraps
from jwt import decode
from re import match
import datetime

from database import *
from shortener import *
from analyzer import *


analyzer = Analyzer()


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
            elif (
                "exp_date" not in data
                and "is_permanent" in data
                and data["is_permanent"].title() == "True"
            ):
                short_url = Shortener().shorten_url(
                    data["url"],
                    is_permanent=True,
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
                    return jsonify({"url": url.long_url}), 200
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

    try:
        data = request.get_json()
        if "url" not in data:
            return jsonify({"error": "Missing required JSON field: url:str."}), 400
        elif len(data["url"]) == 0:
            return jsonify({"error": "URL is empty!"}), 400
        elif len(data["url"]) > 12:
            return jsonify({"error": "Well that's not a so short, ain't!"}), 400
        elif len(data["url"]) < 4:
            return jsonify({"error": "Oh, now it's too short :|"}), 400

        url = Url.query.filter_by(short_url=data["url"], user_id=user.id).first()
        if url is None:
            return jsonify({"error": "URL doesn't exist."})

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
            and "exp_date" not in data
            and data["is_permanent"].title() == "False"
        ):
            return (
                jsonify(
                    {
                        "error": "If you set is_permanent to False you have to provide an exp date."
                    }
                ),
                400,
            )
        elif (
            "is_permanent" in data
            and "exp_date" in data
            and data["is_permanent"].title() == "True"
        ):
            return (
                jsonify(
                    {"error": "You can Not set an expiration date to a permanent URL."}
                ),
                400,
            )
        elif (
            "exp_date" not in data
            and "is_permanent" in data
            and data["is_permanent"].title() == "True"
        ):
            url.is_permanent = True
            url.expiration_date = None
            db.session.commit()
            return jsonify({"massage": "Updated URL successfully!"}), 200
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
                url.is_permanent = False
                url.expiration_date = exp_date.strftime("%d-%m-%Y.%H:%M")
                db.session.commit()
                return jsonify({"massage": "Updated URL successfully!"}), 200
    except:
        return jsonify({"error": "No JSON data provided."}), 400


@app.route("/api/delete", methods=["DELETE"])
@token_required
def api_delete(user):
    if user is None:
        return jsonify({"error": "Token is missing!"}), 401

    try:
        data = request.get_json()
        if "url" not in data:
            return jsonify({"error": "Missing required JSON field: url:str."}), 400
        elif len(data["url"]) == 0:
            return jsonify({"error": "URL is empty!"}), 400
        elif len(data["url"]) > 12:
            return jsonify({"error": "Well that's not a so short, ain't!"}), 400
        elif len(data["url"]) < 4:
            return jsonify({"error": "Oh, now it's too short :|"}), 400

        url = Url.query.filter_by(short_url=data["url"], user_id=user.id).first()
        if url is None:
            return jsonify({"error": "URL doesn't exist."})

        analyzer.short_url = url.short_url
        analyzer.delete()
        db.session.delete(url)
        db.session.commit()
        return jsonify({"massage": "Deleted URL successfully!"}), 200
    except:
        return jsonify({"error": "No JSON data provided."}), 400


@app.route("/api/stats", methods=["GET"])
@token_required
def api_stats(user):
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
                    analyzer.short_url = url.short_url
                    stats = analyzer.analyze()
                    return (
                        jsonify(
                            {
                                "short_url": url.short_url,
                                "long_url": url.long_url,
                                "creation_date": url.creation_date,
                                "expiration_date": url.expiration_date,
                                "is_permanent": url.is_permanent,
                                "entries": stats["entries"],
                                "total_entries_count": stats["total_entries_count"],
                                "total_unique_entries_count": stats[
                                    "total_unique_entries_count"
                                ],
                                "most_frequent_entry_time_of_day": stats[
                                    "most_frequent_entry_time_of_day"
                                ],
                                "most_frequent_entry_time_of_month": stats[
                                    "most_frequent_entry_time_of_month"
                                ],
                                "most_frequent_entry_time_of_year": stats[
                                    "most_frequent_entry_time_of_year"
                                ],
                                "average_response_time": stats["average_response_time"],
                                "top_platforms": stats["top_platforms"],
                                "top_browsers": stats["top_browsers"],
                                "top_countries": stats["top_countries"],
                                "top_regions": stats["top_regions"],
                                "top_cities": stats["top_cities"],
                                "average_distance": stats["average_distance"],
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
                analyzer.short_url = url.short_url
                stats = analyzer.analyze()
                json_url = {
                    "short_url": url.short_url,
                    "long_url": url.long_url,
                    "creation_date": url.creation_date,
                    "expiration_date": url.expiration_date,
                    "is_permanent": url.is_permanent,
                    "entries": stats["entries"],
                    "total_entries_count": stats["total_entries_count"],
                    "total_unique_entries_count": stats["total_unique_entries_count"],
                    "most_frequent_entry_time_of_day": stats[
                        "most_frequent_entry_time_of_day"
                    ],
                    "most_frequent_entry_time_of_month": stats[
                        "most_frequent_entry_time_of_month"
                    ],
                    "most_frequent_entry_time_of_year": stats[
                        "most_frequent_entry_time_of_year"
                    ],
                    "average_response_time": stats["average_response_time"],
                    "top_platforms": stats["top_platforms"],
                    "top_browsers": stats["top_browsers"],
                    "top_countries": stats["top_countries"],
                    "top_regions": stats["top_regions"],
                    "top_cities": stats["top_cities"],
                    "average_distance": stats["average_distance"],
                }
                json_urls.append(json_url)

            return jsonify(json_urls), 200
        else:
            return (
                jsonify(
                    {
                        "error": "Error occurred.",
                        "usage": "Run without anything to get stats for all URLs, or to get stats for particular url info Use the JSON field: url:str.",
                    }
                ),
                400,
            )


if __name__ == "__main__":
    app.run(debug=True)
