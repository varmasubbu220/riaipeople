import anyio
import asyncio
from email.message import EmailMessage
import aiosmtplib

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465  # Change to 465 for SMTPS (secure)
SMTP_USERNAME = "lallipriya2003@gmail.com"
SMTP_PASSWORD = "zjtltlzqjwmuydvm"  # Use Google App Password
SENDER_EMAIL = "lallipriya2003@gmail.com"

async def send_email(to_email: str, subject: str, plain_text: str, html_content: str = None):
    message = EmailMessage()
    message["From"] = SENDER_EMAIL
    message["To"] = to_email
    message["Subject"] = subject

    # Add plain text version
    message.set_content(plain_text)

    # Add HTML version (if provided)
    if html_content:
        message.add_alternative(html_content, subtype="html")

    try:
        await aiosmtplib.send(
            message,
            hostname=SMTP_SERVER,
            port=SMTP_PORT,
            username=SMTP_USERNAME,
            password=SMTP_PASSWORD,
            use_tls=True,  # True for SMTPS (secure)
            start_tls=False,  # False for direct TLS connection
        )
        print("✅ Email sent successfully")
        return {"message": "Email sent successfully"}
    except Exception as e:
        print("❌ Error sending email:", e)
        return {"error": str(e)}