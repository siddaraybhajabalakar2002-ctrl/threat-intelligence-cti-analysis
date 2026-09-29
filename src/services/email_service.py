"""
Reusable SMTP Email Service with TLS/SSL Support, Input Validation,
HTML/Text Templating, and Robust Error Handling.
"""
import os
import re
import ssl
import smtplib
import logging
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr, make_msgid, formatdate
from typing import Optional, Dict, Any

try:
    from dotenv import load_dotenv
    # Load .env from project root
    _proj_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    _env_file = os.path.join(_proj_root, ".env")
    if os.path.exists(_env_file):
        load_dotenv(_env_file, override=False)
    else:
        load_dotenv(override=False)
except ImportError:
    pass

# Configure logger for email service
logger = logging.getLogger("EmailService")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Strict RFC 5322 compatible email validation regex pattern
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$')


class EmailService:
    """
    Modular, reusable SMTP Email Service supporting TLS/SSL encryption,
    template rendering, input validation, and detailed logging.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_tls: Optional[bool] = None,
        use_ssl: Optional[bool] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        timeout: Optional[int] = None
    ):
        """
        Initialize EmailService with credentials or read from environment variables.
        """
        self.host = host or os.getenv("SMTP_HOST", "localhost")
        self.port = int(port or os.getenv("SMTP_PORT", "587"))
        self.username = username if username is not None else os.getenv("SMTP_USERNAME", "")
        self.password = password if password is not None else os.getenv("SMTP_PASSWORD", "")
        
        # Security options: TLS (STARTTLS) vs SSL (implicit)
        env_tls = os.getenv("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes")
        env_ssl = os.getenv("SMTP_USE_SSL", "false").lower() in ("true", "1", "yes")
        self.use_tls = use_tls if use_tls is not None else env_tls
        self.use_ssl = use_ssl if use_ssl is not None else env_ssl

        self.from_email = from_email or os.getenv("SMTP_FROM_EMAIL", "noreply@example.com")
        self.from_name = from_name or os.getenv("SMTP_FROM_NAME", "Security Alert System")
        self.timeout = int(timeout or os.getenv("SMTP_TIMEOUT", "30"))

    @staticmethod
    def validate_email(email_address: str) -> bool:
        """
        Validate recipient or sender email address format.
        """
        if not email_address or not isinstance(email_address, str):
            return False
        return bool(EMAIL_REGEX.match(email_address.strip()))

    def _create_smtp_connection(self):
        """
        Establish a secure SMTP or SMTP_SSL connection based on instance settings.
        Returns active SMTP connection object.
        """
        context = ssl.create_default_context()

        if self.use_ssl:
            logger.debug(f"Connecting to SMTP SSL server {self.host}:{self.port}")
            server = smtplib.SMTP_SSL(self.host, self.port, timeout=self.timeout, context=context)
        else:
            logger.debug(f"Connecting to SMTP server {self.host}:{self.port}")
            server = smtplib.SMTP(self.host, self.port, timeout=self.timeout)
            if self.use_tls:
                logger.debug("Initiating STARTTLS extension...")
                server.starttls(context=context)

        if self.username and self.password:
            logger.debug(f"Authenticating as {self.username}")
            server.login(self.username, self.password)

        return server

    def send_email(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        reply_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a general email with text and optional HTML content.

        :param to_email: Target email address.
        :param subject: Email subject line.
        :param body_text: Plain text fallback email body.
        :param body_html: HTML email body (optional).
        :param reply_to: Reply-To email address (optional).
        :return: Dict containing execution result: {'success': bool, 'message_id': str, 'error': str}
        """
        # 1. Input Validation
        if not self.validate_email(to_email):
            error_msg = f"Invalid target email address provided: '{to_email}'"
            logger.error(error_msg)
            return {"success": False, "message_id": "", "error": error_msg}

        if not subject or not subject.strip():
            error_msg = "Email subject cannot be empty."
            logger.error(error_msg)
            return {"success": False, "message_id": "", "error": error_msg}

        if not body_text or not body_text.strip():
            error_msg = "Email plain text body cannot be empty."
            logger.error(error_msg)
            return {"success": False, "message_id": "", "error": error_msg}

        # 2. Construct Multipart Message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject.strip()
        msg["From"] = formataddr((self.from_name, self.from_email))
        msg["To"] = to_email.strip()
        msg["Date"] = formatdate(localtime=True)
        message_id = make_msgid()
        msg["Message-ID"] = message_id

        if reply_to and self.validate_email(reply_to):
            msg["Reply-To"] = reply_to.strip()

        # Attach plain text part
        text_part = MIMEText(body_text, "plain", "utf-8")
        msg.attach(text_part)

        # Attach HTML part if available
        if body_html:
            html_part = MIMEText(body_html, "html", "utf-8")
            msg.attach(html_part)

        # 3. SMTP Dispatch with error handling
        try:
            with self._create_smtp_connection() as server:
                server.send_message(msg)
            
            logger.info(f"Email successfully sent to {to_email} [Subject: '{subject}']")
            return {"success": True, "message_id": message_id, "error": ""}

        except smtplib.SMTPAuthenticationError as e:
            err = f"SMTP Authentication failed for user '{self.username}': {e.smtp_error.decode('utf-8', errors='ignore') if isinstance(e.smtp_error, bytes) else str(e)}"
            logger.error(err)
            return {"success": False, "message_id": message_id, "error": err}

        except smtplib.SMTPConnectError as e:
            err = f"Failed to connect to SMTP server '{self.host}:{self.port}': {e}"
            logger.error(err)
            return {"success": False, "message_id": message_id, "error": err}

        except (socket.timeout, TimeoutError) as e:
            err = f"Connection timeout ({self.timeout}s) while reaching SMTP server '{self.host}:{self.port}': {e}"
            logger.error(err)
            return {"success": False, "message_id": message_id, "error": err}

        except ssl.SSLError as e:
            err = f"SSL/TLS security negotiation error with host '{self.host}': {e}"
            logger.error(err)
            return {"success": False, "message_id": message_id, "error": err}

        except smtplib.SMTPException as e:
            err = f"SMTP protocol error sending to '{to_email}': {e}"
            logger.error(err)
            return {"success": False, "message_id": message_id, "error": err}

        except Exception as e:
            err = f"Unexpected error during email transmission to '{to_email}': {e}"
            logger.error(err)
            return {"success": False, "message_id": message_id, "error": err}

    # =========================================================================
    # PRE-BUILT TEMPLATED EMAIL FUNCTIONS
    # =========================================================================

    def send_welcome_email(
        self,
        to_email: str,
        username: str,
        login_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a welcome email to a new user.

        :param to_email: Recipient's email address.
        :param username: Recipient's user name.
        :param login_url: Optional URL for signing into the platform.
        """
        subject = f"Welcome to Security Intelligence Platform, {username}!"
        login_url = login_url or "https://example.com/login"

        body_text = (
            f"Hello {username},\n\n"
            f"Welcome to the Security Intelligence & Threat Analysis Platform!\n"
            f"We are excited to have you on board. Your account is now active.\n\n"
            f"You can log in and access your portal here:\n{login_url}\n\n"
            f"Best regards,\n"
            f"The Security Operations Team"
        )

        body_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; color: #333; }}
            .card {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border: 1px solid #e1e8ed; }}
            .header {{ background: linear-gradient(135deg, #1e293b, #0f172a); padding: 30px; text-align: center; color: #ffffff; }}
            .header h1 {{ margin: 0; font-size: 24px; font-weight: 600; letter-spacing: 0.5px; }}
            .content {{ padding: 30px; line-height: 1.6; font-size: 15px; color: #475569; }}
            .cta-button {{ display: inline-block; padding: 12px 28px; background-color: #2563eb; color: #ffffff !important; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 20px 0; }}
            .footer {{ background-color: #f8fafc; padding: 20px; text-align: center; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; }}
          </style>
        </head>
        <body>
          <div class="card">
            <div class="header">
              <h1>🛡️ Welcome Aboard</h1>
            </div>
            <div class="content">
              <p>Hello <strong>{username}</strong>,</p>
              <p>Welcome to the <strong>Security Intelligence & Threat Analysis Platform</strong>! We are thrilled to have you join our threat analysis ecosystem.</p>
              <p>Your account is fully activated and ready. Click below to sign in and explore the interactive dashboard:</p>
              <div style="text-align: center;">
                <a href="{login_url}" class="cta-button">Go to Login Portal</a>
              </div>
              <p>If you have any questions or need assistance setting up your pipeline, please reach out to our security support team.</p>
              <p>Best regards,<br><strong>The Security Operations Team</strong></p>
            </div>
            <div class="footer">
              &copy; Security Intelligence Platform &bull; Automated System Notification
            </div>
          </div>
        </body>
        </html>
        """
        return self.send_email(to_email, subject, body_text, body_html)

    def send_password_reset_email(
        self,
        to_email: str,
        username: str,
        reset_link_or_token: str,
        expire_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Send a password reset link or token to a user.

        :param to_email: Target user's email.
        :param username: Target user's name.
        :param reset_link_or_token: Direct reset URL or token code.
        :param expire_minutes: Minutes until link expires (default 60).
        """
        subject = "Action Required: Password Reset Request"
        
        if reset_link_or_token.startswith("http://") or reset_link_or_token.startswith("https://"):
            reset_url = reset_link_or_token
        else:
            reset_url = f"https://example.com/reset-password?token={reset_link_or_token}"

        body_text = (
            f"Hello {username},\n\n"
            f"We received a request to reset your password for your account.\n"
            f"Click the link below to reset your password (valid for {expire_minutes} minutes):\n\n"
            f"{reset_url}\n\n"
            f"If you did not request a password reset, please ignore this email or contact security support immediately.\n\n"
            f"Best regards,\n"
            f"The Security Operations Team"
        )

        body_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; color: #333; }}
            .card {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border: 1px solid #e1e8ed; }}
            .header {{ background: linear-gradient(135deg, #dc2626, #991b1b); padding: 30px; text-align: center; color: #ffffff; }}
            .header h1 {{ margin: 0; font-size: 24px; font-weight: 600; letter-spacing: 0.5px; }}
            .content {{ padding: 30px; line-height: 1.6; font-size: 15px; color: #475569; }}
            .cta-button {{ display: inline-block; padding: 12px 28px; background-color: #dc2626; color: #ffffff !important; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 20px 0; }}
            .warning-box {{ background-color: #fef2f2; border-left: 4px solid #ef4444; padding: 12px 16px; margin: 20px 0; font-size: 13px; color: #991b1b; }}
            .footer {{ background-color: #f8fafc; padding: 20px; text-align: center; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; }}
          </style>
        </head>
        <body>
          <div class="card">
            <div class="header">
              <h1>🔑 Password Reset Request</h1>
            </div>
            <div class="content">
              <p>Hello <strong>{username}</strong>,</p>
              <p>We received a request to reset the password associated with your account.</p>
              <div style="text-align: center;">
                <a href="{reset_url}" class="cta-button">Reset Your Password</a>
              </div>
              <div class="warning-box">
                ⏱️ <strong>Security Notice:</strong> This password reset link will expire in <strong>{expire_minutes} minutes</strong>.
              </div>
              <p>If you did not initiate this request, no action is required and your password remains secure. However, we recommend reviewing your account security settings.</p>
              <p>Best regards,<br><strong>The Security Operations Team</strong></p>
            </div>
            <div class="footer">
              &copy; Security Intelligence Platform &bull; Automated Security Alert
            </div>
          </div>
        </body>
        </html>
        """
        return self.send_email(to_email, subject, body_text, body_html)

    def send_notification_email(
        self,
        to_email: str,
        title: str,
        message: str,
        action_url: Optional[str] = None,
        action_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a generic notification or security alert email.

        :param to_email: Recipient's email address.
        :param title: Notification title / subject.
        :param message: Main message content.
        :param action_url: Optional call-to-action button URL.
        :param action_text: Optional call-to-action button label.
        """
        subject = f"Notification: {title}"

        action_section_text = ""
        action_section_html = ""

        if action_url:
            button_label = action_text or "View Details"
            action_section_text = f"\n\nLink: {action_url}"
            action_section_html = f"""
              <div style="text-align: center;">
                <a href="{action_url}" class="cta-button">{button_label}</a>
              </div>
            """

        body_text = (
            f"Security Notification: {title}\n"
            f"----------------------------------------\n\n"
            f"{message}"
            f"{action_section_text}\n\n"
            f"Best regards,\n"
            f"The Security Operations Team"
        )

        body_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; color: #333; }}
            .card {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border: 1px solid #e1e8ed; }}
            .header {{ background: linear-gradient(135deg, #0284c7, #0369a1); padding: 25px; text-align: center; color: #ffffff; }}
            .header h1 {{ margin: 0; font-size: 22px; font-weight: 600; }}
            .content {{ padding: 30px; line-height: 1.6; font-size: 15px; color: #334155; }}
            .message-box {{ background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 16px; margin: 15px 0; white-space: pre-wrap; font-size: 14px; color: #1e293b; }}
            .cta-button {{ display: inline-block; padding: 12px 28px; background-color: #0284c7; color: #ffffff !important; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 20px 0; }}
            .footer {{ background-color: #f8fafc; padding: 20px; text-align: center; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; }}
          </style>
        </head>
        <body>
          <div class="card">
            <div class="header">
              <h1>🔔 System Notification</h1>
            </div>
            <div class="content">
              <h3 style="margin-top:0; color:#0f172a;">{title}</h3>
              <div class="message-box">{message}</div>
              {action_section_html}
              <p>Best regards,<br><strong>The Security Operations Team</strong></p>
            </div>
            <div class="footer">
              &copy; Security Intelligence Platform &bull; Automated System Notification
            </div>
          </div>
        </body>
        </html>
        """
        return self.send_email(to_email, subject, body_text, body_html)


# Create a module-level singleton instance reading default environment variables
email_service = EmailService()
