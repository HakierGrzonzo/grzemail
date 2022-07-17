from textual.reactive import Reactive
from textual.layout import Layout
from rich.panel import Panel
from rich.text import Text
from textual.widgets import Button, ButtonPressed
from textual.views import GridView


from ..models.email import Email

from ..services import config_class


class EmailBar(GridView):
    async def on_mount(self):
        self.accounts = config_class.get_email_accounts()

        def make_account_button(account: Email):
            return Button(
                account.get_name(),
                name=account.get_name(),
                style="color(0) on color(2)",
            )

        self.buttons = {
            account.get_name(): (make_account_button(account), account)
            for account in self.accounts
        }

        self.grid.set_align("center", "start")
        self.grid.add_column("col", repeat=len(self.buttons.keys()))
        self.grid.add_row("accounts", max_size=1)
        self.grid.place(*[button for button, _ in self.buttons.values()])

    async def handle_button_pressed(self, message: ButtonPressed) -> None:
        assert isinstance(message.sender, Button)
        # Reinit other buttons
        for _, (button, account) in self.buttons.items():
            button.label = account.get_name()
        button, account = self.buttons[message.sender.name]
        button.label = Text(f"*{account.get_name()}*", style="bold color(1)")
        self.root_view.named_widgets["mailbox_bar"].account = account
