from waitress import serve

import logging
from models.user import User, create_account
from app import app


def create_admin_account():
    if User.get_user_count() == 0:
        create_account("admin", "1234", is_admin=True)
        logging.debug("Admin account created.")
    else:
        logging.debug("Admin account already exists.")


logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(message)s")


if __name__ == "__main__":
    create_admin_account()
    serve(
        app,
        host="0.0.0.0",
        port=25621,
    )
