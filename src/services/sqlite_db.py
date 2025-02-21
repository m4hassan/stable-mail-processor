import os
import sqlite3

from logger import get_logger

from . import DatabaseService

logger = get_logger()


class SQLiteDatabase(DatabaseService):
    def __init__(self, db_path):
        self.db_path = db_path
        self.ensure_database_exists()
        self.initialize()

    def ensure_database_exists(self):
        if not os.path.exists(self.db_path):
            open(self.db_path, "a").close()
            logger.info(f"Database created at {self.db_path}")

    def initialize(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS processed_mails (
                mail_id TEXT PRIMARY KEY,
                processed_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        conn.commit()
        conn.close()

    def get_processed_mail_ids(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT mail_id FROM processed_mails")
        rows = cursor.fetchall()
        conn.close()
        return set(row[0] for row in rows)

    def save_processed_mail_id(self, mail_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO processed_mails (mail_id) VALUES (?)", (mail_id,)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            logger.warning(f"Mail ID '{mail_id}' already exists in processed mail IDs")
        finally:
            conn.close()
