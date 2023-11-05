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
    def wrapper(*args, **kwargs):
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
            return jsonify({"error": "Token is invalid."}), 401

        return f(user, *args, **kwargs)

    return wrapper


@app.route("/api/shorten", methods=["POST"])
@token_required
def api_shorten(user):
    try:
        data = request.get_json()
        if "url" not in data and user is not None:
            return (
                jsonify(
                    {
                        "error": "Missing required parameter. url:str",
                        "optional_parameters": "exp_date:str(%d-%m-%Y.%H:%M), is_permanent:boolean",
                    }
                ),
                400,
            )
        elif "url" not in data and user is None:
            return jsonify({"error": "Missing required parameter. url:str."}), 400
        elif len(data["url"]) == 0:
            return jsonify({"error": "URL cannot be empty."}), 400
        elif len(data["url"]) > 2048:
            return (
                jsonify({"error": "URL must be less than 2048 characters long."}),
                400,
            )
        elif len(data["url"]) < 6:
            return jsonify({"error": "URL must be more than 6 characters long."}), 400
        elif not match(
            r"^((http|https)://)?([A-Za-z0-9]+(?:-[A-Za-z0-9]+)*\.)+[A-Za-z]{2,}$",
            data["url"],
        ):
            return jsonify({"error": "Invalid URL."}), 400
        elif user is None:
            short_url = Shortener().shorten_url(data["url"])
            return (
                jsonify({"message": "URL shortened successfully!", "url": short_url}),
                200,
            )
        elif user is not None:
            if "is_permanent" in data and data["is_permanent"].title() not in [
                "True",
                "False",
            ]:
                return (
                    jsonify(
                        {
                            "error": "'is_permanent' must be a boolean value (True or False)."
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
                        {"error": "Permanent URLs cannot have an expiration date."}
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
                            "message": "URL shortened successfully!",
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
                                "error": "Expiration date must be in the '%d-%m-%Y.%H:%M' format."
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
                                "error": "Expiration date must be between 5 minutes from now and 50 years in the future."
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
                                "message": "URL shortened successfully!",
                                "url": short_url,
                            }
                        ),
                        200,
                    )
            else:
                short_url = Shortener().shorten_url(data["url"], user_id=user.id)
                return (
                    jsonify(
                        {"message": "URL shortened successfully!", "url": short_url}
                    ),
                    200,
                )
    except:
        return jsonify({"error": "No data provided."}), 400


@app.route("/api/get", methods=["GET"])
@token_required
def api_get(user):
    if user is None:
        return jsonify({"error": "No token provided."}), 401

    try:
        data = request.get_json()
        if "url" in data:
            if len(data["url"]) == 0:
                return jsonify({"error": "URL cannot be empty."}), 400
            elif len(data["url"]) > 12:
                return jsonify({"error": "URL too long."}), 400
            elif len(data["url"]) < 4:
                return jsonify({"error": "URL too short."}), 400
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
            return jsonify({"message": "You have no URLs."}), 200
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
                        "error": "An error occurred.",
                        "usage": "Run without any arguments to get all URLs, or pass a URL in the JSON field url:str to get information about a specific URL.",
                    }
                ),
                400,
            )


@app.route("/api/update", methods=["PUT"])
@token_required
def api_update(user):
    if user is None:
        return jsonify({"error": "No token provided."}), 401

    try:
        data = request.get_json()
        if "url" not in data:
            return jsonify({"error": "Missing required parameter. url:str."}), 400
        elif len(data["url"]) == 0:
            return jsonify({"error": "URL cannot be empty."}), 400
        elif len(data["url"]) > 12:
            return jsonify({"error": "URL too long."}), 400
        elif len(data["url"]) < 4:
            return jsonify({"error": "URL too short."}), 400

        url = Url.query.filter_by(short_url=data["url"], user_id=user.id).first()
        if url is None:
            return jsonify({"error": "URL doesn't exist."})

        if "is_permanent" in data and data["is_permanent"].title() not in [
            "True",
            "False",
        ]:
            return (
                jsonify(
                    {"error": "'is_permanent' must be a boolean value (True or False)."}
                ),
                400,
            )
        elif (
            "is_permanent" in data
            and "exp_date" not in data
            and data["is_permanent"].title() == "False"
        ):
            return (
                jsonify({"error": "Expiration date required for non-permanent URLs."}),
                400,
            )
        elif (
            "is_permanent" in data
            and "exp_date" in data
            and data["is_permanent"].title() == "True"
        ):
            return (
                jsonify({"error": "Permanent URLs cannot have an expiration date."}),
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
            return jsonify({"message": "URL updated successfully!"}), 200
        elif "exp_date" in data:
            if Shortener().check_datetime_format(data["exp_date"]) is False:
                return (
                    jsonify(
                        {
                            "error": "Expiration date must be in the '%d-%m-%Y.%H:%M' format."
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
                            "error": "Expiration date must be between 5 minutes from now and 50 years in the future."
                        }
                    ),
                    400,
                )
            else:
                url.is_permanent = False
                url.expiration_date = exp_date.strftime("%d-%m-%Y.%H:%M")
                db.session.commit()
                return jsonify({"message": "URL updated successfully!"}), 200
    except:
        return jsonify({"error": "No data provided."}), 400


@app.route("/api/delete", methods=["DELETE"])
@token_required
def api_delete(user):
    if user is None:
        return jsonify({"error": "No token provided."}), 401

    try:
        data = request.get_json()
        if "url" not in data:
            return jsonify({"error": "Missing required parameter. url:str."}), 400
        elif len(data["url"]) == 0:
            return jsonify({"error": "URL cannot be empty."}), 400
        elif len(data["url"]) > 12:
            return jsonify({"error": "URL too long."}), 400
        elif len(data["url"]) < 4:
            return jsonify({"error": "URL too short."}), 400

        url = Url.query.filter_by(short_url=data["url"], user_id=user.id).first()
        if url is None:
            return jsonify({"error": "URL doesn't exist."})

        analyzer.short_url = url.short_url
        analyzer.delete()
        db.session.delete(url)
        db.session.commit()
        return jsonify({"message": "URL deleted successfully!"}), 200
    except:
        return jsonify({"error": "No data provided."}), 400


@app.route("/api/stats", methods=["GET"])
@token_required
def api_stats(user):
    if user is None:
        return jsonify({"error": "No token provided."}), 401

    try:
        data = request.get_json()
        if "url" in data:
            if len(data["url"]) == 0:
                return jsonify({"error": "URL cannot be empty."}), 400
            elif len(data["url"]) > 12:
                return jsonify({"error": "URL too long."}), 400
            elif len(data["url"]) < 4:
                return jsonify({"error": "URL too short."}), 400
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
            return jsonify({"message": "You have no URLs."}), 200
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
                        "usage": "Run without any arguments to get all URLs, or pass a URL in the JSON field url:str to get information about a specific URL.",
                    }
                ),
                400,
            )


if __name__ == "__main__":
    app.run(debug=True)
