import asyncio
from aioimaplib.aioimaplib import IMAP4_SSL
from .message import Message

from grzemail.services.FilterFactory import FilterFactory
from .wrapper import Setupable


class MailBox(Setupable):
    def __init__(self, connection: IMAP4_SSL, name: str) -> None:
        super().__init__()
        self._name = name
        self._connection = connection

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
            await message.fetch_headers()
            yield message

    async def close(self):
        res, _ = await self._connection.close()
        if res != "OK":
            raise Exception(f"Failed to close inbox {self._name}")

    def __repr__(self) -> str:
        return f"<MailBox {self._name}>"
