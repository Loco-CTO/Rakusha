import sys

sys.dont_write_bytecode = True
from dotenv import load_dotenv

load_dotenv()
import os

if not os.path.exists("uploads"):
    os.mkdir("uploads")
if not os.path.exists("sqlite"):
    os.mkdir("sqlite")

from flask import Flask, redirect, url_for
from flask_login import LoginManager

from error import handle_error
from models.user import User, create_account
from routes.auth_routes import auth_bp
from routes.dashboard_route import dashboard_bp
from routes.invite_routes import invite_bp
from routes.storage_routes import storage_bp
from routes.upload_routes import upload_bp
from routes.view_routes import view_bp
from version import __version__

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"


@app.context_processor
def inject_version():
    return dict(version=__version__)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route("/login")
def login_redirect():
    return redirect(url_for("auth.login"))


app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(upload_bp, url_prefix="/upload")
app.register_blueprint(view_bp, url_prefix="/view")
app.register_blueprint(storage_bp, url_prefix="/storage")
app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
app.register_blueprint(invite_bp, url_prefix="/invite")

app.register_error_handler(404, handle_error)
app.register_error_handler(405, handle_error)
app.register_error_handler(500, handle_error)


def create_admin_account():
    if User.get_user_count() == 0:
        create_account("admin", "1234", is_admin=True)
        print("Admin account created.")
    else:
        print("Admin account already exists.")


if __name__ == "__main__":
    create_admin_account()
    app.run(host="0.0.0.0", port=25621, debug=True)
