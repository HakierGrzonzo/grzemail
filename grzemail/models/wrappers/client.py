from aioimaplib.aioimaplib import IMAP4_SSL
from grzemail.models.wrappers.mailbox import MailBox
from grzemail.models.wrappers.wrapper import Wrapper

from grzemail.utils.namespace import parse_mailbox, parse_namespace


class Client:
    def __init__(self, connection: IMAP4_SSL) -> None:
        self._connection = connection
        self._separator = None

    async def get_mailboxes(self):
        res, data = await self._connection.namespace()
        if res != "OK":
            raise Exception("Failed to namespace inboxes")
        namespace, self._separator = parse_namespace(data[0])
        res, data = await self._connection.list(f'"{namespace}"', '"*"')
        if res != "OK":
            raise Exception("Failed to list inboxes")
        # Get rid of the last result, it is some performence data
        mailboxes = [parse_mailbox(x) for x in data[:-1]]
        return {
            mailbox["name"]: Wrapper(MailBox(self._connection, mailbox["name"]))
            for mailbox in mailboxes
        }
