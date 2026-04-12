"""
Email service — PurelyMail via SMTP (aiosmtplib).
"""
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.settings import settings


async def send_daily_report(to_address: str, subject: str, body_html: str, body_text: str = "") -> None:
    """Send the daily report email."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.FROM_EMAIL
    msg["To"] = to_address

    if body_text:
        msg.attach(MIMEText(body_text, "plain"))
    msg.attach(MIMEText(body_html, "html"))

    await aiosmtplib.send(
        msg,
        hostname=settings.PURELYMAIL_SMTP_HOST,
        port=settings.PURELYMAIL_SMTP_PORT,
        username=settings.FROM_EMAIL,
        password=settings.PURELYMAIL_API_TOKEN,
        start_tls=True,
    )
