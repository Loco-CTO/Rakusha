import os
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from models.page_title import build_title
from models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        remember = "remember" in request.form
        user = User.get_by_username(username)
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash("Logged in successfully.")
            return redirect(url_for("dashboard.dashboard"))
        flash("Invalid username or password.")
    return render_template("login_view.html", pagetitle=build_title("Login"))


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("auth.login"))
