from socpi.app import asyncio
from sqlalchemy import select
from grzemail.daemon.cache import save_message_to_cache
from sqlalchemy.sql import func
from grzemail.services.FilterFactory import FilterFactory
from grzemail.utils.hash import static_hash
from ..services import config_class
from ..models.email import Email
from ..services.database import Mailboxes, Messages, get_async_session
import logging

logger = logging.getLogger(__name__)


async def download_mail_for_account(account: Email):
    logger.info(f"Starting email download for {account.get_name()}")
    logger.error(f"{account.get_id()}")
    async for session in get_async_session():
        result, mailboxes = await asyncio.gather(
            session.execute(
                select(Mailboxes).filter(Mailboxes.account == account.get_id())
            ),
            account.get_mailboxes(),
        )
        all_mailboxes = result.scalars().all()
        if len(all_mailboxes) == 0:
            logger.warn(f"Setting up local mailboxes for {account.get_name()}")
            new_mailboxes = list(
                Mailboxes(
                    id=static_hash(name),
                    name=name,
                    account=account.get_id(),
                )
                for name in mailboxes
            )
            for mailbox in new_mailboxes:
                session.add(mailbox)
                await session.flush()
            await session.commit()
            result = await session.execute(
                select(Mailboxes).filter(Mailboxes.account == account.get_id())
            )
            all_mailboxes = result.scalars().all()

        logger.info(f"Getting last dates for {account.get_name()}")
        last_message_date_per_mailbox = await session.execute(
            select([func.max(Messages.sent_date), Mailboxes.name])
            .join(Mailboxes, Mailboxes.id == Messages.mailbox)
            .filter(Mailboxes.account == account.get_id())
            .group_by(Mailboxes.id)
        )
        last_message_all = last_message_date_per_mailbox.all()
        logger.info(last_message_all)
        if len(last_message_all) == 0:
            # download all emails
            filters = {
                mailbox.name: FilterFactory() for mailbox in all_mailboxes
            }
        else:
            date_map = {
                mailbox: sent_date.date()
                for sent_date, mailbox in last_message_all
            }
            filters = {
                mailbox.name: FilterFactory().SINCE(date_map[mailbox.name])
                if date_map.get(mailbox.name)
                else FilterFactory()
                for mailbox in all_mailboxes
            }

        msg_ids_for_account = await session.execute(
            select(Messages.id)
            .join(Mailboxes, Mailboxes.id == Messages.mailbox)
            .filter(Mailboxes.account == account.get_id())
        )
        msg_ids_for_account = msg_ids_for_account.scalars().all()

        save_tasks = []
        try:
            for mailbox in all_mailboxes:
                async for message in account.get_mail(
                    filters[mailbox.name], mailbox.name
                ):
                    logger.debug(f"Storing message {message}")
                    msg_id = message.get_id(mailbox.id)
                    if msg_id in msg_ids_for_account:
                        continue
                    session.add(
                        Messages(
                            id=msg_id,
                            uid=message._uid,
                            mailbox=mailbox.id,
                            sent_date=message.get_sent_date(),
                            subject=message.get_header("Subject"),
                            sender=0,
                        )
                    )
                    save_tasks.append(
                        asyncio.Task(save_message_to_cache(message, msg_id))
                    )
        except Exception as e:
            logger.error(f"Failed to get all messages, will retry")
            raise e
        finally:
            await session.flush()
            await asyncio.gather(*save_tasks, session.commit())


async def downloader():
    accounts = config_class.get_email_accounts()
    while True:
        errors = await asyncio.gather(
            *[download_mail_for_account(a) for a in accounts],
            return_exceptions=True,
        )
        print(errors)
        for x in errors:
            if x is not None:
                raise x
        await asyncio.sleep(3)
        if all([e == None for e in errors]):
            break
