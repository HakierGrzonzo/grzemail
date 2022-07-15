import asyncio
import logging
from email.mime.text import MIMEText
from .services import config_class as config

logging.basicConfig(level=logging.DEBUG)

emails = config.get_email_accounts()

loop = asyncio.get_event_loop()
loop.run_until_complete(emails[0].get_mail())
