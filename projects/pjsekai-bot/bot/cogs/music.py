# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

import bisect
import datetime
import dateutil.parser
import discord
from discord.ext.commands import hybrid_group, Cog, Context
from async_pjsekai.enums.enums import CharacterType
from typing import Optional, Literal

from .pjsekai_client import get_pjsk_client_cog
from ..bot.client import BOT_VERSION, BotClient
from ..models.music import MusicData


class MusicListEmbedView(discord.ui.View):
    def __init__(self, time: datetime.datetime, index: int = 1):
        super().__init__()
        self.time = time
        self.index = index

    async def process(self, client: BotClient):
        if pjsk_client_cog := get_pjsk_client_cog(client):
            yield "defer", {}

            musics_by_publish_at_list = pjsk_client_cog.musics_by_publish_at_list
            musics = musics_by_publish_at_list[
                bisect.bisect_right(
                    musics_by_publish_at_list,
                    self.time,
                    key=lambda music: music.published_at if music.published_at else -1,
                ) :
            ]
            music_datas = [pjsk_client_cog.music_data_from_music(m) for m in musics]

            if len(music_datas) == 0:
                out_embed = discord.Embed(
                    title=f"Music releasing after <t:{int(self.time.timestamp())}:f> ({len(music_datas)})",
                    description="None!",
                )
                out_embed.set_footer(text=BOT_VERSION)
                yield "send", {"embed": out_embed}
            else:
                self.index = max(min(self.index, len(music_datas)), 1)
                out_embed = discord.Embed(
                    title=f"Music releasing after <t:{int(self.time.timestamp())}:f> ({self.index}/{len(music_datas)})"
                )
                out_embed_file = await pjsk_client_cog.add_music_embed_fields(
                    music_datas[self.index - 1], out_embed, set_title=False
                )
                out_embed.set_footer(text=BOT_VERSION)
                yield "send", {
                    "files": [out_embed_file]
                    if out_embed_file
                    else discord.utils.MISSING,
                    "embed": out_embed,
                    "view": self,
                }

    async def process_context(self, ctx: Context[BotClient]):
        async for action, kwargs in self.process(ctx.bot):
            match action:
                case "defer":
                    await ctx.defer()
                case "send":
                    await ctx.send(**kwargs)

    async def process_interaction(self, interaction: discord.Interaction[BotClient]):
        async for action, kwargs in self.process(interaction.client):
            match action:
                case "defer":
                    pass
                case "send":
                    kwargs["attachments"] = kwargs.pop("files", discord.utils.MISSING)
                    await interaction.response.edit_message(**kwargs)

    @discord.ui.button(label="previous", style=discord.ButtonStyle.primary)
    async def previous(
        self, interaction: discord.Interaction[BotClient], button: discord.ui.Button
    ):
        self.index = self.index - 1
        await self.process_interaction(interaction)

    @discord.ui.button(label="next", style=discord.ButtonStyle.primary)
    async def next(
        self, interaction: discord.Interaction[BotClient], button: discord.ui.Button
    ):
        self.index = self.index + 1
        await self.process_interaction(interaction)


class MusicCog(Cog):
    @hybrid_group()
    async def music(self, ctx: Context[BotClient]):
        pass

    @music.command()
    async def list(
        self,
        ctx: Context[BotClient],
        after: Optional[str] = None,
        design: Optional[Literal["quote", "embed"]] = None,
    ):
        if after:
            after_dt = dateutil.parser.parse(after)
            if after_dt.tzinfo is None or after_dt.tzinfo.utcoffset(after_dt) is None:
                after_dt = after_dt.replace(tzinfo=datetime.timezone.utc)
        else:
            after_dt = datetime.datetime.now(datetime.timezone.utc)

        match design:
            case "quote":
                if pjsk_client_cog := get_pjsk_client_cog(ctx.bot):
                    await ctx.defer()
                    musics_by_publish_at_list = (
                        pjsk_client_cog.musics_by_publish_at_list
                    )
                    musics = musics_by_publish_at_list[
                        bisect.bisect_right(
                            musics_by_publish_at_list,
                            after_dt,
                            key=lambda music: music.published_at
                            if music.published_at
                            else -1,
                        ) :
                    ]
                    music_datas = [
                        pjsk_client_cog.music_data_from_music(m) for m in musics
                    ]
                    out_strs = (
                        [m.get_str() for m in music_datas] if music_datas else ["None!"]
                    )
                    await ctx.send("\n".join(["```", *out_strs, "```"]))
            case "embed":
                view = MusicListEmbedView(after_dt)
                await view.process_context(ctx)
            case _:
                if pjsk_client_cog := get_pjsk_client_cog(ctx.bot):
                    await ctx.defer()
                    musics_by_publish_at_list = (
                        pjsk_client_cog.musics_by_publish_at_list
                    )
                    musics = musics_by_publish_at_list[
                        bisect.bisect_right(
                            musics_by_publish_at_list,
                            after_dt,
                            key=lambda music: music.published_at
                            if music.published_at
                            else -1,
                        ) :
                    ]
                    music_datas = [
                        pjsk_client_cog.music_data_from_music(m) for m in musics
                    ]
                    out_strs = (
                        [m.get_str() for m in music_datas] if music_datas else ["None!"]
                    )
                    await ctx.send("\n".join(out_strs))

    @music.command()
    async def view(self, ctx: Context[BotClient], id: int):
        await ctx.defer()

        if (pjsk_client_cog := get_pjsk_client_cog(ctx.bot)) and (
            music := pjsk_client_cog.musics_dict.get(id)
        ):
            music_data = pjsk_client_cog.music_data_from_music(music)
            out_embed = discord.Embed()
            out_embed.set_footer(text=BOT_VERSION)
            out_embed_file = await pjsk_client_cog.add_music_embed_fields(
                music_data, out_embed
            )
            if out_embed_file:
                await ctx.send(file=out_embed_file, embed=out_embed)
            else:
                await ctx.send(embed=out_embed)
        else:
            await ctx.send("Not found!")

    @music.command()
    async def vocal(self, ctx: Context[BotClient], id: int):
        await ctx.defer()

        if (
            (pjsk_client_cog := get_pjsk_client_cog(ctx.bot))
            and (music := pjsk_client_cog.musics_dict.get(id))
            and (music_vocals := pjsk_client_cog.music_vocal_dict.get(id))
        ):
            music_data = pjsk_client_cog.music_data_from_music(music)
            out_embed = discord.Embed()
            out_embed.title = music.title
            for music_vocal in music_vocals:
                character_list = []
                if characters := music_vocal.characters:
                    for character in characters:
                        if character_id := character.character_id:
                            match character.character_type:
                                case CharacterType.GAME_CHARACTER:
                                    if game_character := pjsk_client_cog.game_character_dict.get(
                                        character_id
                                    ):
                                        name = f"{game_character.first_name} {game_character.given_name}"
                                        ruby_name = f"{game_character.first_name_ruby} {game_character.given_name_ruby}"
                                        character_list.append(f"{name} ({ruby_name})")
                                    else:
                                        character_list.append("<unknown>")
                                case CharacterType.OUTSIDE_CHARACTER:
                                    if (
                                        outside_character := pjsk_client_cog.outside_character_dict.get(
                                            character_id
                                        )
                                    ) and (name := outside_character.name):
                                        character_list.append(f"{name}")
                                    else:
                                        character_list.append("<unknown>")
                                case _:
                                    character_list.append("<unknown>")
                out_embed.add_field(
                    name=music_vocal.caption,
                    value=", ".join(character_list),
                    inline=False,
                )

            out_embed.set_footer(text=BOT_VERSION)
            out_embed_file = await pjsk_client_cog.add_music_embed_thumbnail(
                music_data, out_embed
            )
            if out_embed_file:
                await ctx.send(file=out_embed_file, embed=out_embed)
            else:
                await ctx.send(embed=out_embed)
        else:
            await ctx.send("Not found!")
