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
        if "token" in request.headers:
            provided_token = request.headers["token"]
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
    if user is None:
        return jsonify({"message": "Store token normally"})

    return jsonify({"message": "Store token with user id", "user": user.username})


@app.route("/api/get", methods=["GET"])
@token_required
def api_get(user):
    if user is None:
        return jsonify({"error": "Token is missing!"}), 401

    return


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
