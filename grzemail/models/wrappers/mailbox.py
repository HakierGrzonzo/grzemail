from aioimaplib.aioimaplib import IMAP4_SSL
from sqlalchemy.util import asyncio
from .message import Message

from grzemail.services.FilterFactory import FilterFactory
from .wrapper import Setupable
import logging
import asyncio

logger = logging.getLogger(__name__)


class MailBox(Setupable):
    def __init__(self, connection: IMAP4_SSL, name: str) -> None:
        super().__init__()
        self._name = name
        self._connection = connection

    def get_name(self) -> str:
        return self._name

    async def setup(self):
        res, _ = await self._connection.select(self._name)
        if res != "OK":
            raise Exception(f"Failed to select inbox {self._name}")

    async def search(self, filter: FilterFactory | None):
        filter_string = filter.make() if filter else ""
        res, data = await self._connection.search(filter_string)
        if res != "OK":
            raise Exception(
                f"Failed to search for '{filter_string} in mailbox {self._name}'"
            )
        message_uids = data[0].decode().split()
        proto_messages = [
            Message(self._connection, uid) for uid in message_uids
        ]
        for message in proto_messages:
            await asyncio.gather(message.fetch_headers(), asyncio.sleep(1))
            yield message

    async def close(self):
        res, _ = await self._connection.close()
        if res != "OK":
            raise Exception(f"Failed to close inbox {self._name}")

    def __repr__(self) -> str:
        return f"<MailBox {self._name}>"
