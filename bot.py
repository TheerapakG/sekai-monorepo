import bisect
from collections import defaultdict
from dataclasses import dataclass
import datetime
import dateutil.parser
import discord
import discord.ext.tasks as tasks
from dotenv import load_dotenv
import git
import os
from pathlib import Path
from pjsekai.enums.enums import MusicDifficultyType
from pjsekai.enums.platform import Platform
from pjsekai.enums.unknown import Unknown
from async_pjsekai.models.master_data import (
    CharacterType,
    GameCharacter,
    Music,
    MusicCategory,
    MusicDifficulty,
    MusicDifficultyType,
    MusicVocal,
    OutsideCharacter,
    ReleaseCondition,
    ResourceBox,
    ResourceBoxPurpose,
    ResourceBoxType,
    ResourceType,
)
import shutil
import subprocess
from typing import Optional, Literal

from async_pjsekai.client import Client

import jycm.helper

jycm.helper.make_json_path_key = lambda l: l
from jycm.jycm import YouchamaJsonDiffer

load_dotenv()

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

CATEGORY = {
    MusicCategory.MV_2D.value: "2d",
    MusicCategory.MV.value: "3d",
    MusicCategory.ORIGINAL.value: "original",
}

TAG_SHORT = {
    "vocaloid": "vir",
    "light_music_club": "leo",
    "idol": "mor",
    "street": "viv",
    "theme_park": "won",
    "school_refusal": "25j",
    "other": "oth",
}

TAG_LONG = {
    "vocaloid": "VIRTUAL SINGERS",
    "light_music_club": "Leo/need",
    "idol": "MORE MORE JUMP!",
    "street": "Vivid BAD SQUAD",
    "theme_park": "Wonderlands x Showtime",
    "school_refusal": "25-ji, Nightcord de.",
    "other": "other",
}

import UnityPy
import UnityPy.config
from UnityPy.tools.extractor import EXPORT_TYPES, export_obj

UnityPy.config.FALLBACK_UNITY_VERSION = Platform.ANDROID.unity_version

export_types_keys = list(EXPORT_TYPES.keys())


def defaulted_export_index(type):
    try:
        return export_types_keys.index(type)
    except (IndexError, ValueError):
        return 999


class MyClient(discord.Client):
    announce_channel: Optional[discord.TextChannel]

    def __init__(self, *, intents: discord.Intents):
        activity = discord.Game(name=BOT_VERSION)
        super().__init__(activity=activity, intents=intents)
        self.tree = discord.app_commands.CommandTree(self)
        self.announce_channel = None

        pjsk_path = (
            Path(os.environ["PJSK_DATA"]) if "PJSK_DATA" in os.environ else Path.cwd()
        )
        self.pjsk_client = Client(
            bytes(os.environ["KEY"], encoding="utf-8"),
            bytes(os.environ["IV"], encoding="utf-8"),
            system_info_file_path=str((pjsk_path / "system-info.json").absolute()),
            master_data_file_path=str((pjsk_path / "master-data.json").absolute()),
            user_data_file_path=str((pjsk_path / "user-data.json").absolute()),
            asset_directory=str((pjsk_path / "asset").absolute()),
        )

        self.musics_dict: dict[int, Music] = {}
        self.musics_by_publish_at_list: list[Music] = []
        self.difficulties_dict: dict[
            int, dict[MusicDifficultyType | Unknown, MusicDifficulty]
        ] = {}
        self.release_conditions_dict: dict[int, ReleaseCondition] = {}
        self.music_resource_boxes_dict: dict[int, ResourceBox] = {}
        self.music_tags_dict: defaultdict[int, set[str]] = defaultdict(set)
        self.music_vocal_dict: defaultdict[int, list[MusicVocal]] = defaultdict(list)
        self.game_character_dict: dict[int, GameCharacter] = {}
        self.outside_character_dict: dict[int, OutsideCharacter] = {}

    async def setup_hook(self):
        await self.pjsk_client.start()
        if not any(dict(self.pjsk_client.master_data).values()):
            await self.pjsk_client.update_all()
        self.prepare_data_dicts()

    async def setup_guild(self, guild: discord.Guild):
        if "TEST" in os.environ:
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

    def prepare_data_dicts(self):
        self.musics_dict.clear()
        if musics := self.pjsk_client.master_data.musics:
            for music in musics:
                if music_id := music.id:
                    self.musics_dict[music_id] = music
            self.musics_by_publish_at_list = sorted(
                musics,
                key=lambda music: music.published_at if music.published_at else -1,
            )

        self.difficulties_dict.clear()
        if difficulties := self.pjsk_client.master_data.music_difficulties:
            for difficulty in difficulties:
                if (music_id := difficulty.music_id) and (
                    music_difficulty := difficulty.music_difficulty
                ):
                    difficulty_types_dict = self.difficulties_dict.get(music_id, {})
                    difficulty_types_dict[music_difficulty] = difficulty
                    self.difficulties_dict[music_id] = difficulty_types_dict

        self.release_conditions_dict.clear()
        if release_conditions := self.pjsk_client.master_data.release_conditions:
            for condition in release_conditions:
                if condition_id := condition.id:
                    self.release_conditions_dict[condition_id] = condition

        self.music_resource_boxes_dict.clear()
        if resource_boxes := self.pjsk_client.master_data.resource_boxes:
            for resource_box in resource_boxes:
                if (
                    resource_box.resource_box_purpose == ResourceBoxPurpose.SHOP_ITEM
                    and resource_box.resource_box_type == ResourceBoxType.EXPAND
                ):
                    if details := resource_box.details:
                        for detail in details:
                            if (detail.resource_type == ResourceType.MUSIC) and (
                                resource_id := detail.resource_id
                            ):
                                self.music_resource_boxes_dict[
                                    resource_id
                                ] = resource_box

        self.music_tags_dict.clear()
        if tags := self.pjsk_client.master_data.music_tags:
            for tag in tags:
                if (music_id := tag.music_id) and (music_tag := tag.music_tag):
                    self.music_tags_dict[music_id].add(music_tag)

        self.music_vocal_dict.clear()
        if music_vocals := self.pjsk_client.master_data.music_vocals:
            for music_vocal in music_vocals:
                if music_id := music_vocal.music_id:
                    self.music_vocal_dict[music_id].append(music_vocal)

        self.game_character_dict.clear()
        if game_characters := self.pjsk_client.master_data.game_characters:
            for character in game_characters:
                if character_id := character.id:
                    self.game_character_dict[character_id] = character

        self.outside_character_dict.clear()
        if outside_characters := self.pjsk_client.master_data.outside_characters:
            for character in outside_characters:
                if character_id := character.id:
                    self.outside_character_dict[character_id] = character

    async def load_asset(self, asset_bundle_str: str, force: bool = False) -> list[str]:
        if directory := self.pjsk_client.asset_directory:
            if (
                (asset := self.pjsk_client.asset)
                and (asset_bundle_info := asset.asset_bundle_info)
                and (bundles := asset_bundle_info.bundles)
            ):
                bundle_hash = (
                    bundles[asset_bundle_str].hash
                    if asset_bundle_str in bundles
                    else None
                )
                if not bundle_hash:
                    bundle_hash = ""

                if (directory / "bundle" / f"{asset_bundle_str}.unity3d").exists():
                    try:
                        with open(directory / "hash" / asset_bundle_str, "r") as f:
                            if f.read() == bundle_hash and not force:
                                print(f"bundle {asset_bundle_str} already updated")
                                with open(
                                    directory / "path" / asset_bundle_str, "r"
                                ) as f:
                                    return f.readlines()
                    except FileNotFoundError:
                        pass

                    print(f"updating bundle {asset_bundle_str}")
                else:
                    print(f"downloading bundle {asset_bundle_str}")

                paths: list[str] = []

                async with self.pjsk_client.api_manager.download_asset_bundle(
                    asset_bundle_str
                ) as asset_bundle:
                    (directory / "bundle" / asset_bundle_str).parent.mkdir(
                        parents=True, exist_ok=True
                    )
                    with open(
                        directory / "bundle" / f"{asset_bundle_str}.unity3d", "wb"
                    ) as f:
                        async for chunk in asset_bundle.chunks:
                            f.write(chunk)

                    env = UnityPy.load(
                        str(directory / "bundle" / f"{asset_bundle_str}.unity3d")
                    )
                    container = sorted(
                        env.container.items(),
                        key=lambda x: defaulted_export_index(x[1].type),
                    )

                    for obj_path, obj in container:
                        obj_path = "/".join(x for x in obj_path.split("/") if x)
                        obj_dest = directory / obj_path
                        obj_dest.parent.mkdir(parents=True, exist_ok=True)

                        paths.append(obj_path)

                        print(f"extracting {obj_path}")

                        export_obj(
                            obj,  # type: ignore
                            obj_dest,
                        )

                        if obj_dest.suffixes == [".acb", ".bytes"]:
                            shutil.copy(obj_dest, obj_dest.with_suffix(""))
                            subprocess.run(
                                [
                                    "./vgmstream-cli",
                                    "-o",
                                    obj_dest.parent / "?n.wav",
                                    "-S",
                                    "0",
                                    obj_dest.with_suffix(""),
                                ]
                            )

                (directory / "path" / asset_bundle_str).parent.mkdir(
                    parents=True, exist_ok=True
                )
                with open(directory / "path" / asset_bundle_str, "w") as f:
                    f.writelines(paths)

                (directory / "hash" / asset_bundle_str).parent.mkdir(
                    parents=True, exist_ok=True
                )
                with open(directory / "hash" / asset_bundle_str, "w") as f:
                    f.write(bundle_hash)

                print(f"updated bundle {asset_bundle_str}")
                return paths
        return []

    @tasks.loop(seconds=60)
    async def diff_musics_task(self):
        musics = self.musics_dict.copy()

        if await self.pjsk_client.update_all():
            self.prepare_data_dicts()
            new_musics = self.musics_dict.copy()

            musics_diff = YouchamaJsonDiffer(musics, new_musics).get_diff()
            if "dict:add" in musics_diff:
                for diff in musics_diff["dict:add"]:
                    if len(diff["right_path"]) == 1:
                        music: Music = diff["right"]
                        music_data = MusicData.from_music(music)
                        if announce_channel := self.announce_channel:
                            out_embed = discord.Embed(title=f"new music found!")
                            out_embed.set_footer(text=BOT_VERSION)
                            out_embed_file = await music_data.add_embed_fields(
                                out_embed, set_title=False
                            )
                            if out_embed_file:
                                await announce_channel.send(
                                    file=out_embed_file, embed=out_embed
                                )
                            else:
                                await announce_channel.send(embed=out_embed)


intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.event
async def on_ready():
    if "TEST" not in os.environ:
        await client.tree.sync()
    for guild in client.guilds:
        await client.setup_guild(guild)
    announce_channel = (
        client.get_channel(int(os.environ["ANNOUNCE_CHANNEL"]))
        if "ANNOUNCE_CHANNEL" in os.environ
        else None
    )
    if announce_channel and isinstance(announce_channel, discord.TextChannel):
        client.announce_channel = announce_channel
    print("CONNECTED: starting pjsk polling")
    client.diff_musics_task.start()


@client.event
async def on_resumed():
    announce_channel = (
        client.get_channel(int(os.environ["ANNOUNCE_CHANNEL"]))
        if "ANNOUNCE_CHANNEL" in os.environ
        else None
    )
    if announce_channel and isinstance(announce_channel, discord.TextChannel):
        client.announce_channel = announce_channel
    print("RESUMED: starting pjsk polling")
    client.diff_musics_task.start()


@client.event
async def on_disconnect():
    print("DISCONNECTED: canceling pjsk polling")
    client.diff_musics_task.cancel()


@client.event
async def on_guild_join(guild: discord.Guild):
    await client.setup_guild(guild)


@dataclass
class MusicData:
    title: Optional[str]
    ids: dict[str, int]
    lyricist: Optional[str]
    composer: Optional[str]
    arranger: Optional[str]
    categories: list[MusicCategory]
    tags: list[str]
    publish_at: Optional[datetime.datetime]
    difficulties: list[MusicDifficulty | None]
    release_condition: Optional[ReleaseCondition]
    asset_bundle_name: Optional[str]

    def title_str(self):
        return self.title if self.title else "??"

    def category_strs(self):
        return [
            CATEGORY[category.value]
            for category in self.categories
            if category.value and CATEGORY.get(category.value)
        ]

    def tag_short_strs(self):
        return [name for tag, name in TAG_SHORT.items() if tag in self.tags]

    def tag_long_strs(self):
        return [name for tag, name in TAG_LONG.items() if tag in self.tags]

    def publish_at_str(self):
        return f"<t:{int(self.publish_at.timestamp())}:f>" if self.publish_at else "??"

    def difficulty_short_strs(self):
        return [f"{e.play_level if e.play_level else '??'} ({e.total_note_count if e.total_note_count else '??'})" if e else "?? (??)" for e in self.difficulties]  # type: ignore

    def difficulty_long_strs(self):
        return [f"{e.music_difficulty.value}: {e.play_level if e.play_level else '??'} ({e.total_note_count if e.total_note_count else '??'})" if e else "?? (??)" for e in self.difficulties]  # type: ignore

    def ids_str(self):
        return " ".join(f"{k}: {v}" for k, v in self.ids.items() if k and v)

    def release_condition_str(self):
        if not self.release_condition:
            return "??"

        match self.release_condition.id:
            case None:
                return "??"
            case 1:
                return "unlocked"
            case 5:
                return "shop: 2"
            case 10:
                return "present"
            case _:
                return f"{self.release_condition.id}: {self.release_condition.sentence}"

    def get_str(self):
        categories = self.category_strs()
        tags = self.tag_short_strs()
        return " | ".join(
            [
                " ".join(
                    [
                        s
                        for s in [
                            f"**{self.title_str()}**",
                            f"[{'|'.join(categories)}]" if categories else None,
                            f"[{'|'.join(tags)}]" if tags else None,
                            self.publish_at_str(),
                        ]
                        if s
                    ]
                ),
                f"LV: {'/'.join(self.difficulty_short_strs())}",
                self.ids_str(),
                self.release_condition_str(),
            ]
        )

    async def add_embed_thumbnail(self, embed: discord.Embed):
        img_path = await client.load_asset(f"music/jacket/{self.asset_bundle_name}")

        if img_path and (directory := client.pjsk_client.asset_directory):
            filename = Path(img_path[0]).name
            file = discord.File(directory / img_path[0], filename=filename)
            embed.set_thumbnail(url=f"attachment://{filename}")
            return file

    async def add_embed_fields(self, embed: discord.Embed, set_title=True):
        categories = self.category_strs()
        categories_str = f"{', '.join(categories)}" if categories else None
        tags = self.tag_long_strs()
        tag_str = f"{', '.join(tags)}" if tags else None

        if set_title:
            embed.title = self.title_str()
        else:
            embed.add_field(name="title", value=self.title_str())

        embed.add_field(name="ids", value=self.ids_str(), inline=False)
        embed.add_field(
            name="lyricist", value=self.lyricist if self.lyricist else "-", inline=False
        )
        embed.add_field(name="composer", value=self.composer if self.composer else "-")
        embed.add_field(name="arranger", value=self.arranger if self.arranger else "-")
        embed.add_field(name="categories", value=categories_str, inline=False)
        embed.add_field(name="tags", value=tag_str)
        embed.add_field(name="publish at", value=self.publish_at_str(), inline=False)
        embed.add_field(
            name="difficulties",
            value="\n".join(self.difficulty_long_strs()),
            inline=False,
        )
        embed.add_field(
            name="release condition", value=self.release_condition_str(), inline=False
        )

        return await self.add_embed_thumbnail(embed)

    @classmethod
    def from_music(cls, music: Music):
        music_categories: list[MusicCategory] = (
            [
                category
                for category in music.categories
                if isinstance(category, MusicCategory)
                and category != MusicCategory.IMAGE
            ]
            if music.categories
            else []
        )
        music_tags: list[str] = []
        music_ids: dict[str, int] = {}
        music_difficulties: list[MusicDifficulty | None] = []
        if music.id:
            music_tags = (
                [tag for tag in client.music_tags_dict[music.id]]
                if client.music_tags_dict[music.id]
                else []
            )
            music_ids["m"] = music.id
            if (
                music_resource_box := client.music_resource_boxes_dict.get(music.id)
            ) and music_resource_box.id:
                music_ids["r"] = music_resource_box.id
            _music_difficulties = client.difficulties_dict.get(music.id, {})
            music_difficulties = [
                _music_difficulties.get(difficulty)
                for difficulty in MusicDifficultyType
            ]

        return cls(
            title=music.title,
            ids=music_ids,
            lyricist=music.lyricist,
            composer=music.composer,
            arranger=music.arranger,
            categories=music_categories,
            tags=music_tags,
            publish_at=music.published_at,
            difficulties=music_difficulties,
            release_condition=client.release_conditions_dict.get(
                music.release_condition_id
            )
            if music.release_condition_id
            else None,
            asset_bundle_name=music.asset_bundle_name,
        )


class MusicListEmbedView(discord.ui.View):
    def __init__(self, time: datetime.datetime, index: int = 1):
        super().__init__()
        self.time = time
        self.index = index

    async def process_interaction(
        self, interaction: discord.Interaction[MyClient], *, edit=False
    ):
        if not edit:
            await interaction.response.defer(thinking=True)
        musics_by_publish_at_list = interaction.client.musics_by_publish_at_list
        musics = musics_by_publish_at_list[
            bisect.bisect_right(
                musics_by_publish_at_list,
                self.time,
                key=lambda music: music.published_at if music.published_at else -1,
            ) :
        ]
        music_datas = [MusicData.from_music(m) for m in musics]

        if len(music_datas) == 0:
            out_embed = discord.Embed(
                title=f"Music releasing after <t:{int(self.time.timestamp())}:f> ({len(music_datas)})",
                description="None!",
            )
            out_embed.set_footer(text=BOT_VERSION)
            if edit:
                await interaction.response.edit_message(embed=out_embed, view=self)
            else:
                await interaction.followup.send(embed=out_embed)
        else:
            self.index = max(min(self.index, len(music_datas)), 1)
            out_embed = discord.Embed(
                title=f"Music releasing after <t:{int(self.time.timestamp())}:f> ({self.index}/{len(music_datas)})"
            )
            out_embed_file = await music_datas[self.index - 1].add_embed_fields(
                out_embed, set_title=False
            )
            out_embed.set_footer(text=BOT_VERSION)
            if edit:
                await interaction.response.edit_message(
                    attachments=[out_embed_file]
                    if out_embed_file
                    else discord.utils.MISSING,
                    embed=out_embed,
                    view=self,
                )
            else:
                await interaction.followup.send(
                    file=out_embed_file if out_embed_file else discord.utils.MISSING,
                    embed=out_embed,
                    view=self,
                )

    @discord.ui.button(label="previous", style=discord.ButtonStyle.primary)
    async def previous(
        self, interaction: discord.Interaction[MyClient], button: discord.ui.Button
    ):
        self.index = self.index - 1
        await self.process_interaction(interaction, edit=True)

    @discord.ui.button(label="next", style=discord.ButtonStyle.primary)
    async def next(
        self, interaction: discord.Interaction[MyClient], button: discord.ui.Button
    ):
        self.index = self.index + 1
        await self.process_interaction(interaction, edit=True)


class MusicGroup(discord.app_commands.Group):
    @discord.app_commands.command()
    async def list(
        self,
        interaction: discord.Interaction[MyClient],
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
                await interaction.response.defer(thinking=True)
                musics_by_publish_at_list = interaction.client.musics_by_publish_at_list
                musics = musics_by_publish_at_list[
                    bisect.bisect_right(
                        musics_by_publish_at_list,
                        after_dt,
                        key=lambda music: music.published_at
                        if music.published_at
                        else -1,
                    ) :
                ]
                music_datas = [MusicData.from_music(m) for m in musics]
                out_strs = (
                    [m.get_str() for m in music_datas] if music_datas else ["None!"]
                )
                await interaction.followup.send("\n".join(["```", *out_strs, "```"]))
            case "embed":
                view = MusicListEmbedView(after_dt)
                await view.process_interaction(interaction)
            case _:
                await interaction.response.defer(thinking=True)
                musics_by_publish_at_list = interaction.client.musics_by_publish_at_list
                musics = musics_by_publish_at_list[
                    bisect.bisect_right(
                        musics_by_publish_at_list,
                        after_dt,
                        key=lambda music: music.published_at
                        if music.published_at
                        else -1,
                    ) :
                ]
                music_datas = [MusicData.from_music(m) for m in musics]
                out_strs = (
                    [m.get_str() for m in music_datas] if music_datas else ["None!"]
                )
                await interaction.followup.send("\n".join(out_strs))

    @discord.app_commands.command()
    async def view(self, interaction: discord.Interaction[MyClient], id: int):
        await interaction.response.defer(thinking=True)

        if music := interaction.client.musics_dict.get(id):
            music_data = MusicData.from_music(music)
            out_embed = discord.Embed()
            out_embed.set_footer(text=BOT_VERSION)
            out_embed_file = await music_data.add_embed_fields(out_embed)
            if out_embed_file:
                await interaction.followup.send(file=out_embed_file, embed=out_embed)
            else:
                await interaction.followup.send(embed=out_embed)
        else:
            await interaction.followup.send("Not found!")

    @discord.app_commands.command()
    async def vocal(self, interaction: discord.Interaction[MyClient], id: int):
        await interaction.response.defer(thinking=True)

        if (music := interaction.client.musics_dict.get(id)) and (
            music_vocals := interaction.client.music_vocal_dict.get(id)
        ):
            music_data = MusicData.from_music(music)
            out_embed = discord.Embed()
            out_embed.title = music.title
            for music_vocal in music_vocals:
                character_list = []
                if characters := music_vocal.characters:
                    for character in characters:
                        if character_id := character.character_id:
                            match character.character_type:
                                case CharacterType.GAME_CHARACTER:
                                    if game_character := interaction.client.game_character_dict.get(
                                        character_id
                                    ):
                                        name = f"{game_character.first_name} {game_character.given_name}"
                                        ruby_name = f"{game_character.first_name_ruby} {game_character.given_name_ruby}"
                                        character_list.append(f"{name} ({ruby_name})")
                                    else:
                                        character_list.append("<unknown>")
                                case CharacterType.OUTSIDE_CHARACTER:
                                    if (
                                        outside_character := interaction.client.outside_character_dict.get(
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
            out_embed_file = await music_data.add_embed_thumbnail(out_embed)
            if out_embed_file:
                await interaction.followup.send(file=out_embed_file, embed=out_embed)
            else:
                await interaction.followup.send(embed=out_embed)
        else:
            await interaction.followup.send("Not found!")


client.tree.add_command(MusicGroup(name="music"))

client.run(os.environ["TOKEN"])
