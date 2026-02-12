import string
import sqlite3
from datetime import datetime, timedelta
from unittest.mock import patch

from models import Database, MagicLink, Session


class TestGenerateToken:
    def test_default_length(self):
        token = MagicLink.generate_token()
        assert len(token) == 32

    def test_custom_length(self):
        token = MagicLink.generate_token(64)
        assert len(token) == 64

    def test_url_safe_characters(self):
        allowed = set(string.ascii_letters + string.digits + "-_")
        token = MagicLink.generate_token(100)
        assert set(token).issubset(allowed)

    def test_uniqueness(self):
        tokens = {MagicLink.generate_token() for _ in range(50)}
        assert len(tokens) == 50


class TestMagicLinkCreate:
    def test_create_returns_token(self, test_db):
        token = MagicLink.create("user@example.com")
        assert isinstance(token, str)
        assert len(token) == 32

    def test_create_stores_row(self, test_db):
        token = MagicLink.create("user@example.com")
        conn = sqlite3.connect(test_db)
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM magic_links WHERE token = ?", (token,)
        ).fetchone()
        conn.close()
        assert row is not None
        assert row["email"] == "user@example.com"
        assert row["used"] == 0


class TestMagicLinkVerify:
    def test_valid_token(self, test_db):
        token = MagicLink.create("user@example.com")
        is_valid, email = MagicLink.verify(token)
        assert is_valid is True
        assert email == "user@example.com"

    def test_nonexistent_token(self, test_db):
        is_valid, email = MagicLink.verify("nonexistent-token")
        assert is_valid is False
        assert email is None

    def test_used_token(self, test_db):
        token = MagicLink.create("user@example.com")
        MagicLink.mark_used(token)
        is_valid, email = MagicLink.verify(token)
        assert is_valid is False
        assert email is None

    def test_expired_token(self, test_db):
        token = MagicLink.create("user@example.com", expiration_minutes=0)
        # Force expiration by backdating
        conn = sqlite3.connect(test_db)
        past = datetime.utcnow() - timedelta(hours=1)
        conn.execute(
            "UPDATE magic_links SET expires_at = ? WHERE token = ?",
            (str(past), token),
        )
        conn.commit()
        conn.close()

        is_valid, email = MagicLink.verify(token)
        assert is_valid is False
        assert email is None


class TestMagicLinkMarkUsed:
    def test_mark_existing(self, test_db):
        token = MagicLink.create("user@example.com")
        assert MagicLink.mark_used(token) is True

    def test_mark_nonexistent(self, test_db):
        assert MagicLink.mark_used("no-such-token") is False


class TestDeleteExpired:
    def test_deletes_expired_keeps_valid(self, test_db):
        valid_token = MagicLink.create("valid@example.com")

        expired_token = MagicLink.create("expired@example.com")
        conn = sqlite3.connect(test_db)
        past = datetime.utcnow() - timedelta(hours=1)
        conn.execute(
            "UPDATE magic_links SET expires_at = ? WHERE token = ?",
            (str(past), expired_token),
        )
        conn.commit()
        conn.close()

        deleted = MagicLink.delete_expired()
        assert deleted == 1

        # Valid token still exists
        is_valid, _ = MagicLink.verify(valid_token)
        assert is_valid is True


class TestSessionCreate:
    def test_create_returns_session_id(self, test_db):
        sid = Session.create("user@example.com")
        assert isinstance(sid, str)
        assert len(sid) > 0

    def test_create_stores_row(self, test_db):
        sid = Session.create("user@example.com")
        conn = sqlite3.connect(test_db)
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (sid,)
        ).fetchone()
        conn.close()
        assert row is not None
        assert row["email"] == "user@example.com"


class TestSessionValidate:
    def test_valid_session(self, test_db):
        sid = Session.create("user@example.com")
        assert Session.validate(sid) is True

    def test_nonexistent_session(self, test_db):
        assert Session.validate("nonexistent-session") is False

    def test_expired_session(self, test_db):
        sid = Session.create("user@example.com")
        # Backdate last_accessed beyond timeout
        conn = sqlite3.connect(test_db)
        old = datetime.utcnow() - timedelta(days=30)
        conn.execute(
            "UPDATE sessions SET last_accessed = ? WHERE session_id = ?",
            (str(old), sid),
        )
        conn.commit()
        conn.close()

        assert Session.validate(sid) is False


class TestSessionGetEmail:
    def test_existing_session(self, test_db):
        sid = Session.create("user@example.com")
        assert Session.get_email(sid) == "user@example.com"

    def test_nonexistent_session(self, test_db):
        assert Session.get_email("no-such-session") is None


class TestSessionDelete:
    def test_delete_existing(self, test_db):
        sid = Session.create("user@example.com")
        assert Session.delete(sid) is True
        assert Session.validate(sid) is False

    def test_delete_nonexistent(self, test_db):
        assert Session.delete("no-such-session") is False


class TestSessionDeleteOld:
    def test_deletes_old_keeps_recent(self, test_db):
        recent_sid = Session.create("recent@example.com")

        old_sid = Session.create("old@example.com")
        conn = sqlite3.connect(test_db)
        old_date = datetime.utcnow() - timedelta(days=60)
        conn.execute(
            "UPDATE sessions SET created_at = ? WHERE session_id = ?",
            (str(old_date), old_sid),
        )
        conn.commit()
        conn.close()

        deleted = Session.delete_old(days=30)
        assert deleted == 1
        assert Session.validate(recent_sid) is True


class TestDatabase:
    def test_init_creates_tables(self, test_db):
        conn = sqlite3.connect(test_db)
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        conn.close()
        table_names = {row[0] for row in tables}
        assert "magic_links" in table_names
        assert "sessions" in table_names

    def test_idempotent_reinit(self, test_db):
        # Insert data, then re-init — data should survive
        MagicLink.create("user@example.com")
        Database(test_db)

        conn = sqlite3.connect(test_db)
        count = conn.execute("SELECT COUNT(*) FROM magic_links").fetchone()[0]
        conn.close()
        assert count == 1
