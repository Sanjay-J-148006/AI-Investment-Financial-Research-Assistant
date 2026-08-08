import sqlite3
import os
from typing import List, Dict, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "investor_memory.db")

def init_sqlite_db(db_path: str = DB_PATH):
    """
    Initializes SQLite tables for investor profiles and conversation history log.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS investor_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        risk_profile TEXT,
        preferred_industries TEXT,
        investment_horizon TEXT,
        notes TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversation_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        role TEXT,
        content TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()

def save_investor_profile(name: str, risk_profile: str, preferred_industries: str, horizon: str, notes: str = "") -> str:
    """
    Saves or updates an investor profile in SQLite.
    """
    init_sqlite_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO investor_profiles (name, risk_profile, preferred_industries, investment_horizon, notes)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(name) DO UPDATE SET
        risk_profile=excluded.risk_profile,
        preferred_industries=excluded.preferred_industries,
        investment_horizon=excluded.investment_horizon,
        notes=excluded.notes,
        updated_at=CURRENT_TIMESTAMP
    """, (name, risk_profile, preferred_industries, horizon, notes))
    
    conn.commit()
    conn.close()
    return f"Saved profile for investor '{name}'."

def get_investor_profile(name: str) -> Optional[Dict]:
    """
    Retrieves an investor profile by name.
    """
    init_sqlite_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, risk_profile, preferred_industries, investment_horizon, notes, updated_at FROM investor_profiles WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "id": row[0],
            "name": row[1],
            "risk_profile": row[2],
            "preferred_industries": row[3],
            "investment_horizon": row[4],
            "notes": row[5],
            "updated_at": row[6]
        }
    return None

def get_all_investor_profiles() -> List[Dict]:
    """
    Retrieves all saved investor profiles from SQLite.
    """
    init_sqlite_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, risk_profile, preferred_industries, investment_horizon, notes, updated_at FROM investor_profiles ORDER BY updated_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    profiles = []
    for r in rows:
        profiles.append({
            "id": r[0],
            "name": r[1],
            "risk_profile": r[2],
            "preferred_industries": r[3],
            "investment_horizon": r[4],
            "notes": r[5],
            "updated_at": r[6]
        })
    return profiles

def delete_investor_profile(name: str) -> str:
    """
    Deletes an investor profile by name.
    """
    init_sqlite_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM investor_profiles WHERE name = ?", (name,))
    conn.commit()
    conn.close()
    return f"Deleted profile for '{name}'."

def log_conversation_turn(session_id: str, role: str, content: str):
    """
    Logs a single conversation message to persistent SQLite history.
    """
    init_sqlite_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO conversation_logs (session_id, role, content) VALUES (?, ?, ?)", (session_id, role, content))
    conn.commit()
    conn.close()

def get_recent_conversation_logs(session_id: str, limit: int = 15) -> List[Dict]:
    """
    Retrieves recent conversation history from SQLite.
    """
    init_sqlite_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT role, content, timestamp FROM conversation_logs WHERE session_id = ? ORDER BY id DESC LIMIT ?", (session_id, limit))
    rows = cursor.fetchall()
    conn.close()
    
    return [{"role": r[0], "content": r[1], "timestamp": r[2]} for r in reversed(rows)]
