import sqlite3

from mysql.connector import Error


class DatabaseHandler:
    def __init__(self, db_type, create_query, db_file=None):
        self.db_type = db_type
        self.create_query = create_query
        self.db_file = db_file
        self.connection = None
        self.connect()

    def connect(self):
        if self.db_type == "sqlite":
            self._connect_sqlite(self.db_file)

    def _connect_sqlite(self, db_file):
        try:
            self.connection = sqlite3.connect(db_file, check_same_thread=False)
            self.create_tables()
        except sqlite3.Error as e:
            print(f"Error connecting to SQLite: {e}")

    def create_tables(self):
        for table, queries in self.create_query[self.db_type].items():
            self._create_or_update_table(table, queries)

    def _create_or_update_table(self, table_name, queries):
        if not self._table_exists(table_name):
            self._create_table(table_name, queries["create"])
        else:
            self._update_table(table_name, queries["columns"])

    def _table_exists(self, table_name):
        cursor = self.connection.cursor()
        if self.db_type == "sqlite":
            cursor.execute(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
            )
        elif self.db_type == "mysql":
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        exists = cursor.fetchone() is not None
        cursor.close()
        return exists

    def _create_table(self, table_name, create_query):
        cursor = self.connection.cursor()
        cursor.execute(create_query)
        self.connection.commit()
        cursor.close()

    def _update_table(self, table_name, columns):
        cursor = self.connection.cursor()
        existing_columns = self._get_existing_columns(table_name)
        for column, column_def in columns.items():
            if column not in existing_columns:
                alter_query = (
                    f"ALTER TABLE {table_name} ADD COLUMN {column} {column_def}"
                )
                cursor.execute(alter_query)
                self.connection.commit()

    def _get_existing_columns(self, table_name):
        cursor = self.connection.cursor()
        if self.db_type == "sqlite":
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = {col[1] for col in cursor.fetchall()}
        elif self.db_type == "mysql":
            cursor.execute(f"DESCRIBE {table_name}")
            columns = {col[0] for col in cursor.fetchall()}
        cursor.close()
        return columns

    def execute(self, query, params=None):
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor.fetchall()
        except (sqlite3.Error, Error) as e:
            print(f"Database error: {e}")
            return None
        finally:
            cursor.close()

    def fetchall(self):
        cursor = self.connection.cursor()
        try:
            return cursor.fetchall() if cursor else None
        except (sqlite3.Error, Error) as e:
            print(f"Database error: {e}")
            return None
        finally:
            cursor.close()

    def fetchone(self):
        cursor = self.connection.cursor()
        try:
            return cursor.fetchone() if cursor else None
        except (sqlite3.Error, Error) as e:
            print(f"Database error: {e}")
            return None
        finally:
            cursor.close()

    def close(self):
        if self.connection:
            self.connection.close()
