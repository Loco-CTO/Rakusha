import os

from flask import Blueprint, abort, current_app, render_template, send_file

from database import db_handler
from models.page_title import build_title

from .extensions import supported_extensions

view_bp = Blueprint("view", __name__)
uploads_folder = "uploads"


@view_bp.route("/<filename>", methods=["GET"])
def view(filename):
    file_path = os.path.join(uploads_folder, filename)
    if os.path.exists(file_path):
        db_handler.execute(
            "UPDATE uploads SET views = views + 1 WHERE filename = ?",
            (filename,),
        )
        current_app.logger.info(f"Incremented view count for {filename}")

        extension = filename.rsplit(".", 1)[1].lower()

        if extension in supported_extensions["image"]:
            return render_template(
                "image_view.html",
                pagetitle=build_title("View Image"),
                filename=filename,
            )
        elif extension in supported_extensions["video"]:
            return render_template(
                "video_view.html",
                pagetitle=build_title("View Video"),
                filename=filename,
            )
        elif extension in supported_extensions["audio"]:
            return render_template(
                "audio_view.html",
                pagetitle=build_title("View Audio"),
                filename=filename,
            )
        elif (
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
    abort(404)


@view_bp.route("/raw/<filename>", methods=["GET"])
def view_raw(filename):
    file_path = os.path.join(uploads_folder, filename)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype="text/plain", as_attachment=False)
    abort(404)
