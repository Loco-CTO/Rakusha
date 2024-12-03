import os

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from werkzeug.security import check_password_hash

from database import db_handler
from models.page_title import build_title

from .extensions import supported_extensions

view_bp = Blueprint("view", __name__)
uploads_folder = "uploads"
from werkzeug.utils import secure_filename


@view_bp.route("/<filename>", methods=["GET", "POST"])
def view(filename):
    filename = secure_filename(filename)
    file_path = os.path.join(uploads_folder, filename)
    password = None

    if not os.path.exists(os.path.abspath(uploads_folder)):
        abort(404)

    file_info = db_handler.execute(
        "SELECT password_hash FROM uploads WHERE filename = ?",
        (filename,),
    )[0]

    if file_info[0]:
        if request.method == "POST":
            password = request.form.get("password")
            if check_password_hash(file_info[0], password):
                return render_file_view(filename, file_path, password)
            flash("Incorrect password.", "error")
        return render_template("password_view.html", filename=filename)

    return render_file_view(filename, file_path, password)


def render_file_view(filename, file_path, password=None):
    extension = filename.rsplit(".", 1)[1].lower()

    filename = f"{filename}?password={password}" if password else filename

    if extension in supported_extensions["image"]:
        return render_template(
            "image_view.html",
            pagetitle=build_title("View Image"),
            filename=filename,
        )
    if extension in supported_extensions["video"]:
        return render_template(
            "video_view.html",
            pagetitle=build_title("View Video"),
            filename=filename,
        )
    if extension in supported_extensions["audio"]:
        return render_template(
            "audio_view.html",
            pagetitle=build_title("View Audio"),
            filename=filename,
        )
    if (
        extension in supported_extensions["text"]
        or extension in supported_extensions["code"]
    ):
        with open(file_path, "r") as file:
            file_content = file.read()
        line_numbers = "\n".join(
            str(i + 1) for i in range(len(file_content.splitlines()))
        )
        return render_template(
            "text_view.html",
            pagetitle=build_title("View Text"),
            filename=filename,
            file_content=file_content,
            line_numbers=line_numbers,
        )
    return send_file(file_path)


@view_bp.route("/raw/<filename>", methods=["GET", "POST"])
def view_raw(filename):
    filename = secure_filename(filename)
    file_path = os.path.join(uploads_folder, filename)

    if not os.path.exists(os.path.abspath(uploads_folder)):
        abort(404)

    file_info = db_handler.execute(
        "SELECT password_hash FROM uploads WHERE filename = ?",
        (filename,),
    )[0]

    if file_info[0]:
        password = request.args.get("password")
        if password and check_password_hash(file_info[0], password):
            return send_file(file_path, mimetype="text/plain", as_attachment=False)
        if request.method == "POST":
            password = request.form.get("password")
            if check_password_hash(file_info[0], password):
                return redirect(
                    url_for("view.view_raw", filename=filename, password=password)
                )
            flash("Incorrect password.", "error")
        return render_template("password_view.html", filename=filename)

    return send_file(file_path, mimetype="text/plain", as_attachment=False)
