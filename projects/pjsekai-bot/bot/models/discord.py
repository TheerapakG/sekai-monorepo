from typing import Protocol, runtime_checkable


@runtime_checkable
class Mentionable(Protocol):
    mention: str
