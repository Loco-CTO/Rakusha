import secrets
import sqlite3
import uuid

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from database import db_handler


def create_account(name, password, is_admin=False):
    account_identifier = str(uuid.uuid4())
    secret_key = secrets.token_hex(16)
    password_hash = generate_password_hash(password)
    user = User(
        id=None,
        username=name,
        password_hash=password_hash,
        account_identifier=account_identifier,
        secret_key=secret_key,
        email="",
        is_admin=is_admin,
    )
    user.save()
    return user


class User(UserMixin):
    def __init__(
        self,
        id,
        username,
        password_hash,
        account_identifier,
        secret_key,
        email,
        is_admin=False,
    ):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.account_identifier = account_identifier
        self.secret_key = secret_key
        self.email = email
        self.is_admin = is_admin

    @staticmethod
    def get(user_id):
        query = "SELECT * FROM users WHERE id = ?"
        result = db_handler.execute(query, (user_id,))
        if result:
            return User(*result[0])
        return None

    @staticmethod
    def get_by_username(username):
        query = "SELECT * FROM users WHERE username = ?"
        result = db_handler.execute(query, (username,))
        if result:
            return User(*result[0])
        return None

    @staticmethod
    def get_by_secret_key(secret_key):
        query = "SELECT * FROM users WHERE secret_key = ?"
        result = db_handler.execute(query, (secret_key,))
        if result:
            return User(*result[0])
        return None

    @staticmethod
    def get_user_count():
        query = "SELECT COUNT(*) FROM users"
        result = db_handler.execute(query)
        return result[0][0] if result else 0

    @staticmethod
    def get_all_users():
        query = "SELECT * FROM users"
        result = db_handler.execute(query)
        return [User(*row) for row in result] if result else []

    @staticmethod
    def delete_user(user_id):
        query = "DELETE FROM users WHERE id = ?"
        db_handler.execute(query, (user_id,))

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def save(self):
        try:
            if self.id:
                query = """
                    UPDATE users
                    SET username = ?, password = ?, account_identifier = ?, secret_key = ?, email = ?, is_admin = ?
                    WHERE id = ?
                """
                db_handler.execute(
                    query,
                    (
                        self.username,
                        self.password_hash,
                        self.account_identifier,
                        self.secret_key,
                        self.email,
                        self.is_admin,
                        self.id,
                    ),
                )
            else:
                query = """
                    INSERT INTO users (username, password, account_identifier, secret_key, email, is_admin)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                db_handler.execute(
                    query,
                    (
                        self.username,
                        self.password_hash,
                        self.account_identifier,
                        self.secret_key,
                        self.email,
                        self.is_admin,
                    ),
                )
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError("A user with this email or username already exists.")
            raise e
