import asyncio
import discord
from discord.ext.commands import Bot, Cog
import git
import os
from typing import Any, Iterable, Optional

from ..models.task import Task

repo = git.Repo(search_parent_directories=True)  # type: ignore
date = repo.head.commit.committed_datetime
sha = repo.head.commit.hexsha
dirty = repo.is_dirty(untracked_files=True)
BOT_VERSION = "-".join(
    i
    for i in [
        "TiaraPJSKBot",
        date.date().isoformat().replace("-", ""),
        sha[:7],
        "dev" if dirty else None,
    ]
    if i
)


class BotClient(Bot):
    announce_channel: Optional[discord.TextChannel]

    def __init__(
        self,
        cogs: Iterable[Cog],
        tasks: Iterable[Task[Any]],
        *,
        intents: discord.Intents,
    ):
        activity = discord.Game(name=BOT_VERSION)
        super().__init__([], activity=activity, intents=intents)
        self._cogs = cogs
        self._tasks = tasks
        self.announce_channel = None

        @self.listen()
        async def on_ready():
            announce_channel = (
                self.get_channel(int(os.environ["ANNOUNCE_CHANNEL"]))
                if "ANNOUNCE_CHANNEL" in os.environ
                else None
            )
            if announce_channel and isinstance(announce_channel, discord.TextChannel):
                self.announce_channel = announce_channel

            if "TEST" not in os.environ:
                await self.tree.sync()
            await asyncio.gather(*(self.setup_guild(guild) for guild in self.guilds))

            for task in self._tasks:
                task.task.start(client=self)

        @self.listen()
        async def on_resumed():
            announce_channel = (
                self.get_channel(int(os.environ["ANNOUNCE_CHANNEL"]))
                if "ANNOUNCE_CHANNEL" in os.environ
                else None
            )
            if announce_channel and isinstance(announce_channel, discord.TextChannel):
                self.announce_channel = announce_channel

            for task in self._tasks:
                if task.stop_on_disconnect:
                    task.task.start(client=self)

        @self.listen()
        async def on_disconnect():
            for task in self._tasks:
                if task.stop_on_disconnect:
                    task.task.cancel()

        @self.listen()
        async def on_guild_join(guild: discord.Guild):
            await self.setup_guild(guild)

    async def setup_guild(self, guild: discord.Guild):
        if "TEST" in os.environ:
            self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

    async def setup_hook(self):
        await asyncio.gather(*(self.add_cog(cog) for cog in self._cogs))
