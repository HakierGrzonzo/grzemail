import datetime
from email import message_from_bytes
from email import parser
import email.message
from email.iterators import _structure
from email.header import decode_header
from enum import Enum
from typing import Optional
from aioimaplib.aioimaplib import IMAP4_SSL
from email.parser import BytesHeaderParser
from email.utils import parsedate_tz, mktime_tz

import logging

from grzemail.utils.hash import static_hash

logger = logging.getLogger(__name__)


class MessageState(Enum):
    PROTO = 1
    HEADERS = 2
    FULL = 3


def _body_scorer(part: email.message.Message) -> int:
    cases = [
        (lambda x: x.get_content_disposition() == "inline", 1),
        (lambda x: x.get_content_disposition() == "attachment", -99),
        (lambda x: x.is_multipart(), -99),
        (lambda x: "text" in x.get_content_type(), 1),
        (lambda x: "text/plain" in x.get_content_type(), 10),
        (lambda x: "html" in x.get_content_type(), 5),
    ]
    return sum(score for test, score in cases if test(part))


class Message:
    def __init__(self, connection: IMAP4_SSL, uid: str) -> None:
        self._uid = uid
        self._connection = connection
        self._headers: Optional[email.message.Message] = None
        self.__header_bytes: Optional[bytes] = None
        self.__full_message: Optional[bytes] = None
        self._message: Optional[email.message.Message] = None

    def state(self) -> MessageState:
        if not self._headers:
            return MessageState.PROTO
        if not self._message:
            return MessageState.HEADERS
        return MessageState.FULL

    def get_id(self, mailbox_id: int) -> int:
        return static_hash(self._uid, str(mailbox_id))

    def get_header(self, key: str, default="") -> str:
        if self.state() == MessageState.PROTO:
            raise Exception(f"Headers missing for {self._uid}")
        raw = self._headers.get(key, default)
        if raw == None:
            raise KeyError(f"Header {key} not set for {self._uid}")
        parsed, codec = decode_header(raw)[0]
        if codec is None:
            return raw
        try:
            return parsed.decode(codec)
        except LookupError:
            logger.error(
                f"Failed to decode header {key}, got codec {codec} and content {parsed}"
            )
            return parsed.decode(errors="ignore")

    def get_sent_date(self):
        if self.state() == MessageState.PROTO:
            raise Exception(f"Headers missing for {self._uid}")
        try:
            date_candidate = self.get_header("Recived", None)
        except:
            date_candidate = self.get_header("Date", None)

        return datetime.datetime.fromtimestamp(
            mktime_tz(parsedate_tz(date_candidate))
        )

    def __repr__(self) -> str:
        repr_dict = {
            MessageState.PROTO: lambda: f"prototype {self._uid}",
            MessageState.HEADERS: lambda: f'partial from "{self.get_header("From")}" subject "{self.get_header("Subject")}"',
            MessageState.FULL: lambda: f'partial from "{self.get_header("From")}" subject "{self.get_header("Subject")}"',
        }
        return f"<Message {repr_dict[self.state()]()}>"

    async def fetch_headers(self):
        res, data = await self._connection.fetch(self._uid, "BINARY[HEADER]")
        if res != "OK":
            raise Exception(f"failed to fetch message {self._uid}")
        parser = BytesHeaderParser()
        self.__header_bytes = data[1]
        self._headers = parser.parsebytes(self.__header_bytes)

    async def fetch_body(self):
        if self.state() == MessageState.PROTO:
            raise Exception(f"Headers missing for {self._uid}")

        res, data = await self._connection.fetch(self._uid, "BINARY[TEXT]")
        if res != "OK":
            raise Exception(f"failed to fetch message {self._uid}")
        parser = BytesHeaderParser()
        self.__full_message = self.__header_bytes + data[1]
        self._message = message_from_bytes(self.__full_message)

    def get_body_text(self) -> str:
        if self.state() != MessageState.FULL:
            raise Exception(f"Missing body for message {self._uid}")
        body = max(
            list((_body_scorer(x), x) for x in self._message.walk()),
            key=lambda x: x[0],
        )[1]
        charset = body.get_content_charset()
        return body.get_payload(decode=True).decode(
            charset if charset else "ascii"
        )

    async def get_msg_bytes(self):
        if self.state() == MessageState.PROTO:
            await self.fetch_headers()
        if self.state() == MessageState.HEADERS:
            await self.fetch_body()
        return self.__full_message
