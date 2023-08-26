from flask import request, redirect, url_for, jsonify
from flask_jwt_extended import get_jwt_identity, create_access_token, jwt_required
from datetime import datetime
from core.models import ShortUrls, Users
from core import app
from core import db
from helpers import generate_short_id, is_valid_email

# Link shortener for anonymous users


@app.route("/", methods=["POST"])
def index():
    url = request.json.get("url")

    if not url:
        # Url is required
        return jsonify({"message": "url is required"}), 400

    # Generate a random short_id
    short_id = generate_short_id(8)
    short_url = request.host_url + short_id

    # Check if a url already exists in the db.
    # If it exists, return its short_id and don't create a new one.
    original_url = ShortUrls.query.filter_by(original_url=url).first()
    if original_url is None:
        new_link = ShortUrls(
            original_url=url, short_id=short_id, short_url=short_url, created_at=datetime.utcnow())
        db.session.add(new_link)
        db.session.commit()
        short_url = request.host_url + short_id
    else:
        original_url_short_id = original_url.short_id
        short_url = request.host_url + original_url_short_id
    return jsonify({"short_url": short_url}), 201

# Redirect to original_url endpoint


@app.route("/<short_id>")
def redirect_url(short_id):
    """Redirect to the original link"""
    link = ShortUrls.query.filter_by(short_id=short_id).first()
    if link:
        return redirect(link.original_url)

    return redirect(url_for("index"))

# auth endpoint - login


@app.route("/login", methods=["POST"])
def login():
    """Login route"""
    email = request.json.get("email").lower().strip()
    password = request.json.get("password")

    # Check if email or password is missing
    if not email:
        return jsonify({"message": "Please enter your email"}), 400
    if not password:
        return jsonify({"message": "Please enter your password"}), 400

    # Check if email is valid
    if not is_valid_email(email):
        return jsonify({"message": "Email is not valid"}), 400

    user = Users.query.filter_by(email=email).first()

    # If the user is not found or the password is incorrect
    if not user:
        return jsonify({"message": "Invalid email"}), 401
    if not user.verify_password(password):
        return jsonify({"message": "Invalid password"}), 401
    access_token = create_access_token(identity=email)

    return jsonify({"message": "User logged in successfully", "token": access_token, "username": user.username, "email": email}), 200

# auth endpoint - register


@app.route("/register", methods=["POST"])
def register():
    """Registration route"""
    username = request.json.get("username")
    email = request.json.get("email")
    password = request.json.get("password")

    # Check if username, email, or password is missing
    if not username:
        return jsonify({"message": "Please enter your username"}), 400
    if not email:
        return jsonify({"message": "Please enter your email"}), 400
    if not password:
        return jsonify({"message": "Please enter your password"}), 400

    # Normalize and strip fields
    username = username.lower().strip()
    username = username.replace(" ", "")
    email = email.lower().strip()

    # Check if email is valid
    if not is_valid_email(email):
        return jsonify({"message": "Email is not valid"}), 400

    # Check if username or email already exists in the db
    username_exists = Users.query.filter_by(username=username).first()
    email_exists = Users.query.filter_by(email=email).first()

    if username_exists:
        return jsonify({"message": "Username already exists"}), 409
    if email_exists:
        return jsonify({"message": "Email already exists"}), 409

    db.session.add(Users(username=username, email=email, password=password))
    db.session.commit()
    access_token = create_access_token(identity=email)
    return jsonify({"message": "User registered successfully", "token": access_token, "username": username, "email": email}), 201

# Link shortener endpoint for logged in users


@app.route("/<username>", methods=["POST"])
@jwt_required()
def logged_in_user(username):
    """Link-shortener endpoint for logged in users"""
    url = request.json.get("url")
    short_id = request.json.get("custom_id")

    current_user_email = get_jwt_identity()
    current_user = Users.query.filter_by(email=current_user_email).first()

    if not current_user:
        return jsonify({"message": "User not found"}), 404

    # Ensure the username from the route matches the logged-in user's username
    if current_user.username != username:
        return jsonify({"message": "Access denied"}), 403

    if not url:
        # Url is required
        return jsonify({"message": "url is required"}), 400

    if short_id and ShortUrls.query.filter_by(short_id=short_id).first() is not None:
        # Please enter a different custom id
        return jsonify({"message": "Please, enter a different custom id"}), 400

    if not short_id:
        short_id = generate_short_id(8)
    short_url = request.host_url + short_id

    # Check if a url already exists in the db for this user
    # If it exists, return its short_id and don't create a new one.
    original_url = ShortUrls.query.filter_by(
        original_url=url, user_id=current_user.id).first()

    if original_url is None:
        new_link = ShortUrls(original_url=url, short_id=short_id,
                             user=current_user, short_url=short_url, created_at=datetime.utcnow())
        db.session.add(new_link)
        db.session.commit()
        return jsonify({"short_url": short_url}), 201
    else:
        original_url_short_url = original_url.short_url

    return jsonify({"short_url": original_url_short_url}), 201


# dashboard of all created links for logged in users

@app.route("/<username>/dashboard", methods=["GET"])
@jwt_required()
def dashboard(username):
    """Returns a list of all shortened urls by a user"""
    current_user_email = get_jwt_identity()
    current_user = Users.query.filter_by(email=current_user_email).first()

    if not current_user:
        return jsonify({"message": "User not found"}), 404

    if username == current_user.username:
        # Convert each ShortUrls object to a dictionary
        urls = [url.to_dict() for url in current_user.urls]
        return jsonify({"shortened_urls": urls}), 200

    return jsonify({"message": "Invalid username"})


# Reset password endpoint for logged in users


@app.route("/resetpassword", methods=["POST"])
@jwt_required()
def reset_password():
    """Resets user's password"""
    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")

    # Get the user from the token's identity claim
    current_user_email = get_jwt_identity()
    user = Users.query.filter_by(email=current_user_email).first()

    if not user:
        return jsonify({"message": "User does not exist"}), 404

    if not old_password or not new_password:
        return jsonify({"message": "Old password and new password are required"}), 400

    if not user.verify_password(old_password):
        return jsonify({"message": "Invalid old password"}), 401

    # Update the password
    user.password = new_password
    db.session.commit()

    return jsonify({"message": "Password changed successfully"}), 200
