# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

import aiofiles
import aiofiles.os
import asyncio
from collections import defaultdict
from dataclasses import astuple
import discord
from discord.ext.commands import Cog
import discord.ext.tasks as tasks
import os
from pathlib import Path
from async_pjsekai.client import Client
from async_pjsekai.enums.enums import (
    MusicCategory,
    MusicDifficultyType,
    ResourceBoxPurpose,
    ResourceBoxType,
    ResourceType,
)
from async_pjsekai.enums.platform import Platform
from async_pjsekai.enums.unknown import Unknown
from async_pjsekai.models.master_data import (
    GameCharacter,
    MasterData,
    Music,
    MusicDifficulty,
    MusicVocal,
    OutsideCharacter,
    ReleaseCondition,
    ResourceBox,
)

from ..bot.client import BOT_VERSION, BotClient
from ..models.music import MusicData


import jycm.helper

jycm.helper.make_json_path_key = lambda l: l
from jycm.jycm import YouchamaJsonDiffer

import UnityPy
import UnityPy.config
import UnityPy.files
from UnityPy.tools.extractor import EXPORT_TYPES, export_obj

UnityPy.config.FALLBACK_UNITY_VERSION = Platform.ANDROID.unity_version

export_types_keys = list(EXPORT_TYPES.keys())


def defaulted_export_index(type):
    try:
        return export_types_keys.index(type)
    except (IndexError, ValueError):
        return 999


async def extract_acb_bytes(path: Path):
    async with aiofiles.open(path, "rb") as src, aiofiles.open(
        path.with_suffix(""), "wb"
    ) as dst:
        await aiofiles.os.sendfile(
            dst.fileno(), src.fileno(), 0, (await aiofiles.os.stat(path)).st_size
        )
    process = await asyncio.subprocess.create_subprocess_exec(
        "/usr/bin/vgmstream-cli",
        "-o",
        path.parent / "?n.wav",
        "-S",
        "0",
        path.with_suffix(""),
    )
    return await process.wait()


async def extract(directory: Path, path: str, obj: UnityPy.files.ObjectReader):
    print(f"extracting {path}")

    dst = directory / path
    await aiofiles.os.makedirs(dst.parent, exist_ok=True)

    export_obj(obj, dst)  # type: ignore

    match dst.suffixes:
        case [".acb", ".bytes"]:
            await extract_acb_bytes(dst)


class PjskClientCog(Cog):
    client: BotClient
    pjsk_client: Client

    def __init__(self, client: BotClient) -> None:
        super().__init__()

        self.client = client

        pjsk_path = (
            Path(os.environ["PJSK_DATA"]) if "PJSK_DATA" in os.environ else Path.cwd()
        )
        self.pjsk_client = Client(
            bytes(os.environ["KEY"], encoding="utf-8"),
            bytes(os.environ["IV"], encoding="utf-8"),
            system_info_file_path=str((pjsk_path / "system-info.msgpack").resolve()),
            master_data_file_path=str((pjsk_path / "master-data.msgpack").resolve()),
            user_data_file_path=str((pjsk_path / "user-data.json").resolve()),
            asset_directory=str((pjsk_path / "asset").resolve()),
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

    async def cog_load(self):
        await self.pjsk_client.start()
        update = False
        async with self.pjsk_client.master_data as (master_data, sync):
            if not any(astuple(master_data)):
                update = True
        if update:
            await self.pjsk_client.update_all()
        await self.prepare_data_dicts()
        await self.pjsk_client.set_master_data(MasterData.create(), write=False)
        self.update_data.start()

    async def cog_unload(self):
        self.update_data.cancel()
        await self.pjsk_client.close()

    async def prepare_data_dicts(self):
        async with self.pjsk_client.master_data as (master_data, sync):
            if not sync:
                return

            self.musics_dict.clear()
            if musics := master_data.musics:
                for music in musics:
                    if music_id := music.id:
                        self.musics_dict[music_id] = music
                self.musics_by_publish_at_list = sorted(
                    musics,
                    key=lambda music: music.published_at if music.published_at else -1,
                )

            self.difficulties_dict.clear()
            if difficulties := master_data.music_difficulties:
                for difficulty in difficulties:
                    if (music_id := difficulty.music_id) and (
                        music_difficulty := difficulty.music_difficulty
                    ):
                        difficulty_types_dict = self.difficulties_dict.get(music_id, {})
                        difficulty_types_dict[music_difficulty] = difficulty
                        self.difficulties_dict[music_id] = difficulty_types_dict

            self.release_conditions_dict.clear()
            if release_conditions := master_data.release_conditions:
                for condition in release_conditions:
                    if condition_id := condition.id:
                        self.release_conditions_dict[condition_id] = condition

            self.music_resource_boxes_dict.clear()
            if resource_boxes := master_data.resource_boxes:
                for resource_box in resource_boxes:
                    if (
                        resource_box.resource_box_purpose
                        == ResourceBoxPurpose.SHOP_ITEM
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
            if tags := master_data.music_tags:
                for tag in tags:
                    if (music_id := tag.music_id) and (music_tag := tag.music_tag):
                        self.music_tags_dict[music_id].add(music_tag)

            self.music_vocal_dict.clear()
            if music_vocals := master_data.music_vocals:
                for music_vocal in music_vocals:
                    if music_id := music_vocal.music_id:
                        self.music_vocal_dict[music_id].append(music_vocal)

            self.game_character_dict.clear()
            if game_characters := master_data.game_characters:
                for character in game_characters:
                    if character_id := character.id:
                        self.game_character_dict[character_id] = character

            self.outside_character_dict.clear()
            if outside_characters := master_data.outside_characters:
                for character in outside_characters:
                    if character_id := character.id:
                        self.outside_character_dict[character_id] = character

    async def load_asset(self, asset_bundle_str: str, force: bool = False) -> list[str]:
        if (directory := self.pjsk_client.asset_directory) and (
            asset := self.pjsk_client.asset
        ):
            async with asset.asset_bundle_info as (asset_bundle_info, sync):
                bundle_hash = None
                if asset_bundle_info and (bundles := asset_bundle_info.bundles):
                    if asset_bundle_str in bundles:
                        bundle_hash = bundles[asset_bundle_str].hash

            if bundle_hash is None:
                bundle_hash = ""

            if force:
                print(f"downloading bundle {asset_bundle_str}")
            else:
                try:
                    async with aiofiles.open(
                        directory / "hash" / asset_bundle_str, "r"
                    ) as f:
                        if await f.read() == bundle_hash:
                            print(f"bundle {asset_bundle_str} already updated")
                            async with aiofiles.open(
                                directory / "path" / asset_bundle_str, "r"
                            ) as f:
                                return (await f.read()).splitlines()
                        else:
                            print(f"updating bundle {asset_bundle_str}")
                except FileNotFoundError:
                    print(f"downloading bundle {asset_bundle_str}")

            paths: list[str] = []
            tasks: list[asyncio.Task] = []

            async with self.pjsk_client.api_manager.download_asset_bundle(
                asset_bundle_str
            ) as asset_bundle:
                await aiofiles.os.makedirs(
                    (directory / "bundle" / asset_bundle_str).parent, exist_ok=True
                )
                async with aiofiles.open(
                    directory / "bundle" / f"{asset_bundle_str}.unity3d", "wb"
                ) as f:
                    async for chunk in asset_bundle.chunks:
                        await f.write(chunk)

            env = UnityPy.load(
                str(directory / "bundle" / f"{asset_bundle_str}.unity3d")
            )
            container = sorted(
                env.container.items(),
                key=lambda x: defaulted_export_index(x[1].type),
            )

            await aiofiles.os.makedirs(
                (directory / "path" / asset_bundle_str).parent, exist_ok=True
            )
            async with aiofiles.open(directory / "path" / asset_bundle_str, "w") as f:
                for obj_path, obj in container:
                    obj_path = "/".join(x for x in obj_path.split("/") if x)
                    paths.append(obj_path)
                    await f.write(obj_path + "\n")

                    tasks.append(asyncio.create_task(extract(directory, obj_path, obj)))

            await asyncio.gather(*tasks)

            await aiofiles.os.makedirs(
                (directory / "hash" / asset_bundle_str).parent, exist_ok=True
            )
            async with aiofiles.open(directory / "hash" / asset_bundle_str, "w") as f:
                await f.write(bundle_hash)

            print(f"updated bundle {asset_bundle_str}")
            return paths

        return []

    async def add_music_embed_thumbnail(self, music: MusicData, embed: discord.Embed):
        img_path = await self.load_asset(f"music/jacket/{music.asset_bundle_name}")

        if img_path and (directory := self.pjsk_client.asset_directory):
            filename = Path(img_path[0]).name
            file = discord.File(directory / img_path[0], filename=filename)
            embed.set_thumbnail(url=f"attachment://{filename}")
            return file

    async def add_music_embed_fields(
        self, music: MusicData, embed: discord.Embed, set_title=True
    ):
        categories = music.category_strs()
        categories_str = f"{', '.join(categories)}" if categories else None
        tags = music.tag_long_strs()
        tag_str = f"{', '.join(tags)}" if tags else None

        if set_title:
            embed.title = music.title_str()
        else:
            embed.add_field(name="title", value=music.title_str())

        embed.add_field(name="ids", value=music.ids_str(), inline=False)
        embed.add_field(
            name="lyricist",
            value=music.lyricist if music.lyricist else "-",
            inline=False,
        )
        embed.add_field(
            name="composer", value=music.composer if music.composer else "-"
        )
        embed.add_field(
            name="arranger", value=music.arranger if music.arranger else "-"
        )
        embed.add_field(name="categories", value=categories_str, inline=False)
        embed.add_field(name="tags", value=tag_str)
        embed.add_field(name="publish at", value=music.publish_at_str(), inline=False)
        embed.add_field(
            name="difficulties",
            value="\n".join(music.difficulty_long_strs()),
            inline=False,
        )
        embed.add_field(
            name="release condition", value=music.release_condition_str(), inline=False
        )

        return await self.add_music_embed_thumbnail(music, embed)

    def music_data_from_music(self, music: Music):
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
                [tag for tag in self.music_tags_dict[music.id]]
                if self.music_tags_dict[music.id]
                else []
            )
            music_ids["m"] = music.id
            if (
                music_resource_box := self.music_resource_boxes_dict.get(music.id)
            ) and music_resource_box.id:
                music_ids["r"] = music_resource_box.id
            _music_difficulties = self.difficulties_dict.get(music.id, {})
            music_difficulties = [
                _music_difficulties.get(difficulty)
                for difficulty in MusicDifficultyType
            ]

        return MusicData(
            title=music.title,
            ids=music_ids,
            lyricist=music.lyricist,
            composer=music.composer,
            arranger=music.arranger,
            categories=music_categories,
            tags=music_tags,
            publish_at=music.published_at,
            difficulties=music_difficulties,
            release_condition=self.release_conditions_dict.get(
                music.release_condition_id
            )
            if music.release_condition_id
            else None,
            asset_bundle_name=music.asset_bundle_name,
        )

    async def diff_musics(self, old_musics: dict[int, Music]):
        new_musics = self.musics_dict.copy()

        musics_diff = YouchamaJsonDiffer(old_musics, new_musics).get_diff()
        if "dict:add" in musics_diff:
            for diff in musics_diff["dict:add"]:
                if len(diff["right_path"]) == 1:
                    music: Music = diff["right"]
                    music_data = self.music_data_from_music(music)
                    if announce_channel := self.client.announce_channel:
                        out_embed = self.client.generate_embed(
                            title=f"new music found!"
                        )
                        out_embed_file = await self.add_music_embed_fields(
                            music_data, out_embed, set_title=False
                        )
                        if out_embed_file:
                            await announce_channel.send(
                                file=out_embed_file, embed=out_embed
                            )
                        else:
                            await announce_channel.send(embed=out_embed)

    @tasks.loop(seconds=60)
    async def update_data(self):
        old_musics = self.musics_dict.copy()

        await self.pjsk_client.update_all()

        await self.prepare_data_dicts()
        await self.pjsk_client.set_master_data(MasterData.create(), write=False)

        await self.diff_musics(old_musics)

    @update_data.before_loop
    async def before_diff_musics(self):
        await self.client.wait_until_ready()


def get_pjsk_client_cog(client: BotClient):
    if cog := client.get_cog("PjskClientCog"):
        if isinstance(cog, PjskClientCog):
            return cog


async def setup(client: BotClient):
    await client.add_cog(PjskClientCog(client))
