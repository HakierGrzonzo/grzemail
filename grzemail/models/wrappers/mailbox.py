from aioimaplib.aioimaplib import IMAP4_SSL
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

    async def close(self):
        res, _ = await self._connection.close()
        if res != "OK":
            raise Exception(f"Failed to close inbox {self._name}")

    def __repr__(self) -> str:
        return f"<MailBox {self._name}>"
