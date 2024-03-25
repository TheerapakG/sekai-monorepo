# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

import asyncio
import bisect
from contextlib import suppress
from dataclasses import dataclass
import datetime
import dateutil.parser
import discord
from discord.ext.commands import hybrid_group, Cog, Context
from async_pjsekai.enums.enums import CharacterType
import random
from typing import Optional, Literal, TYPE_CHECKING


from ..bot.client import BotClient
from ..models.music import MusicData
from ..utils.discord import add_embed_thumbnail

if TYPE_CHECKING:
    from .pjsekai_client import PjskClientCog


def get_pjsk_client_cog(client: BotClient):
    from .pjsekai_client import PjskClientCog  # get fresh version of cog

    if cog := client.get_cog(PjskClientCog.__cog_name__):
        if isinstance(cog, PjskClientCog):
            return cog


def get_music_datas(client_cog: "PjskClientCog", after: datetime.datetime):
    musics_by_publish_at_list = client_cog.musics_by_publish_at_list
    musics = musics_by_publish_at_list[
        bisect.bisect_right(
            musics_by_publish_at_list,
            after,
            key=lambda music: music.published_at if music.published_at else -1,
        ) :
    ]
    return [client_cog.music_data_from_music(m) for m in musics]


class MusicListEmbedView(discord.ui.View):
    def __init__(self, after: datetime.datetime, index: int = 1):
        super().__init__()
        self.after = after
        self.index = index

    async def process(self, client: BotClient):
        yield "defer", {}
        client_cog = get_pjsk_client_cog(client)

        if client_cog is None:
            out_embed = client.generate_embed(
                title=f"Music releasing after <t:{int(self.after.timestamp())}:f>",
                description="Client not loaded!",
            )
            yield "send", {"embed": out_embed}
            return

        music_datas = get_music_datas(client_cog, self.after)

        if not music_datas:
            out_embed = client.generate_embed(
                title=f"Music releasing after <t:{int(self.after.timestamp())}:f> ({len(music_datas)})",
                description="None!",
            )
            yield "send", {"embed": out_embed}
            return

        else:
            self.index = max(min(self.index, len(music_datas)), 1)
            out_embed = client.generate_embed(
                title=f"Music releasing after <t:{int(self.after.timestamp())}:f> ({self.index}/{len(music_datas)})"
            )
            music_data = music_datas[self.index - 1]
            music_data.add_embed_fields(out_embed, set_title=False)
            out_embed_file = None
            if images := await music_data.get_images(client_cog.pjsk_client):
                out_embed_file = add_embed_thumbnail(out_embed, images[0])
            yield "send", {
                "files": [out_embed_file] if out_embed_file else discord.utils.MISSING,
                "embed": out_embed,
                "view": self,
            }
            return

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


class MusicSearchEmbedView(discord.ui.View):
    def __init__(self, q: str, index: int = 1):
        super().__init__()
        self.q = q
        self.ids: list[int] | None = None
        self.index = index

    async def process(self, client: BotClient):
        yield "defer", {}
        client_cog = get_pjsk_client_cog(client)

        if client_cog is None:
            out_embed = client.generate_embed(
                title=f"Search result for music containing {self.q}",
                description="Client not loaded!",
            )
            yield "send", {"embed": out_embed}
            return

        if self.ids is None:
            self.ids = [
                i["id"]
                for i in client.meilisearch_client.index("musics").search(
                    self.q, {"attributesToRetrieve": ["id"]}
                )["hits"]
            ]
            if not self.ids:
                out_embed = client.generate_embed(
                    title=f"Search result for music containing {self.q}",
                    description="None!",
                )
                yield "send", {"embed": out_embed}
                return

        self.index = max(min(self.index, len(self.ids)), 1)

        if (music := client_cog.musics_dict.get(self.ids[self.index - 1])) is None:
            out_embed = client.generate_embed(
                title=f"Search result for music containing {self.q}",
                description="None!",
            )
            yield "send", {"embed": out_embed}
            return

        else:
            music_data = client_cog.music_data_from_music(music)
            out_embed = client.generate_embed(
                title=f"Search result for music containing {self.q} ({self.index}/{len(self.ids)})"
            )
            music_data.add_embed_fields(out_embed, set_title=False)
            out_embed_file = None
            if images := await music_data.get_images(client_cog.pjsk_client):
                out_embed_file = add_embed_thumbnail(out_embed, images[0])
            yield "send", {
                "files": [out_embed_file] if out_embed_file else discord.utils.MISSING,
                "embed": out_embed,
                "view": self,
            }
            return

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


@dataclass
class Guess:
    music: MusicData
    task: asyncio.Task


class MusicCog(Cog):
    guess_in_progress: dict[int, Guess]

    def __init__(self):
        self.guess_in_progress = {}

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
                await ctx.defer()
                client_cog = get_pjsk_client_cog(ctx.bot)

                if client_cog is None:
                    await ctx.send("Client not loaded!")
                    return

                music_datas = get_music_datas(client_cog, after_dt)
                out_strs = (
                    [m.get_str() for m in music_datas] if music_datas else ["None!"]
                )
                await ctx.send("\n".join(["```", *out_strs, "```"]))
            case "embed":
                view = MusicListEmbedView(after_dt)
                await view.process_context(ctx)
            case _:
                await ctx.defer()
                client_cog = get_pjsk_client_cog(ctx.bot)

                if client_cog is None:
                    await ctx.send("Client not loaded!")
                    return

                music_datas = get_music_datas(client_cog, after_dt)
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
            out_embed = ctx.bot.generate_embed()
            music_data.add_embed_fields(out_embed, set_title=False)
            if images := await music_data.get_images(pjsk_client_cog.pjsk_client):
                out_embed_file = add_embed_thumbnail(out_embed, images[0])
                await ctx.send(file=out_embed_file, embed=out_embed)
            else:
                await ctx.send(embed=out_embed)
        else:
            await ctx.send("Not found!")

    @music.command()
    async def search(self, ctx: Context[BotClient], q: str):
        view = MusicSearchEmbedView(q)
        await view.process_context(ctx)

    @music.command()
    async def guess(self, ctx: Context[BotClient]):
        await ctx.defer()

        if (self.guess_in_progress.get(ctx.channel.id, None)) is not None:
            out_embed = ctx.bot.generate_embed(title="active guess found!")
            await ctx.send(embed=out_embed)
            return

        if (pjsk_client_cog := get_pjsk_client_cog(ctx.bot)) is None:
            await ctx.send("please load pjsk_client extension")
            return

        music = random.choice([*pjsk_client_cog.musics_dict.values()])
        music_data = pjsk_client_cog.music_data_from_music(music)
        out_embed = ctx.bot.generate_embed(
            title="guess the song!",
            description="type g followed by the name of the song",
        )
        out_embed_file = await music_data.add_embed_random_crop_thumbnail(
            pjsk_client_cog.pjsk_client, out_embed
        )

        async def check_guess():
            while True:

                def check(msg: discord.Message):
                    if msg.channel != ctx.channel:
                        return False

                    match msg.content.split():
                        case [lead, *_] if lead == "g":
                            return True
                        case _:
                            return False

                msg = await ctx.bot.wait_for("message", check=check)
                match msg.content.split():
                    case [lead, *rest] if lead == "g":
                        pass
                    case _:
                        continue

                search = " ".join(rest)

                matches = [
                    i["id"]
                    for i in ctx.bot.meilisearch_client.index("musics").search(
                        search, {"attributesToRetrieve": ["id"]}
                    )["hits"]
                ]
                match matches:
                    case [first, *_]:
                        pass
                    case _:
                        out_embed = ctx.bot.generate_embed(
                            title=f"i afraid i dont know {search}",
                        )
                        await ctx.channel.send(embed=out_embed)
                        continue

                if first == music_data.ids["m"]:
                    del self.guess_in_progress[ctx.channel.id]
                    out_embed = ctx.bot.generate_embed(
                        title="correct!", description=music_data.title_str()
                    )
                    if images := await music_data.get_images(
                        pjsk_client_cog.pjsk_client
                    ):
                        out_embed_file = add_embed_thumbnail(out_embed, images[0])
                        await ctx.channel.send(file=out_embed_file, embed=out_embed)
                    else:
                        await ctx.channel.send(embed=out_embed)

                    return
                else:
                    guess_music = pjsk_client_cog.musics_dict[first]
                    guess_music_data = pjsk_client_cog.music_data_from_music(
                        guess_music
                    )
                    out_embed = ctx.bot.generate_embed(
                        title="try again...", description=guess_music_data.title_str()
                    )
                    if images := await music_data.get_images(
                        pjsk_client_cog.pjsk_client
                    ):
                        out_embed_file = add_embed_thumbnail(out_embed, images[0])
                        await ctx.channel.send(file=out_embed_file, embed=out_embed)
                    else:
                        await ctx.channel.send(embed=out_embed)

        self.guess_in_progress[ctx.channel.id] = Guess(
            music_data, asyncio.create_task(check_guess())
        )

        if out_embed_file:
            await ctx.send(file=out_embed_file, embed=out_embed)
        else:
            await ctx.send(embed=out_embed)

    @music.command()
    async def endguess(self, ctx: Context[BotClient]):
        await ctx.defer()

        if (guess := self.guess_in_progress.pop(ctx.channel.id, None)) is None:
            out_embed = ctx.bot.generate_embed(title="no guess found!")
            await ctx.send(embed=out_embed)
            return

        if (pjsk_client_cog := get_pjsk_client_cog(ctx.bot)) is None:
            await ctx.send("please load pjsk_client extension")
            return

        guess.task.cancel()

        with suppress(asyncio.CancelledError):
            await guess.task

        out_embed = ctx.bot.generate_embed(
            title="aww...", description=guess.music.title_str()
        )
        if images := await guess.music.get_images(pjsk_client_cog.pjsk_client):
            out_embed_file = add_embed_thumbnail(out_embed, images[0])
            await ctx.send(file=out_embed_file, embed=out_embed)
        else:
            await ctx.send(embed=out_embed)

    @music.command()
    async def vocal(self, ctx: Context[BotClient], id: int):
        await ctx.defer()

        if (
            (pjsk_client_cog := get_pjsk_client_cog(ctx.bot))
            and (music := pjsk_client_cog.musics_dict.get(id))
            and (music_vocals := pjsk_client_cog.music_vocal_dict.get(id))
        ):
            music_data = pjsk_client_cog.music_data_from_music(music)
            out_embed = ctx.bot.generate_embed(title=music.title)
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
                                        name = " ".join(
                                            n
                                            for n in [
                                                game_character.first_name,
                                                game_character.given_name,
                                            ]
                                            if n
                                        )
                                        ruby_name = " ".join(
                                            n
                                            for n in [
                                                game_character.first_name_ruby,
                                                game_character.given_name_ruby,
                                            ]
                                            if n
                                        )
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

                if images := await music_data.get_images(pjsk_client_cog.pjsk_client):
                    out_embed_file = add_embed_thumbnail(out_embed, images[0])
                    await ctx.send(file=out_embed_file, embed=out_embed)
                else:
                    await ctx.send(embed=out_embed)
        else:
            await ctx.send("Not found!")


async def setup(client: BotClient):
    await client.add_cog(MusicCog())
