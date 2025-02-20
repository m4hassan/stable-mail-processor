import logging
import os
import sqlite3

logger = logging.getLogger(__name__)

DB_FILE = os.path.join(os.path.dirname(__file__), 'processed_mail_ids.sqlite3')


def init_db():
    """
    Initialize the SQLite database and create the processed_mail table if it doesn't exist.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_mails (
            mail_id TEXT PRIMARY KEY,
            processed_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def load_processed_mail_ids():
    """
    Load the list of processed mail IDs from the DB.

    Returns:
        set: A set of processed mail IDs.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT mail_id FROM processed_mails")
    rows = cursor.fetchall()

    return set(row[0] for row in rows)


def save_processed_mail_id(mail_id):
    """
    Save a new mail ID to the processed list in the SQLite database.

    Args:
        mail_id (str): The mail ID to save.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO processed_mails (mail_id) VALUES (?)", (mail_id,))
        conn.commit()
    except sqlite3.IntegrityError:
        logger.warning(f"The mail ID '{mail_id}' already exists in processed mail IDs. skipping...")
        pass
    finally:
        conn.close()

# Initialize DB upon loading module
init_db()


