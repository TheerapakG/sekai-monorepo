# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

import asyncio
import discord
import discord.types.embed
from discord.ext.commands import Bot
import git
from meilisearch import Client as MeiliSearchClient
import os
from typing import Any, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

repo = git.Repo(search_parent_directories=True)
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
BOT_FOOTER = f"{BOT_VERSION} by TheerapakG"


class BotClient(Bot):
    engine: Optional[AsyncEngine]
    async_session: Optional[async_sessionmaker[AsyncSession]]
    meilisearch_client: MeiliSearchClient

    def __init__(
        self,
        *,
        intents: discord.Intents,
    ):
        activity = discord.Game(name=BOT_VERSION)
        super().__init__([], activity=activity, intents=intents)
        self.engine = None
        self.async_session = None
        self.meilisearch_client = MeiliSearchClient(
            f"http://127.0.0.1:{os.environ['MEILISEARCH_PORT']}"
        )

        @self.listen()
        async def on_ready():
            engine = create_async_engine(
                f"postgresql+asyncpg://{os.environ['DB_USERNAME']}:{os.environ['DB_PASSWORD']}@localhost:{os.environ['DB_PORT']}"
            )

            self.engine = engine
            self.async_session = async_sessionmaker(engine, expire_on_commit=False)
            await asyncio.gather(*(self.setup_guild(guild) for guild in self.guilds))

        @self.listen()
        async def on_guild_join(guild: discord.Guild):
            await self.setup_guild(guild)

    async def setup_guild(self, guild: discord.Guild):
        if "TEST" in os.environ:
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

    def generate_embed(
        self,
        *,
        color: Optional[int | discord.Colour] = None,
        title: Optional[Any] = None,
        type: discord.types.embed.EmbedType = "rich",
        description: Optional[Any] = None,
    ):
        embed = discord.Embed(
            color=color, title=title, type=type, description=description
        )
        embed.set_footer(text=BOT_FOOTER)
        return embed
