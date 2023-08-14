from flask import request, redirect, url_for, jsonify
from datetime import datetime
from core.models import ShortUrls
from core import app
from core import db
from helpers import generate_short_id


@app.route("/", methods=["POST"])
def index():
    url = request.json.get("url")
    short_id = request.json.get("custom_id")

    if short_id and ShortUrls.query.filter_by(short_id=short_id).first() is not None:
        # Please enter a different custom id
        return jsonify({"message": "Please, enter a different custom id"}), 400
    if not url:
        # Url is required
        return jsonify({"message": "url is required"}), 400
    if not short_id:
        short_id = generate_short_id(8)

    # Check if a url already exists in the db.
    # If it exists, return it's short_id and don't create a new one.
    # If it doesn't exist, create a new one
    original_url = ShortUrls.query.filter_by(original_url=url).first()
    if original_url is None:
        new_link = ShortUrls(
            original_url=url, short_id=short_id, created_at=datetime.utcnow())
        db.session.add(new_link)
        db.session.commit()
        short_url = request.host_url + short_id
    else:
        original_url_short_id = original_url.short_id
        short_url = request.host_url + original_url_short_id
    return jsonify({"short_url": short_url}), 201


@app.route("/<short_id>")
def redirect_url(short_id):
    link = ShortUrls.query.filter_by(short_id=short_id).first()
    if link:
        return redirect(link.original_url)

    return redirect(url_for("index"))
