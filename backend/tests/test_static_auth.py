import os
from unittest.mock import patch

from models import Session


class TestUnauthenticatedAccess:
    def test_redirect_to_login(self, client, test_db):
        resp = client.get("/")
        assert resp.status_code == 302
        assert "/auth/login" in resp.headers["Location"]

    def test_subpath_redirect(self, client, test_db):
        resp = client.get("/some/page")
        assert resp.status_code == 302
        assert "/auth/login" in resp.headers["Location"]


class TestAuthenticatedAccess:
    def _patch_public_dir(self, public_dir):
        """Return a patch that makes serve_protected_static resolve to our temp public_dir."""
        real_join = os.path.join
        real_abspath = os.path.abspath

        def patched_join(*args):
            # Intercept the join that builds public_dir path
            # static_auth does: os.path.join(os.path.dirname(__file__), '..', 'public')
            if len(args) == 3 and args[1] == ".." and args[2] == "public":
                return str(public_dir)
            return real_join(*args)

        return patch("static_auth.os.path.join", side_effect=patched_join)

    def test_serves_file(self, authenticated_client, public_dir, test_db):
        with self._patch_public_dir(public_dir):
            resp = authenticated_client.get("/style.css")
            assert resp.status_code == 200
            assert b"body" in resp.data

    def test_directory_serves_index(self, authenticated_client, public_dir, test_db):
        with self._patch_public_dir(public_dir):
            resp = authenticated_client.get("/about")
            assert resp.status_code == 200
            assert b"About" in resp.data

    def test_missing_file_fallback(self, authenticated_client, public_dir, test_db):
        with self._patch_public_dir(public_dir):
            resp = authenticated_client.get("/nonexistent.html")
            assert resp.status_code == 200
            # Should fall back to index.html
            assert b"Home" in resp.data


class TestDirectoryTraversal:
    def _patch_public_dir(self, public_dir):
        real_join = os.path.join

        def patched_join(*args):
            if len(args) == 3 and args[1] == ".." and args[2] == "public":
                return str(public_dir)
            return real_join(*args)

        return patch("static_auth.os.path.join", side_effect=patched_join)

    def test_traversal_blocked(self, authenticated_client, public_dir, test_db):
        with self._patch_public_dir(public_dir):
            resp = authenticated_client.get("/../../etc/passwd")
            # Flask normalizes paths, but the security check should prevent escape
            assert resp.status_code in (200, 403, 404)
            if resp.status_code == 200:
                # If 200, it should be the fallback index, not /etc/passwd
                assert b"root:" not in resp.data


class TestIsAuthenticated:
    def test_no_session(self, app, test_db):
        with app.test_request_context():
            from static_auth import is_authenticated

            assert is_authenticated() is False

    def test_invalid_session(self, app, test_db):
        with app.test_request_context():
            from flask import session

            session["session_id"] = "nonexistent-id"
            from static_auth import is_authenticated

            assert is_authenticated() is False

    def test_valid_session(self, app, test_db):
        sid = Session.create("user@example.com")
        with app.test_request_context():
            from flask import session
            from static_auth import is_authenticated

            session["session_id"] = sid
            assert is_authenticated() is True
