from typing import AsyncGenerator


class Setupable:
    def __init__(self) -> None:
        pass

    async def setup(self) -> None:
        pass

    async def close(self) -> None:
        pass


class Wrapper:
    def __init__(self, child: Setupable) -> None:
        self._child = child

    def __repr__(self) -> str:
        return f"<Wrapper>{self._child}</Wrapper>"

    async def use_wrapped(self) -> AsyncGenerator[Setupable, None]:
        await self._child.setup()
        yield self._child
        await self._child.close()
