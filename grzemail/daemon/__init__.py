from ..services import config_class
from socpi import App, Client, get_path_in_run

from grzemail.models.email import Email

app = App(get_path_in_run('grzemail'))

accounts = config_class.get_email_accounts()

@app.register
def get_accounts() -> dict[str, Email]:
    return {account._name: account for account in accounts}

client = Client(app)
