"""
database.py
------------
Handles all SQLite database logic for user accounts.
Passwords are never stored in plain text - they are salted and hashed
using SHA-256 (via Python's built-in hashlib) before being saved.

Table schema (users.db -> table 'users'):
    id            INTEGER PRIMARY KEY AUTOINCREMENT
    username      TEXT UNIQUE NOT NULL
    email         TEXT UNIQUE NOT NULL
    password_hash TEXT NOT NULL
    salt          TEXT NOT NULL
    created_at    TEXT NOT NULL
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime

DB_PATH = "users.db"


def get_connection():
    """Return a new SQLite connection (each Streamlit rerun gets its own)."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the users table if it does not already exist. Safe to call every run."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT UNIQUE NOT NULL,
            email         TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt          TEXT NOT NULL,
            created_at    TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def _hash_password(password: str, salt: str) -> str:
    """Combine password + salt and hash with SHA-256."""
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def create_user(username: str, email: str, password: str) -> tuple[bool, str]:
    """
    Insert a new user into the database.
    Returns (success: bool, message: str).
    """
    username = username.strip()
    email = email.strip().lower()

    if not username or not email or not password:
        return False, "All fields are required."
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    conn = get_connection()
    cur = conn.cursor()

    # Check for existing username / email before inserting
    cur.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
    if cur.fetchone():
        conn.close()
        return False, "Username or email is already registered."

    salt = secrets.token_hex(16)
    password_hash = _hash_password(password, salt)
    created_at = datetime.utcnow().isoformat()

    try:
        cur.execute(
            "INSERT INTO users (username, email, password_hash, salt, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (username, email, password_hash, salt, created_at),
        )
        conn.commit()
        return True, "Account created successfully. Please log in."
    except sqlite3.IntegrityError:
        return False, "Username or email is already registered."
    finally:
        conn.close()


def verify_user(email: str, password: str) -> tuple[bool, str]:
    """
    Verify login credentials (email + password).
    Returns (success: bool, username_or_error_message: str).
    """
    email = email.strip().lower()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT username, password_hash, salt FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return False, "No account found with that email."

    candidate_hash = _hash_password(password, row["salt"])
    if candidate_hash == row["password_hash"]:
        return True, row["username"]
    return False, "Incorrect password."
