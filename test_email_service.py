"""
Unit and Integration Tests for EmailService
"""
import unittest
from unittest.mock import MagicMock, patch
import smtplib
import socket
import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.email_service import EmailService, email_service



class TestEmailService(unittest.TestCase):

    def setUp(self):
        self.service = EmailService(
            host="smtp.test.com",
            port=587,
            username="user@test.com",
            password="secret_password",
            use_tls=True,
            use_ssl=False,
            from_email="sender@test.com",
            from_name="Test Sender",
            timeout=5
        )

    # -------------------------------------------------------------------------
    # Input Validation Tests
    # -------------------------------------------------------------------------
    def test_email_validation_valid(self):
        valid_emails = [
            "user@example.com",
            "john.doe@company.co.uk",
            "admin+test@domain.org",
            "user.name123@sub.domain.net"
        ]
        for email in valid_emails:
            self.assertTrue(
                EmailService.validate_email(email),
                f"Expected email '{email}' to be valid."
            )

    def test_email_validation_invalid(self):
        invalid_emails = [
            "",
            "plainaddress",
            "@missinguser.com",
            "user@.com",
            "user@domain",
            "user@domain..com",
            None
        ]
        for email in invalid_emails:
            self.assertFalse(
                EmailService.validate_email(email),
                f"Expected email '{email}' to be invalid."
            )

    def test_send_email_invalid_recipient(self):
        res = self.service.send_email(
            to_email="invalid-email-format",
            subject="Test Subject",
            body_text="Test Body"
        )
        self.assertFalse(res["success"])
        self.assertIn("Invalid target email address", res["error"])

    def test_send_email_empty_subject(self):
        res = self.service.send_email(
            to_email="user@example.com",
            subject="  ",
            body_text="Test Body"
        )
        self.assertFalse(res["success"])
        self.assertIn("subject cannot be empty", res["error"])

    def test_send_email_empty_body(self):
        res = self.service.send_email(
            to_email="user@example.com",
            subject="Test Subject",
            body_text=""
        )
        self.assertFalse(res["success"])
        self.assertIn("body cannot be empty", res["error"])

    # -------------------------------------------------------------------------
    # SMTP Connection & Sending Mock Tests
    # -------------------------------------------------------------------------
    @patch("smtplib.SMTP")
    def test_send_email_success_tls(self, mock_smtp_class):
        mock_instance = MagicMock()
        mock_instance.__enter__.return_value = mock_instance
        mock_smtp_class.return_value = mock_instance

        res = self.service.send_email(
            to_email="recipient@example.com",
            subject="Hello World",
            body_text="This is plain text.",
            body_html="<p>This is HTML.</p>"
        )

        self.assertTrue(res["success"])
        self.assertNotEqual(res["message_id"], "")
        self.assertEqual(res["error"], "")

        # Verify SMTP setup calls
        mock_smtp_class.assert_called_once_with("smtp.test.com", 587, timeout=5)
        mock_instance.starttls.assert_called_once()
        mock_instance.login.assert_called_once_with("user@test.com", "secret_password")
        mock_instance.send_message.assert_called_once()

    @patch("smtplib.SMTP_SSL")
    def test_send_email_success_ssl(self, mock_smtp_ssl_class):
        ssl_service = EmailService(
            host="smtp.test.com",
            port=465,
            username="user@test.com",
            password="secret_password",
            use_tls=False,
            use_ssl=True,
            from_email="sender@test.com",
            from_name="Test Sender"
        )

        mock_instance = MagicMock()
        mock_instance.__enter__.return_value = mock_instance
        mock_smtp_ssl_class.return_value = mock_instance

        res = ssl_service.send_email(
            to_email="recipient@example.com",
            subject="SSL Test",
            body_text="Plain text"
        )

        self.assertTrue(res["success"])
        mock_smtp_ssl_class.assert_called_once()
        mock_instance.login.assert_called_once_with("user@test.com", "secret_password")

    @patch("smtplib.SMTP")
    def test_send_email_auth_error(self, mock_smtp_class):
        mock_instance = MagicMock()
        mock_instance.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Authentication failed")
        mock_instance.__enter__.return_value = mock_instance
        mock_smtp_class.return_value = mock_instance

        res = self.service.send_email(
            to_email="recipient@example.com",
            subject="Auth Failure Test",
            body_text="Content"
        )

        self.assertFalse(res["success"])
        self.assertIn("SMTP Authentication failed", res["error"])

    @patch("smtplib.SMTP")
    def test_send_email_timeout(self, mock_smtp_class):
        mock_smtp_class.side_effect = socket.timeout("Timed out connecting to server")

        res = self.service.send_email(
            to_email="recipient@example.com",
            subject="Timeout Test",
            body_text="Content"
        )

        self.assertFalse(res["success"])
        self.assertIn("Connection timeout", res["error"])

    # -------------------------------------------------------------------------
    # Templated Email Helper Tests
    # -------------------------------------------------------------------------
    @patch.object(EmailService, "send_email")
    def test_send_welcome_email(self, mock_send):
        mock_send.return_value = {"success": True, "message_id": "<msg1>", "error": ""}

        res = self.service.send_welcome_email(
            to_email="newuser@example.com",
            username="Alice",
            login_url="https://portal.example.com/login"
        )

        self.assertTrue(res["success"])
        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        self.assertEqual(args[0], "newuser@example.com")
        self.assertIn("Welcome to Security Intelligence Platform, Alice!", args[1])
        self.assertIn("Alice", args[2])
        self.assertIn("https://portal.example.com/login", args[3])

    @patch.object(EmailService, "send_email")
    def test_send_password_reset_email(self, mock_send):
        mock_send.return_value = {"success": True, "message_id": "<msg2>", "error": ""}

        res = self.service.send_password_reset_email(
            to_email="user@example.com",
            username="Bob",
            reset_link_or_token="token_xyz_123",
            expire_minutes=30
        )

        self.assertTrue(res["success"])
        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        self.assertEqual(args[0], "user@example.com")
        self.assertIn("Action Required: Password Reset Request", args[1])
        self.assertIn("token_xyz_123", args[2])
        self.assertIn("30 minutes", args[3])

    @patch.object(EmailService, "send_email")
    def test_send_notification_email(self, mock_send):
        mock_send.return_value = {"success": True, "message_id": "<msg3>", "error": ""}

        res = self.service.send_notification_email(
            to_email="admin@example.com",
            title="High Severity Threat Detected",
            message="Threat Actor 'APT29' activity detected on IP 192.168.1.50",
            action_url="https://portal.example.com/alerts/101",
            action_text="Investigate Alert"
        )

        self.assertTrue(res["success"])
        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        self.assertEqual(args[0], "admin@example.com")
        self.assertIn("High Severity Threat Detected", args[1])
        self.assertIn("APT29", args[2])
        self.assertIn("https://portal.example.com/alerts/101", args[3])


if __name__ == "__main__":
    unittest.main()
