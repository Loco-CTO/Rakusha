import os

from constant import BASE_DIR

from .handler import DatabaseHandler

db_handler = DatabaseHandler(
    db_type="sqlite",
    create_query={
        "sqlite": {
            "users": {
                "create": """
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        account_identifier TEXT UNIQUE NOT NULL,
                        secret_key TEXT NOT NULL,
                        email TEXT NOT NULL,
                        is_admin BOOLEAN DEFAULT FALSE
                    )
                """,
                "columns": {
                    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                    "username": "TEXT UNIQUE NOT NULL",
                    "password": "TEXT NOT NULL",
                    "account_identifier": "TEXT UNIQUE NOT NULL",
                    "secret_key": "TEXT NOT NULL",
                    "email": "TEXT NOT NULL",
                    "is_admin": "BOOLEAN DEFAULT FALSE",
                },
            },
            "uploads": {
                "create": """
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_name TEXT NOT NULL,
            filename TEXT NOT NULL,
            views INTEGER DEFAULT 0,
            size INTEGER NOT NULL,
            owner_identifier TEXT NOT NULL,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            password_hash TEXT,
            FOREIGN KEY(owner_identifier) REFERENCES users(account_identifier)
        )
    """,
                "columns": {
                    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                    "original_name": "TEXT NOT NULL",
                    "filename": "TEXT NOT NULL",
                    "views": "INTEGER DEFAULT 0",
                    "size": "INTEGER NOT NULL",
                    "owner_identifier": "TEXT NOT NULL",
                    "password_hash": "TEXT",
                    "upload_time": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                },
            },
            "invites": {
                "create": """
                    CREATE TABLE IF NOT EXISTS invites (
                        code TEXT PRIMARY KEY,
                        used BOOLEAN DEFAULT FALSE
                    )
                """,
                "columns": {
                    "code": "TEXT PRIMARY KEY",
                    "used": "BOOLEAN DEFAULT FALSE",
                },
            },
        }
    },
    db_file=os.path.join(BASE_DIR, "sqlite", "xflask.db"),
)

db_handler.create_tables()
