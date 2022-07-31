import asyncio
from .downloader import downloader
from ..services.database import create_tables
import logging
from ..services import config_class
from socpi import App, Client, get_path_in_run

from ..models.email import Email

logger = logging.getLogger(__name__)


app = App(get_path_in_run("grzemail"))

accounts = config_class.get_email_accounts()


@app.register
def get_accounts() -> dict[str, Email]:
    return {account._name: account for account in accounts}


async def daemon_main():
    logger.info("Creating Tables!")
    await create_tables()
    downloader_task = asyncio.Task(downloader())
    try:
        await downloader_task
        # await app.run()
    finally:
        downloader_task.cancel()


client = Client(app)
