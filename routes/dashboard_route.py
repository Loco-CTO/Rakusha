import datetime
import os

from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from constant import BASE_DIR
from database import db_handler
from models.invite import Invite
from models.page_title import build_title
from models.user import User

dashboard_bp = Blueprint("dashboard", __name__)

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")


@dashboard_bp.route("/set_password", methods=["POST"])
@login_required
def set_password():
    user = current_user
    filename = request.form.get("filename")
    new_password = request.form.get("new_password")
    if not filename:
        return jsonify({"error": "Filename and password are required"}), 400

    password_hash = generate_password_hash(new_password) if new_password else None
    db_handler.execute(
        "UPDATE uploads SET password_hash = ? WHERE filename = ? AND owner_identifier = ?",
        (password_hash, filename, user.account_identifier),
    )
    return jsonify({"success": "Password set successfully"}), 200


@dashboard_bp.route("/delete_file", methods=["POST"])
@login_required
def delete_file():
    user = current_user
    filename = request.form.get("filename")
    if not filename:
        session["notification"] = {"message": "No filename provided", "type": "error"}
        return jsonify({"error": "No filename provided"}), 400

    filename = secure_filename(filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(os.path.abspath(UPLOAD_FOLDER)):
        session["notification"] = {"message": "Invalid file path", "type": "error"}
        return jsonify({"error": "Invalid file path"}), 400

    if os.path.exists(file_path):
        os.remove(file_path)
        db_handler.execute(
            "DELETE FROM uploads WHERE filename = ? AND owner_identifier = ?",
            (filename, user.account_identifier),
        )
        session["notification"] = {
            "message": "File deleted successfully",
            "type": "success",
        }
        return jsonify({"success": "File deleted successfully"}), 200
    session["notification"] = {"message": "File not found", "type": "error"}
    return jsonify({"error": "File not found"}), 404


@dashboard_bp.route("/clear_notification", methods=["GET"])
def clear_notification():
    session.pop("notification", None)
    return "", 204


@dashboard_bp.route("/")
@login_required
def dashboard():
    user = current_user
    uploaded_files_count = db_handler.execute(
        "SELECT COUNT(*) FROM uploads WHERE owner_identifier = ?",
        (user.account_identifier,),
    )[0][0]
    views_count = (
        db_handler.execute(
            "SELECT SUM(views) FROM uploads WHERE owner_identifier = ?",
            (user.account_identifier,),
        )[0][0]
        or 0
    )
    storage_usage = (
        db_handler.execute(
            "SELECT SUM(size) FROM uploads WHERE owner_identifier = ?",
            (user.account_identifier,),
        )[0][0]
        or 0
    )
    storage_usage = f"{storage_usage / (1024 ** 3):.2f} GB"

    recent_uploads = db_handler.execute(
        "SELECT original_name, filename, upload_time, size FROM uploads WHERE owner_identifier = ? ORDER BY upload_time DESC LIMIT 10",
        (user.account_identifier,),
    )

    formatted_uploads = []
    for upload in recent_uploads:
        upload_time = datetime.datetime.strptime(upload[2], "%Y-%m-%d %H:%M:%S.%f")
        formatted_upload_time = upload_time.strftime("%Y-%m-%d %H:%M")
        formatted_uploads.append(
            (upload[0], upload[1], formatted_upload_time, upload[3])
        )

    return render_template(
        "dashboard_home.html",
        active_page="home",
        pagetitle=build_title("Dashboard"),
        username=user.username,
        uploaded_files_count=uploaded_files_count,
        views_count=views_count,
        storage_usage=storage_usage,
        recent_uploads=formatted_uploads,
        is_admin=user.is_admin,
    )


@dashboard_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    user = current_user
    if request.method == "POST":
        try:
            if "update_email" in request.form:
                new_email = request.form["email"]
                password = request.form["password"]
                if user.check_password(password):
                    user.email = new_email
                    user.save()
                    flash("Email updated successfully.", "success")
                else:
                    flash("Incorrect password.", "error")
            elif "update_username" in request.form:
                new_username = request.form["username"]
                password = request.form["password"]
                if user.check_password(password):
                    user.username = new_username
                    user.save()
                    flash("Username updated successfully.", "success")
                else:
                    flash("Incorrect password.", "error")
            elif "update_password" in request.form:
                current_password = request.form["current_password"]
                new_password = request.form["new_password"]
                confirm_new_password = request.form["confirm_new_password"]
                if new_password != confirm_new_password:
                    flash("New passwords do not match.", "error")
                elif user.check_password(current_password):
                    user.password_hash = generate_password_hash(new_password)
                    user.save()
                    flash("Password updated successfully.", "success")
                else:
                    flash("Incorrect current password.", "error")
            elif "delete_uploads" in request.form:
                password = request.form["password"]
                if user.check_password(password):
                    uploads = db_handler.execute(
                        "SELECT filename FROM uploads WHERE owner_identifier = ?",
                        (user.account_identifier,),
                    )
                    for upload in uploads:
                        file_path = os.path.join(UPLOAD_FOLDER, upload[0])
                        if os.path.exists(file_path):
                            os.remove(file_path)
                    db_handler.execute(
                        "DELETE FROM uploads WHERE owner_identifier = ?",
                        (user.account_identifier,),
                    )
                    flash("All uploads deleted successfully.", "success")
                else:
                    flash("Incorrect password.", "error")
            elif "request_data" in request.form:
                password = request.form["password"]
                if user.check_password(password):
                    flash(
                        "Your data request has been received. You will receive an email with your data within 30 working days.",
                        "success",
                    )
                    flash(
                        "NOT IMPLEMENTED",
                        "success",
                    )
                else:
                    flash("Incorrect password.", "error")
            return redirect(url_for("dashboard.settings"))
        except ValueError as e:
            flash(str(e), "error")
        return redirect(url_for("dashboard.settings"))

    return render_template(
        "dashboard_settings.html",
        active_page="settings",
        is_admin=user.is_admin,
        pagetitle=build_title("Settings"),
        username=user.username,
        email=user.email,
        user_secret=user.account_identifier,
        sharex_key=user.secret_key,
        sharex_address=url_for("upload.sharex", _external=True),
        sharex_config=f"""{{
    "Version": "16.1.0",
    "Name": "Rystal Files",
    "DestinationType": "ImageUploader, FileUploader",
    "RequestMethod": "POST",
    "RequestURL": "{url_for("upload.sharex", _external=True)}",
    "Body": "MultipartFormData",
    "Arguments": {{
        "secret_key": "{user.secret_key}"
    }},
    "FileFormName": "file",
    "URL": "{{json:url}}"
}}""",
    )


@dashboard_bp.route("/upload")
@login_required
def upload():
    user = current_user
    return render_template(
        "dashboard_upload.html",
        is_admin=user.is_admin,
        active_page="upload",
        pagetitle=build_title("Upload"),
    )


@dashboard_bp.route("/files", methods=["GET"])
@login_required
def files():
    user = current_user
    page = request.args.get("page", 1, type=int)
    per_page = 25
    offset = (page - 1) * per_page

    sort_by = request.args.get("sort_by", "upload_time")
    sort_order = request.args.get("sort_order", "desc")
    search = request.args.get("search", "")

    valid_sort_by = ["filename", "upload_time", "views", "size"]
    valid_sort_order = ["asc", "desc"]

    if sort_by not in valid_sort_by:
        sort_by = "upload_time"
    if sort_order not in valid_sort_order:
        sort_order = "desc"

    if sort_by == "filename":
        sort_by = "original_name"

    search_query = f"%{search}%"

    total_files = db_handler.execute(
        "SELECT COUNT(*) FROM uploads WHERE owner_identifier = ? AND original_name LIKE ?",
        (user.account_identifier, search_query),
    )[0][0]

    uploads = db_handler.execute(
        f"SELECT original_name, filename, upload_time, size, views, password_hash FROM uploads WHERE owner_identifier = ? AND original_name LIKE ? ORDER BY {sort_by} {sort_order} LIMIT ? OFFSET ?",
        (user.account_identifier, search_query, per_page, offset),
    )

    formatted_uploads = []
    for upload in uploads:
        upload_time = datetime.datetime.strptime(upload[2], "%Y-%m-%d %H:%M:%S.%f")
        formatted_upload_time = upload_time.strftime("%Y-%m-%d %H:%M")
        is_protected = "Yes" if upload[5] else "No"
        formatted_uploads.append(
            (
                upload[0],
                upload[1],
                formatted_upload_time,
                upload[3],
                upload[4],
                is_protected,
            )
        )

    total_pages = (total_files + per_page - 1) // per_page

    return render_template(
        "dashboard_files.html",
        active_page="files",
        is_admin=user.is_admin,
        pagetitle=build_title("Files"),
        uploads=formatted_uploads,
        page=page,
        total_pages=total_pages,
        sort_by=sort_by,
        sort_order=sort_order,
        search=search,
    )


@dashboard_bp.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    user = current_user
    if not user.is_admin:
        flash("Access denied.")
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        if "create_invite" in request.form:
            invite = Invite.create_invite()
            flash(
                f"Invite link created: {url_for('invite.register', code=invite.code, _external=True)}"
            )
        elif "delete_invite" in request.form:
            code = request.form["delete_invite"]
            Invite.delete_invite(code)
            flash("Invite deleted successfully.")
        elif "delete_user" in request.form:
            user_id = request.form["delete_user"]
            User.delete_user(user_id)
            flash("User deleted successfully.")
        elif "edit_user" in request.form:
            user_id = request.form["edit_user"]
            new_username = request.form["new_username"]
            new_email = request.form["new_email"]
            is_admin = "is_admin" in request.form
            user = User.get(user_id)
            user.username = new_username
            user.email = new_email
            user.is_admin = is_admin
            user.save()
            flash("User updated successfully.")

    users = User.get_all_users()
    invites = Invite.get_all_invites()
    return render_template(
        "dashboard_admin.html",
        users=users,
        is_admin=user.is_admin,
        invites=invites,
        active_page="admin",
    )
