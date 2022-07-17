import logging
from rich.panel import Panel
from textual.layouts.grid import GridLayout
from textual.views import GridView
from rich.text import Text
from textual.widgets import Button, ButtonPressed, Static
from textual.reactive import Reactive

from grzemail.models.wrappers.mailbox import MailBox

from ..models.email import Email

logger = logging.getLogger(__name__)


class MailBoxBar(GridView):
    account = Reactive(None)
    mailboxes = None

    async def on_mount(self) -> None:
        await self._reinit_grid()

    async def watch_account(self, account: Email | None) -> None:
        if account is None:
            self.mailboxes = None
        else:
            try:
                self.mailboxes = await account.get_mailboxes()
            except:
                self.mailboxes = {}
        await self._reinit_grid()

    async def _reinit_grid(self):
        self.layout = GridLayout()
        self.grid.add_column("mailboxes")
        self.grid.set_align("start", "start")
        if self.mailboxes is None:
            self.grid.add_row("row")
            self.grid.place(Static("Select account"))
        else:

            def make_mailbox_button(mailbox: MailBox):
                return Button(
                    mailbox.get_name(),
                    name=mailbox.get_name(),
                    style="color(0) on color(2)",
                )

            self._mailbox_buttons = {
                mailbox.get_name(): (make_mailbox_button(mailbox), mailbox)
                for mailbox in self.mailboxes.values()
            }
            self.grid.add_row(
                "row", repeat=len(self._mailbox_buttons.keys()), max_size=1
            )
            self.grid.place(
                *[button for button, _ in self._mailbox_buttons.values()]
            )
        logger.info(f"Refreshing mailbox bar!")

    async def handle_button_pressed(self, message: ButtonPressed) -> None:
        assert isinstance(message.sender, Button)
        # Reinit other buttons
        for _, (button, mailbox) in self._mailbox_buttons.items():
            button.label = mailbox.get_name()
        button, mailbox = self._mailbox_buttons[message.sender.name]
        button.label = Text(f"*{mailbox.get_name()}*", style="bold color(1)")
