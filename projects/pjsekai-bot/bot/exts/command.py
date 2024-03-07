# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

from discord.ext.commands import hybrid_group, is_owner, Cog, Context

from ..bot.client import BotClient


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


async def setup(client: BotClient):
    await client.add_cog(CommandCog())
