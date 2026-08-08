import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from langchain_core.tools import tool

@tool
def send_email_report(
    recipient_email: str,
    subject: str,
    body: str,
    attachment_path: str = "",
    gmail_user: str = "",
    gmail_password: str = ""
) -> str:
    """
    Sends an investment report email to a client or stakeholder via Gmail SMTP.
    Inputs:
        recipient_email: Target email address
        subject: Subject line for the email
        body: Plain text or markdown email body
        attachment_path: (Optional) local file path to PDF/TXT report to attach
        gmail_user: (Optional) Sender Gmail address
        gmail_password: (Optional) 16-character Gmail App Password
    """
    user = gmail_user or os.getenv("GMAIL_USER", "")
    password = gmail_password or os.getenv("GMAIL_APP_PASSWORD", "")

    if not user or not password:
        return (
            "⚠️ Gmail credentials missing.\n\n"
            "To send emails directly from the application:\n"
            "1. Enter your Sender Gmail Address (e.g. `yourname@gmail.com`) and 16-character Gmail App Password in the settings or dispatch form.\n"
            "2. Note: To generate a 16-character App Password, go to Google Account Settings -> Security -> 2-Step Verification -> App Passwords."
        )

    try:
        msg = MIMEMultipart()
        msg["From"] = user
        msg["To"] = recipient_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as f:
                filename = os.path.basename(attachment_path)
                attachment = MIMEApplication(f.read(), Name=filename)
                attachment["Content-Disposition"] = f'attachment; filename="{filename}"'
                msg.attach(attachment)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(user, password)
            server.send_message(msg)

        return f"✅ Successfully sent email report to {recipient_email} with subject '{subject}'!"

    except Exception as e:
        return f"❌ Failed to send email: {str(e)}"
