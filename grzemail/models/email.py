from email.mime.base import MIMEBase
import logging
from typing import AsyncGenerator
from aiosmtplib import SMTP
from aioimaplib import aioimaplib

from grzemail.models.wrappers.client import Client

from ..services.FilterFactory import FilterFactory

from ..services import secret_class

logger = logging.getLogger(__name__)


class Email:
    def __init__(self, name: str, config) -> None:
        self._name = name
        self._address = config["address"]
        self._host = config["host"]
        self._port = int(config.get("port", 587))
        logger.debug(f"Creating email {self}")
        pass

    def get_name(self) -> str:
        return f"{self._name} <{self._address}>"

    def get_id(self) -> int:
        return hash(f"{self._address}, {self._host}, {self._port}")

    def __repr__(self) -> str:
        return (
            f"<Email {self._name} {self._address} at {self._host}:{self._port}>"
        )

    async def _connect_smtp(self) -> AsyncGenerator[SMTP, None]:
        logger.debug(f"Atempting SMTP on {self}")
        client = SMTP(
            hostname=self._host,
            port=self._port,
            use_tls=False,
        )
        await client.connect()
        await client.starttls()
        await client.login(
            username=self._address,
            password=secret_class.get_password_for_account(self._address),
        )
        logger.debug(f"Connected to SMTP on {self}")
        yield client
        await client.quit()

    async def _connect_imap(self) -> AsyncGenerator[aioimaplib.IMAP4_SSL, None]:
        logger.debug(f"Atempting IMAP on {self}")
        client = aioimaplib.IMAP4_SSL(host=self._host)
        await client.wait_hello_from_server()
        await client.login(
            self._address, secret_class.get_password_for_account(self._address)
        )
        logger.debug(f"Connected to IMAP on {self}")
        yield client
        await client.logout()

    async def send_message(self, body: MIMEBase, **kwargs):
        body["From"] = self._address
        if not "To" in kwargs.keys():
            raise Exception(f"Missing recipient for message from {self}")
        for key, value in kwargs.items():
            body[key] = value
        async for connection in self._connect_smtp():
            print(connection)
            # await connection.send_message(body)

    async def get_mailboxes(self):
        res = {}
        async for connection in self._connect_imap():
            mailboxes = await Client(connection).get_mailboxes()
            for k, v in mailboxes.items():
                res[k] = v
        return res

    async def get_mail(self):
        async for connection in self._connect_imap():
            mailboxes = await Client(connection).get_mailboxes()
            print(mailboxes)
            async for mailbox in mailboxes["INBOX"].use_wrapped():
                async for message in mailbox.search(
                    FilterFactory().FROM("Waldemar.Paszkowski@polsl.pl")
                ):
                    print(message)
                    await message.fetch_body()
                    print(message.get_body_text())
