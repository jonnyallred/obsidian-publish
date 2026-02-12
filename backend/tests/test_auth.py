from unittest.mock import patch

from models import MagicLink, Session


class TestLoginPage:
    def test_get_login(self, client):
        resp = client.get("/auth/login")
        assert resp.status_code == 200


class TestRequestLink:
    def test_valid_email(self, client, test_db):
        with patch("auth.send_magic_link", return_value=True) as mock_send:
            resp = client.post(
                "/auth/request-link",
                data={"email": "user@example.com"},
            )
        assert resp.status_code == 200
        assert b"Check Your Email" in resp.data or b"check" in resp.data.lower()
        mock_send.assert_called_once()

    def test_invalid_email(self, client, test_db):
        resp = client.post(
            "/auth/request-link",
            data={"email": "not-an-email"},
        )
        assert resp.status_code == 400

    def test_empty_email(self, client, test_db):
        resp = client.post(
            "/auth/request-link",
            data={"email": ""},
        )
        assert resp.status_code == 400

    def test_send_failure(self, client, test_db):
        with patch("auth.send_magic_link", return_value=False):
            resp = client.post(
                "/auth/request-link",
                data={"email": "user@example.com"},
            )
        assert resp.status_code == 500


class TestVerifyToken:
    def test_valid_token(self, client, test_db):
        token = MagicLink.create("user@example.com")
        resp = client.get(f"/auth/verify/{token}")
        assert resp.status_code == 302
        assert resp.headers["Location"] == "/"

    def test_invalid_token(self, client, test_db):
        resp = client.get("/auth/verify/bogus-token")
        assert resp.status_code == 400

    def test_used_token(self, client, test_db):
        token = MagicLink.create("user@example.com")
        MagicLink.mark_used(token)
        resp = client.get(f"/auth/verify/{token}")
        assert resp.status_code == 400

    def test_verify_sets_session(self, client, test_db):
        token = MagicLink.create("user@example.com")
        client.get(f"/auth/verify/{token}")

        with client.session_transaction() as sess:
            assert "session_id" in sess
            assert sess["email"] == "user@example.com"


class TestLogout:
    def test_logout_clears_session(self, authenticated_client, test_db):
        resp = authenticated_client.post("/auth/logout")
        assert resp.status_code == 302
        assert "/auth/login" in resp.headers["Location"]

        with authenticated_client.session_transaction() as sess:
            assert "session_id" not in sess

    def test_logout_without_session(self, client, test_db):
        resp = client.post("/auth/logout")
        assert resp.status_code == 302
