"""
Interactive / Standalone Demonstration Script for SMTP Email Service
Usage: python demo_email.py --to recipient@example.com --type welcome|reset|notification
"""
import sys
import os
import argparse

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.email_service import email_service


def main():
    parser = argparse.ArgumentParser(description="Send a demo email using SMTP Email Service")
    parser.add_argument("--to", required=True, help="Recipient email address")
    parser.add_argument(
        "--type",
        choices=["welcome", "reset", "notification"],
        default="welcome",
        help="Type of email to send (welcome, reset, notification)"
    )

    args = parser.parse_args()

    print(f"📧 Sending '{args.type}' email to: {args.to}...")
    print(f"⚙️ Using SMTP Server: {email_service.host}:{email_service.port} (TLS={email_service.use_tls}, SSL={email_service.use_ssl})")

    if args.type == "welcome":
        result = email_service.send_welcome_email(
            to_email=args.to,
            username="Demo User",
            login_url="http://localhost:5000/login"
        )
    elif args.type == "reset":
        result = email_service.send_password_reset_email(
            to_email=args.to,
            username="Demo User",
            reset_link_or_token="DEMO-RESET-TOKEN-12345",
            expire_minutes=30
        )
    elif args.type == "notification":
        result = email_service.send_notification_email(
            to_email=args.to,
            title="High-Severity Threat IOC Detected",
            message="Threat Actor 'APT29' activity detected on IP 192.168.1.50.",
            action_url="http://localhost:5000/api/threats/101",
            action_text="View Intelligence Report"
        )

    if result["success"]:
        print(f"✅ Success! Email sent cleanly.")
        print(f"   Message ID: {result['message_id']}")
    else:
        print(f"❌ Failed to send email:")
        print(f"   Error: {result['error']}")
        print("\n💡 Tip: Copy .env.example to .env and configure your real SMTP credentials.")


if __name__ == "__main__":
    main()
