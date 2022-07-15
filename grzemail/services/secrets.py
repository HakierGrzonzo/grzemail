import keyring
import logging

logger = logging.getLogger(__name__)


class Secrets:
    def __init__(self) -> None:
        pass

    def get_password_for_account(self, username: str) -> str:
        password = keyring.get_password("grzemail", username)
        if password:
            logger.info(f"Getting password for {username}")
            return password
        raise Exception(f"No password set for {username}")
