# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

from discord import TextChannel
from discord.ext.commands import hybrid_group, is_owner, Cog, Context
from sqlalchemy import delete, select
from typing import Literal, Optional

from ..models.discord import Mentionable
from ..schema.schema import ChannelIntent, ChannelIntentEnum
from ..bot.client import BotClient


Intent = Literal["announce", "music_leak", "vocal_leak", "card_leak"]


class ChannelCog(Cog):
    client: BotClient

    def __init__(self, client: BotClient) -> None:
        super().__init__()

        self.client = client

    @hybrid_group()
    async def channel(self, ctx: Context[BotClient]):
        pass

    @channel.command()
    @is_owner()
    async def bind(
        self,
        ctx: Context[BotClient],
        intent: Intent,
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

        async with async_session() as session:
            async with session.begin():
                session.add(
                    ChannelIntent(
                        guild=channel.guild.id,
                        channel=channel.id,
                        intent=ChannelIntentEnum[intent.upper()],
                    )
                )

            await session.commit()

            await ctx.send(
                embed=ctx.bot.generate_embed(
                    title="bind channel success",
                    description="Yay~",
                )
            )

    @channel.command()
    @is_owner()
    async def unbind(
        self,
        ctx: Context[BotClient],
        intent: Intent,
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

        async with async_session() as session:
            async with session.begin():
                await session.execute(
                    delete(ChannelIntent).where(
                        ChannelIntent.guild == channel.guild.id,
                        ChannelIntent.channel == channel.id,
                        ChannelIntent.intent == ChannelIntentEnum[intent.upper()],
                    )
                )

            await ctx.send(
                embed=ctx.bot.generate_embed(
                    title="unbind channel success",
                    description="Yay~",
                )
            )

    @channel.command()
    async def list(self, ctx: Context[BotClient]):
        await ctx.defer()

        if not (guild := ctx.guild):
            await ctx.send(
                embed=ctx.bot.generate_embed(
                    title="cannot do that outside of a server",
                    description="I'm sorry~",
                )
            )
            return

        if (async_session := ctx.bot.async_session) is None:
            await ctx.send(
                embed=ctx.bot.generate_embed(
                    title="cannot connect to DB",
                    description="I'm sorry~",
                )
            )
            return

        async with async_session() as session:
            channel_intents_result = await session.execute(
                select(ChannelIntent).where(ChannelIntent.guild == ctx.guild.id)
            )
            channel_intents = channel_intents_result.scalars().all()

            channel_mapping = {
                channel_intent_enum: list[Mentionable]()
                for channel_intent_enum in ChannelIntentEnum
            }
            for channel_intent in channel_intents:
                if (
                    channel := guild.get_channel_or_thread(channel_intent.channel)
                ) and isinstance(channel, Mentionable):
                    channel_mapping[channel_intent.intent].append(channel)

            embed = ctx.bot.generate_embed(title="bound channels")
            for channel_intent_enum, channel_list in channel_mapping.items():
                embed.add_field(
                    name=channel_intent_enum.name.lower(),
                    value=(
                        " ".join([channel.mention for channel in channel_list])
                        if channel_list
                        else "None"
                    ),
                )

            await ctx.send(embed=embed)

    async def get_channels(self, intent: ChannelIntentEnum):
        if (async_session := self.client.async_session) is not None:
            async with async_session() as session:
                channel_intents_result = await session.execute(
                    select(ChannelIntent).where(ChannelIntent.intent == intent)
                )
                channel_intents = channel_intents_result.scalars().all()
                return map(
                    lambda channel_intent: self.client.get_channel(
                        channel_intent.channel
                    ),
                    channel_intents,
                )
        return []


async def setup(client: BotClient):
    await client.add_cog(ChannelCog(client))
