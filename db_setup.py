import sqlite3
import os

DB_FILE = "chatroom.db"

def init_db():
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()


        # Create a table for messages
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_pin TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()
        print(f"Database {DB_FILE} initialized successfully!")
    else:
        print(f"Database {DB_FILE} already exists.")


if __name__ == "__main__":
    init_db()
