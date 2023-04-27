from dataclasses import dataclass
from discord.ext.tasks import Loop, LF
from typing import Generic


@dataclass(frozen=True, kw_only=True, slots=True)
class Task(Generic[LF]):
    task: Loop[LF]
    stop_on_disconnect: bool
