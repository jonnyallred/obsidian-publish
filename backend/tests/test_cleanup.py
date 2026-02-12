import sqlite3
from datetime import datetime, timedelta

from models import MagicLink, Session
from cleanup import cleanup_database


class TestCleanupDatabase:
    def test_deletes_expired_and_old(self, test_db):
        # Create an expired token
        token = MagicLink.create("expired@example.com")
        conn = sqlite3.connect(test_db)
        past = datetime.utcnow() - timedelta(hours=1)
        conn.execute(
            "UPDATE magic_links SET expires_at = ? WHERE token = ?",
            (str(past), token),
        )
        conn.commit()

        # Create an old session
        sid = Session.create("old@example.com")
        old_date = datetime.utcnow() - timedelta(days=60)
        conn.execute(
            "UPDATE sessions SET created_at = ? WHERE session_id = ?",
            (str(old_date), sid),
        )
        conn.commit()
        conn.close()

        result = cleanup_database()
        assert result is True

        # Verify expired token was deleted
        conn = sqlite3.connect(test_db)
        token_count = conn.execute("SELECT COUNT(*) FROM magic_links").fetchone()[0]
        session_count = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        conn.close()
        assert token_count == 0
        assert session_count == 0

    def test_preserves_valid_data(self, test_db):
        MagicLink.create("valid@example.com")
        Session.create("active@example.com")

        result = cleanup_database()
        assert result is True

        conn = sqlite3.connect(test_db)
        token_count = conn.execute("SELECT COUNT(*) FROM magic_links").fetchone()[0]
        session_count = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        conn.close()
        assert token_count == 1
        assert session_count == 1

    def test_returns_true_on_success(self, test_db):
        assert cleanup_database() is True
