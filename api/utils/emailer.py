# emailer.py
import asyncio
import os

import aiosmtplib
from email.message import EmailMessage
from typing import Optional

SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "false").lower() == "true"
SMTP_USE_SSL = os.getenv("SMTP_USE_SSL", "false").lower() == "  true"
FROM_EMAIL = os.getenv("FROM_EMAIL", "no-reply@example.test")
FROM_NAME  = os.getenv("FROM_NAME", "Summarizer app")

def _msg(to_email: str, subject: str, html: str, text_fallback: Optional[str] = None):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg["To"] = to_email
    # Simple text fallback (optional)
    msg.set_content(text_fallback or "Open this link in a browser.")
    # HTML part
    msg.add_alternative(html, subtype="html")
    return msg

async def send_email_async(to_email: str, subject: str, html: str, text_fallback: Optional[str] = None):
    msg = _msg(to_email, subject, html, text_fallback)
    if SMTP_USE_SSL:
        await aiosmtplib.send(
            msg, hostname=SMTP_HOST, port=SMTP_PORT,
            username=SMTP_USER, password=SMTP_PASS, use_tls=True
        )
    else:
        await aiosmtplib.send(
            msg, hostname=SMTP_HOST, port=SMTP_PORT,
            username=SMTP_USER or None, password=SMTP_PASS or None,
            start_tls=SMTP_USE_TLS
        )

def send_email(*args, **kwargs):
    return asyncio.run(send_email_async(*args, **kwargs))