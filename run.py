from waitress import serve

from app import app
from models.user import User, create_account


def create_admin_account():
    if User.get_user_count() == 0:
        create_account("admin", "1234", is_admin=True)
        print("Admin account created.")
    else:
        print("Admin account already exists.")


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=25621)
