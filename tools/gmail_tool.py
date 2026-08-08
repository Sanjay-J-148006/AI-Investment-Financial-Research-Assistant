import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from langchain_core.tools import tool

@tool
def send_email_report(recipient_email: str, subject: str, body: str, attachment_path: str = "") -> str:
    """
    Sends an investment report email to a client or stakeholder.
    Inputs:
        recipient_email: Target email address
        subject: Subject line for the email
        body: Plain text or markdown email body
        attachment_path: (Optional) local file path to PDF/TXT report to attach
    """
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")

    if not gmail_user or not gmail_password:
        return (
            "Gmail credentials missing. Please set GMAIL_USER and GMAIL_APP_PASSWORD in your .env file "
            "or sidebar settings to send emails."
        )

    try:
        msg = MIMEMultipart()
        msg["From"] = gmail_user
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
            server.login(gmail_user, gmail_password)
            server.send_message(msg)

        return f"Successfully sent email report to {recipient_email} with subject '{subject}'."

    except Exception as e:
        return f"Failed to send email: {str(e)}"
