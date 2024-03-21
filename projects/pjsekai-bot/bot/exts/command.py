# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

from typing import Optional

from discord import TextChannel
from discord.ext.commands import hybrid_group, is_owner, Cog, Context, CommandError
from sqlalchemy import select

from ..bot.client import BotClient
from ..schema.schema import CommandRestrict


class CommandCog(Cog):
    @hybrid_group()
    async def command(self, ctx: Context[BotClient]):
        pass

    @command.command()
    @is_owner()
    async def sync(self, ctx: Context[BotClient]):
        await ctx.defer()

        for guild in ctx.bot.guilds:
            await ctx.bot.tree.sync(guild=guild)

        await ctx.send(
            embed=ctx.bot.generate_embed(title="synced commands!", description="")
        )

    async def restrict_check(self, ctx: Context[BotClient]):
        if await ctx.bot.is_owner(ctx.author):
            return True

        if (async_session := ctx.bot.async_session) is None:
            raise CommandError("Cannot connect to DB :(")

        async with async_session() as session:
            command_restricts_result = await session.execute(
                select(CommandRestrict)
                .where(CommandRestrict.guild == ctx.guild.id)
                .where(CommandRestrict.command == ctx.command.qualified_name)
            )
            command_restricts = command_restricts_result.scalars().all()
            command_restrict_channels = [*map(lambda c: c.channel, command_restricts)]

            if not command_restrict_channels:
                return True

            return ctx.channel.id in command_restrict_channels

    @command.command()
    @is_owner()
    async def restrict(
        self,
        ctx: Context[BotClient],
        command: str,
        channel: Optional[TextChannel] = None,
    ):
        await ctx.defer()

        if not channel:
            if not isinstance(_channel := ctx.channel, TextChannel):
                await ctx.send(
                    embed=ctx.bot.generate_embed(
                        title="cannot do that to this channel",
                        description="I'm sorry~",
                    )
                )
                return
            channel = _channel

        if (async_session := ctx.bot.async_session) is None:
            await ctx.send(
                embed=ctx.bot.generate_embed(
                    title="cannot connect to DB",
                    description="I'm sorry~",
                )
            )
            return

        await ctx.send(
            embed=ctx.bot.generate_embed(
                title="restrict command success",
                description="Yay~",
            )
        )

    @command.command()
    @is_owner()
    async def unrestrict(
        self,
        ctx: Context[BotClient],
        command: str,
        channel: Optional[TextChannel] = None,
    ):
        await ctx.defer()

        if not channel:
            if not isinstance(_channel := ctx.channel, TextChannel):
                await ctx.send(
                    embed=ctx.bot.generate_embed(
                        title="cannot do that to this channel",
                        description="I'm sorry~",
                    )
                )
                return
            channel = _channel

        if (async_session := ctx.bot.async_session) is None:
            await ctx.send(
                embed=ctx.bot.generate_embed(
                    title="cannot connect to DB",
                    description="I'm sorry~",
                )
            )
            return

        await ctx.send(
            embed=ctx.bot.generate_embed(
                title="unrestrict command success",
                description="Yay~",
            )
        )


async def setup(client: BotClient):
    await client.add_cog(CommandCog())
