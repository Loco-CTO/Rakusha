import os

from flask import Blueprint, abort, redirect, send_from_directory, url_for

storage_bp = Blueprint("storage", __name__)
uploads_folder = "uploads"


from flask import flash, render_template, request
from werkzeug.security import check_password_hash

from database import db_handler


@storage_bp.route("/<filename>", methods=["GET", "POST"])
def storage(filename):
    file_path = os.path.join(uploads_folder, filename)
    if not os.path.exists(file_path):
        abort(404)

    file_info = db_handler.execute(
        "SELECT password_hash FROM uploads WHERE filename = ?",
        (filename,),
    )[0]

    if file_info[0]:
        password = request.args.get("password")
        if password and check_password_hash(file_info[0], password):
            return send_from_directory(uploads_folder, filename)
        if request.method == "POST":
            password = request.form.get("password")
            if check_password_hash(file_info[0], password):
                return redirect(
                    url_for("storage.storage", filename=filename, password=password)
                )
            else:
                flash("Incorrect password.", "error")
        return render_template("password_view.html", filename=filename)

    return send_from_directory(uploads_folder, filename)
