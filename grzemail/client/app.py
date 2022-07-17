from textual.app import App
from textual.widgets import Placeholder

from grzemail.client.mailbox_bar import MailBoxBar


from .email_bar import EmailBar


class Grzemail(App):
    async def on_mount(self) -> None:
        await self.view.dock(EmailBar(), edge="top", size=1)
        await self.view.dock(
            MailBoxBar(name="mailbox_bar"), edge="left", size=20
        )
        await self.view.dock(Placeholder(), edge="left")

    def on_key(self, event):
        if event.key.isdigit():
            self.background = f"on color({event.key})"
