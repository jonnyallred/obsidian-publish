from unittest.mock import patch

import responses

from email_service import is_valid_email, send_magic_link


class TestIsValidEmail:
    def test_valid(self):
        assert is_valid_email("user@example.com") is True

    def test_no_at(self):
        assert is_valid_email("userexample.com") is False

    def test_no_dot_in_domain(self):
        assert is_valid_email("user@example") is False

    def test_empty_string(self):
        assert is_valid_email("") is False

    def test_multiple_at_signs(self):
        assert is_valid_email("user@@example.com") is False


class TestSendMagicLink:
    @responses.activate
    def test_success(self, monkeypatch):
        monkeypatch.setattr("config.Config.MAILGUN_API_KEY", "test-key")
        monkeypatch.setattr("config.Config.MAILGUN_DOMAIN", "mg.example.com")

        responses.add(
            responses.POST,
            "https://api.mailgun.net/v3/mg.example.com/messages",
            status=200,
            json={"id": "<msg-id>", "message": "Queued"},
        )

        result = send_magic_link("user@example.com", "https://example.com/auth/verify/tok123")
        assert result is True

    @responses.activate
    def test_api_failure(self, monkeypatch):
        monkeypatch.setattr("config.Config.MAILGUN_API_KEY", "test-key")
        monkeypatch.setattr("config.Config.MAILGUN_DOMAIN", "mg.example.com")

        responses.add(
            responses.POST,
            "https://api.mailgun.net/v3/mg.example.com/messages",
            status=500,
            json={"message": "Internal error"},
        )

        result = send_magic_link("user@example.com", "https://example.com/auth/verify/tok123")
        assert result is False

    def test_missing_credentials(self, monkeypatch):
        monkeypatch.setattr("config.Config.MAILGUN_API_KEY", "")
        monkeypatch.setattr("config.Config.MAILGUN_DOMAIN", "")

        result = send_magic_link("user@example.com", "https://example.com/auth/verify/tok123")
        assert result is False
