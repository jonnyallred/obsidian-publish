import os
import pytest
from pathlib import Path

from models import Database, Session


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """Patch Config.DATABASE_PATH to a temp file and initialize tables."""
    db_path = str(tmp_path / "test.db")
    monkeypatch.setattr("config.Config.DATABASE_PATH", db_path)
    Database(db_path)
    return db_path


@pytest.fixture
def app(test_db):
    """Create Flask app configured for testing."""
    from app import app as flask_app
    from auth import limiter as auth_limiter

    flask_app.config["TESTING"] = True
    flask_app.config["SECRET_KEY"] = "test-secret-key"
    auth_limiter.enabled = False

    return flask_app


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def authenticated_client(client, test_db):
    """Test client with an authenticated session."""
    session_id = Session.create("test@example.com")

    with client.session_transaction() as sess:
        sess["session_id"] = session_id
        sess["email"] = "test@example.com"

    return client


@pytest.fixture
def content_dir(tmp_path):
    """Temp content directory with sample markdown files."""
    d = tmp_path / "content"
    d.mkdir()

    # A published page with a title
    (d / "page-a.md").write_text(
        "---\ntitle: Page A\npublish: true\ntags: [foo, bar]\ndate: 2024-01-01\n---\n"
        "Some content with a link to [[Page B]].\n"
    )

    # Another published page (linked from page-a)
    (d / "page-b.md").write_text(
        "---\ntitle: Page B\npublish: true\n---\nContent of Page B.\n"
    )

    # An orphan page (no other page links to it)
    (d / "orphan.md").write_text(
        "---\ntitle: Orphan Page\npublish: true\ntags: [lonely]\ndate: 2024-06-15\n---\n"
        "Nobody links here.\n"
    )

    # An unpublished page (should be excluded everywhere)
    (d / "draft.md").write_text(
        "---\ntitle: Draft Page\npublish: false\n---\nNot published.\n"
    )

    # Index page (never counted as orphan)
    (d / "index.md").write_text(
        "---\ntitle: Home\npublish: true\n---\nWelcome.\n"
    )

    return d


@pytest.fixture
def public_dir(tmp_path):
    """Temp public directory with sample static files."""
    d = tmp_path / "public"
    d.mkdir()
    (d / "index.html").write_text("<html><body>Home</body></html>")

    sub = d / "about"
    sub.mkdir()
    (sub / "index.html").write_text("<html><body>About</body></html>")

    (d / "style.css").write_text("body { color: black; }")

    return d
