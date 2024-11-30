from flask import Blueprint, send_from_directory

storage_bp = Blueprint("storage", __name__)
uploads_folder = "uploads"


@storage_bp.route("/<filename>")
def storage(filename):
    return send_from_directory(uploads_folder, filename)
