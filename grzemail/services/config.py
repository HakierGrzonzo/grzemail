from configparser import ConfigParser
from ..models import Email
import os


class Config:
    def __init__(self) -> None:
        path = os.path.expanduser("~/.config/grzemail")
        parser = ConfigParser()
        with open(path, "r") as f:
            parser.read_file(f)
        self.config = parser

    def get_cache_dir(self):
        path = self.config.get(
            "directories",
            "cache",
            fallback=os.path.expanduser("~/.cache/grzemail"),
        )
        try:
            os.mkdir(path)
        except FileExistsError:
            pass
        return path

    def get_email_accounts(self):
        email_sections = [
            (section.replace("Email-", "", 1), section)
            for section in self.config.sections()
            if section.startswith("Email-")
        ]
        emails = [
            Email(name, self.config[email_section])
            for name, email_section in email_sections
        ]
        return emails
