import sqlite3
import sqlite3
import os
from datetime import datetime

DB_PATH = "aegis_memory.db"

def get_db_connection():
    """Establishes a connection to the local SQLite database file"""
    conn = sqlite3.connect(DB_PATH)

    # Allows to pull rows out as Dictionaries instead of tuples
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema for structural session memory"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 1. Sessions Table: Tracking overall chat workspaces
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        """)

        # 2. Messages Table: Tracks indicidual conversational traces and tool metrics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
            );
        """)
        conn.commit()

def create_session(session_id: str, title: str) -> None:
    """Inserting a fresh chat session checkpoint into the tracking board"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute(
            "INSERT OR IGNORE INTO sessions (id, title, created_at) VALUES (?, ?, ?);",
            (session_id, title, now)
        )
        conn.commit()
    
def save_message(session_id: str, role: str, content: str) -> None:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?);",
            (session_id, role, content, now)
        )
        conn.commit()
    
def get_all_sessions():
    """Retrieves all historical chat sessions to populate the sidebar"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM session ORDER BY created_at DESC;")
        return cursor.fetchall()
    
def get_session_messages(session_id: str):
    """Gathers the sequential history payload to inject into the LLM context window"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY timestamp ASC;",
            (session_id,)
        )
        return cursor.fetchall()

if __name__=="__main__":
    # Testing with initialization by running independently
    init_db()
    print("Database Structures initialized successfully without system conflicts.")