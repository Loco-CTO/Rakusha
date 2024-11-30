import re

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_user

from models.invite import Invite
from models.user import create_account

invite_bp = Blueprint("invite", __name__)


def validate_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Za-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True


@invite_bp.route("/<code>", methods=["GET", "POST"])
def register(code):
    invite = Invite.get_by_code(code)
    if not invite or invite.used:
        flash("Invalid or expired invite code.")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not validate_password(password):
            flash(
                "Password must be at least 8 characters long and contain at least one number and one alphabet."
            )
            return render_template("register_view.html", code=code)
        try:
            user = create_account(username, password)
            invite.mark_as_used()
            login_user(user)
            flash("Account created successfully.")
            return redirect(url_for("dashboard.dashboard"))
        except ValueError as e:
            flash(str(e))

    return render_template("register_view.html", code=code)
