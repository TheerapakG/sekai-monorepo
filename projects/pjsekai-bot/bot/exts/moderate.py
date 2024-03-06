# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

from discord import TextChannel, VoiceChannel, StageChannel, Thread
from discord.ext.commands import hybrid_group, is_owner, Cog, Context

from ..bot.client import BotClient


class ModerateCog(Cog):
    @hybrid_group()
    async def moderate(self, ctx: Context[BotClient]):
        pass

    @moderate.command()
    @is_owner()
    async def slowmode(self, ctx: Context[BotClient], duration: int):
        await ctx.defer()

        if not isinstance(
            (channel := ctx.channel), (TextChannel, VoiceChannel, StageChannel, Thread)
        ):
            await ctx.send(
                embed=ctx.bot.generate_embed(
                    title="cannot do that to this channel",
                    description="I'm sorry~",
                )
            )
            return

        previous_duration = channel.slowmode_delay
        await channel.edit(slowmode_delay=duration)
        await ctx.send(
            embed=ctx.bot.generate_embed(
                title="successfully updated slowmode",
                description=f"from {'none' if previous_duration == 0 else previous_duration} to {'none' if duration == 0 else duration}",
            )
        )


async def setup(client: BotClient):
    await client.add_cog(ModerateCog())
