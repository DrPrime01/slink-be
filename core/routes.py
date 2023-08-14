from flask import request, redirect, url_for, jsonify
from datetime import datetime
from core.models import ShortUrls
from core import app
from core import db
import secrets


def generate_short_id(chars_length: int):
    """Function to generate short_id of specified length of characters"""
    nbytes = (chars_length * 3) // 4
    return secrets.token_urlsafe(nbytes)[:chars_length]


@app.route("/", methods=["POST"])
def index():
    url = request.json.get("url")
    short_id = request.json.get("custom_id")

    if short_id and ShortUrls.query.filter_by(short_id=short_id).first() is not None:
        # Please enter a different custom id
        return jsonify({"message": "Please, enter a different custom id"})
    if not url:
        # Url is required
        return jsonify({"message": "url is required"})
    if not short_id:
        short_id = generate_short_id(8)

    new_link = ShortUrls(
        original_url=url, short_id=short_id, created_at=datetime.utcnow())
    db.session.add(new_link)
    db.session.commit()
    short_url = request.host_url + short_id
    return jsonify({"short_url": short_url}), 201


@app.route("/<short_id>")
def redirect_url(short_id):
    link = ShortUrls.query.filter_by(short_id=short_id).first()
    if link:
        return redirect(link.original_url)

    return redirect(url_for("index"))


@app.route("/name")
def name():
    return jsonify({"name": "John"})
