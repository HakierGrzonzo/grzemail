from typing import AsyncGenerator, Generic, TypeVar


class Setupable:
    def __init__(self) -> None:
        pass

    def get_name(self) -> str:
        return "Setupable"

    async def setup(self) -> None:
        pass

    async def close(self) -> None:
        pass


T = TypeVar("T")


class Wrapper(Generic[T]):
    def __init__(self, child: T) -> None:
        self._child = child

    def __repr__(self) -> str:
        return f"<Wrapper>{self._child}</Wrapper>"

    def get_name(self) -> str:
        return self._child.get_name()

    async def use_wrapped(self) -> AsyncGenerator[T, None]:
        await self._child.setup()
        yield self._child
        await self._child.close()
