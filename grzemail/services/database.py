from typing import AsyncGenerator
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy import Column
from sqlalchemy.sql.schema import ForeignKey
import logging
from ..services import config_class
from os import path

from sqlalchemy.orm import (
    declarative_base,
    relation,
    relationship,
    sessionmaker,
)

logger = logging.getLogger(__name__)

Base = declarative_base()


class Contacts(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    address = Column(String)
    is_me = Column(Boolean)


class RecipientRelation(Base):
    __tablename__ = "recipient_relation"
    id = Column(Integer, primary_key=True)
    contact = Column(ForeignKey("contacts.id"))
    message = Column(ForeignKey("messages.id"))


class Messages(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    uid = Column(Integer)
    mailbox = Column(Integer, ForeignKey("mailboxes.id"))
    sent_date = Column(DateTime)
    subject = Column(String)
    sender = Column(Integer, ForeignKey("contacts.id"))


class Mailboxes(Base):
    __tablename__ = "mailboxes"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    account = Column(Integer)


def get_db_engine() -> AsyncEngine:
    db_path = path.join(config_class.get_cache_dir(), "db")
    logger.debug(f"Using database at {db_path}")
    return create_async_engine(f"sqlite+aiosqlite:///{db_path}")


engine = get_db_engine()
session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=True
)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_maker() as session:
        yield session
