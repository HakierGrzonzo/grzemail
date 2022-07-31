import aiofiles

from grzemail.services import config_class
from grzemail.models.wrappers.message import Message
from os import path


async def save_message_to_cache(message: Message, id: int):
    cache_path = config_class.get_cache_dir()
    file_path = path.join(cache_path, f"msg_{id}")
    async with aiofiles.open(file_path, "wb+") as f:
        await f.write(await message.get_msg_bytes())
