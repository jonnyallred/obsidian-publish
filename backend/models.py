import sqlite3
import secrets
import string
from datetime import datetime, timedelta
from pathlib import Path
from config import Config

class Database:
    """Database initialization and connection"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.init_db()

    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create magic_links table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS magic_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                token TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                used BOOLEAN DEFAULT 0
            )
        """)

        # Create sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()


class MagicLink:
    """Magic link token management"""

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate a cryptographically random URL-safe token"""
        alphabet = string.ascii_letters + string.digits + '-_'
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def create(email: str, expiration_minutes: int = 15) -> str:
        """
        Create a magic link token for email

        Returns:
            token: The generated token
        """
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()

        token = MagicLink.generate_token()
        expires_at = datetime.utcnow() + timedelta(minutes=expiration_minutes)

        try:
            cursor.execute(
                """
                INSERT INTO magic_links (email, token, expires_at)
                VALUES (?, ?, ?)
                """,
                (email, token, expires_at)
            )
            conn.commit()
            return token
        finally:
            conn.close()

    @staticmethod
    def verify(token: str) -> tuple[bool, str | None]:
        """
        Verify a magic link token

        Returns:
            (is_valid, email): Tuple of validity and email if valid
        """
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT email, expires_at, used FROM magic_links
                WHERE token = ?
                """,
                (token,)
            )
            row = cursor.fetchone()

            if not row:
                return False, None

            email, expires_at, used = row

            # Check if already used
            if used:
                return False, None

            # Check if expired
            expires_at_dt = datetime.fromisoformat(expires_at)
            if datetime.utcnow() > expires_at_dt:
                return False, None

            return True, email
        finally:
            conn.close()

    @staticmethod
    def mark_used(token: str) -> bool:
        """Mark a token as used (prevent reuse)"""
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "UPDATE magic_links SET used = 1 WHERE token = ?",
                (token,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def delete_expired() -> int:
        """Delete expired tokens"""
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                DELETE FROM magic_links
                WHERE expires_at < ?
                """,
                (datetime.utcnow(),)
            )
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()


class Session:
    """Session management"""

    @staticmethod
    def generate_session_id(length: int = 32) -> str:
        """Generate a cryptographically random session ID"""
        return secrets.token_urlsafe(length)

    @staticmethod
    def create(email: str) -> str:
        """
        Create a session for authenticated user

        Returns:
            session_id: The generated session ID
        """
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()

        session_id = Session.generate_session_id()

        try:
            cursor.execute(
                """
                INSERT INTO sessions (session_id, email)
                VALUES (?, ?)
                """,
                (session_id, email)
            )
            conn.commit()
            return session_id
        finally:
            conn.close()

    @staticmethod
    def validate(session_id: str) -> bool:
        """Check if session is valid and not expired"""
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT created_at, last_accessed FROM sessions
                WHERE session_id = ?
                """,
                (session_id,)
            )
            row = cursor.fetchone()

            if not row:
                return False

            created_at, last_accessed = row

            # Check if session has timed out (7 days)
            last_accessed_dt = datetime.fromisoformat(last_accessed)
            timeout_period = timedelta(days=Config.SESSION_TIMEOUT_DAYS)

            if datetime.utcnow() - last_accessed_dt > timeout_period:
                Session.delete(session_id)
                return False

            return True
        finally:
            conn.close()

    @staticmethod
    def update_last_accessed(session_id: str) -> bool:
        """Update the last_accessed timestamp for a session"""
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE sessions
                SET last_accessed = ?
                WHERE session_id = ?
                """,
                (datetime.utcnow(), session_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def get_email(session_id: str) -> str | None:
        """Get email associated with a session"""
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT email FROM sessions WHERE session_id = ?",
                (session_id,)
            )
            row = cursor.fetchone()
            return row['email'] if row else None
        finally:
            conn.close()

    @staticmethod
    def delete(session_id: str) -> bool:
        """Delete a session (logout)"""
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "DELETE FROM sessions WHERE session_id = ?",
                (session_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def delete_old(days: int = 30) -> int:
        """Delete sessions older than specified days"""
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()

        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            cursor.execute(
                """
                DELETE FROM sessions
                WHERE created_at < ?
                """,
                (cutoff_date,)
            )
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()


if __name__ == "__main__":
    # Initialize database when running this file directly
    db = Database()
    print(f"Database initialized at {Config.DATABASE_PATH}")
