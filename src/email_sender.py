# src/email_sender.py

import os
import logging

# Configure logging to show all messages
logging.basicConfig(level=logging.INFO)

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, To
from dotenv import load_dotenv

# Force reload environment variables
load_dotenv(override=True)

# Debug .env file contents
with open('.env', 'r') as f:
    logging.info("Contents of .env file:")
    logging.info(f.read())


def send_email(html_content: str) -> None:
    """
    Sends an HTML email using SendGrid with proper error handling, delivery tracking,
    and recipient management.

    Args:
        html_content (str): The HTML content of the email.
    """
    logging.info("Starting email send process...")
    
    # Debug environment variables
    logging.info("Environment variables:")
    logging.info(f"SENDER_EMAIL: {os.environ.get('SENDER_EMAIL')}")
    logging.info(f"RECIPIENTS: {os.environ.get('RECIPIENTS')}")
    
    sender = os.getenv("SENDER_EMAIL", "no-reply@example.com")
    logging.info(f"Using sender email: {sender}")
    subject = os.getenv(
        "EMAIL_SUBJECT", "Greater Dandenong Council Newsletter")

    # Retrieve recipients from a comma-separated environment variable.
    recipients_str = os.getenv("RECIPIENTS", "")
    if not recipients_str:
        logging.error("No recipients specified in environment variables.")
        return

    recipients = [email.strip()
                  for email in recipients_str.split(",") if email.strip()]
    
    logging.info(f"Sending to recipients: {recipients}")

    message = Mail(
        from_email=sender,
        to_emails=[To(email) for email in recipients],
        subject=subject,
        html_content=html_content
    )

    try:
        api_key = os.getenv("SENDGRID_API_KEY")
        if not api_key:
            logging.error("SendGrid API key is missing")
            return
        
        logging.info("Initializing SendGrid client...")
        sg = SendGridAPIClient(api_key)
        
        logging.info("Attempting to send email...")
        response = sg.send(message)
        
        logging.info("Email sent successfully. Status Code: %s, Message ID: %s",
                     response.status_code,
                     response.headers.get("X-Message-Id", "N/A"))
    except Exception as e:
        logging.error("Error sending email: %s", str(e))
        if hasattr(e, 'body'):
            logging.error("Detailed error: %s", e.body)


if __name__ == "__main__":
    # Define a simple HTML content for testing.
    sample_html = """
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>Test Email</title>
      </head>
      <body>
        <h1>This is a test email!</h1>
        <p>If you received this email, the email_sender module is working correctly.</p>
      </body>
    </html>
    """
    send_email(sample_html)
