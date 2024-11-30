import datetime
import os
import random
import string

from flask import Blueprint, jsonify, request
from flask import url_for
from flask_login import current_user, login_required

from database import db_handler
from models.user import User
from .extensions import supported_extensions

upload_bp = Blueprint("upload", __name__)
storage_folder = "uploads"


def allowed_file(filename):
    if "." in filename:
        extension = filename.rsplit(".", 1)[1].lower()
        for category in supported_extensions.values():
            if extension in category:
                return True
    return False


def secure_string(length):
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))


def secure_filename(filename):
    filename = filename.strip()
    if "." in filename:
        name = secure_string(12)
        extension = filename.rsplit(".", 1)[1].lower()
        return f"{name}.{extension}"
    return filename


@upload_bp.route("/sharex", methods=["POST"])
def sharex():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        secret_key = request.form.get("secret_key")
        user = User.get_by_secret_key(secret_key)
        if not user:
            return jsonify({"error": "Invalid secret key"}), 403
        filename = secure_filename(file.filename)
        file.save(os.path.join(storage_folder, filename))
        file_size = os.path.getsize(os.path.join(storage_folder, filename))
        upload_time = datetime.datetime.now()
        db_handler.execute(
            "INSERT INTO uploads (original_name, filename, views, size, owner_identifier, upload_time) VALUES (?, ?, ?, ?, ?, ?)",
            (
                file.filename,
                filename,
                0,
                file_size,
                user.account_identifier,
                upload_time,
            ),
        )
        return jsonify({"url": url_for("view.view", filename=filename)}), 201
    return jsonify({"error": "File not allowed"}), 400


@upload_bp.route("/dashboard", methods=["POST"])
@login_required
def dashboard():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        user = current_user
        filename = secure_filename(file.filename)
        file.save(os.path.join(storage_folder, filename))
        file_size = os.path.getsize(os.path.join(storage_folder, filename))
        upload_time = datetime.datetime.now()
        db_handler.execute(
            "INSERT INTO uploads (original_name, filename, views, size, owner_identifier, upload_time) VALUES (?, ?, ?, ?, ?, ?)",
            (
                file.filename,
                filename,
                0,
                file_size,
                user.account_identifier,
                upload_time,
            ),
        )
        return jsonify({"url": url_for("view.view", filename=filename)}), 201
    return jsonify({"error": "File not allowed"}), 400
