import sqlite3
from config import DB_PATH
from datetime import datetime

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

def init_db():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            role TEXT,
            content TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

# Состояние
current_sessions = {}

def start_session(user_id: int, title: str) -> int:
    cursor.execute("INSERT INTO sessions (user_id, title) VALUES (?, ?)", (user_id, title[:100]))
    conn.commit()
    session_id = cursor.lastrowid
    current_sessions[user_id] = session_id
    return session_id

def get_session(user_id: int) -> int | None:
    return current_sessions.get(user_id)

def stop_session(user_id: int):
    current_sessions.pop(user_id, None)

def save_message(user_id: int, role: str, content: str):
    session_id = get_session(user_id)
    if session_id is None:
        session_id = start_session(user_id, content)
    cursor.execute("INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
                   (session_id, role, content))
    conn.commit()

def get_session_messages(session_id: int):
    cursor.execute("SELECT role, content FROM messages WHERE session_id = ? ORDER BY id", (session_id,))
    return [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]

def get_user_sessions(user_id: int):
    cursor.execute("SELECT id, title, created_at FROM sessions WHERE user_id = ? ORDER BY id DESC", (user_id,))
    return cursor.fetchall()

def reset_history(user_id: int):
    cursor.execute("DELETE FROM messages WHERE session_id IN (SELECT id FROM sessions WHERE user_id = ?)", (user_id,))
    cursor.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
    conn.commit()
    stop_session(user_id)
