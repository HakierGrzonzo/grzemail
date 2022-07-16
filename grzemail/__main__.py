import asyncio
import logging
from .services import config_class as config

logging.basicConfig(level=logging.INFO)

emails = config.get_email_accounts()

loop = asyncio.get_event_loop()
loop.run_until_complete(emails[0].get_mail())
