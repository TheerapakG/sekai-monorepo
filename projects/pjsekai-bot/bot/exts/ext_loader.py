# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

from discord.ext.commands import hybrid_group, is_owner, Cog, Context

from ..bot.client import BotClient


class ExtLoaderCog(Cog):
    @hybrid_group()
    async def loader(self, ctx: Context[BotClient]):
        pass

    @loader.command()
    async def list(self, ctx: Context[BotClient]):
        await ctx.defer()
        await ctx.send(
            embed=ctx.bot.generate_embed(
                title="extension list", description="\n".join(ctx.bot.extensions.keys())
            )
        )

    @loader.command()
    @is_owner()
    async def load(self, ctx: Context[BotClient], ext: str):
        await ctx.defer()
        await ctx.bot.load_extension(ext)
        await ctx.send(embed=ctx.bot.generate_embed(title=f"loaded {ext}!"))

    @loader.command()
    @is_owner()
    async def unload(self, ctx: Context[BotClient], ext: str):
        await ctx.defer()
        await ctx.bot.unload_extension(ext)
        await ctx.send(embed=ctx.bot.generate_embed(title=f"unloaded {ext}!"))

    @loader.command()
    @is_owner()
    async def reload(self, ctx: Context[BotClient], ext: str):
        await ctx.defer()
        await ctx.bot.reload_extension(ext)
        await ctx.send(embed=ctx.bot.generate_embed(title=f"reloaded {ext}!"))


async def setup(client: BotClient):
    await client.add_cog(ExtLoaderCog())
