# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

from io import BytesIO
import cv2
import json
import aiofiles
import aiofiles.os
import asyncio
from collections import defaultdict
from dataclasses import astuple
import aiohttp
import discord
from discord.ext.commands import Cog
import discord.ext.tasks as tasks
import logging
import numpy as np
import os
from pathlib import Path
from pykakasi import kakasi
import traceback
from typing import TYPE_CHECKING

from async_pjsekai.client import Client
from async_pjsekai.enums.enums import (
    CharacterType,
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

from ..bot.client import BotClient
from ..models.music import MusicData, MusicVocalData
from ..schema.schema import ChannelIntentEnum
from ..utils import crop_rotated_rectangle


if TYPE_CHECKING:
    from .channel import ChannelCog


def get_channel_cog(client: BotClient):
    from .channel import ChannelCog  # get fresh version of cog

    if cog := client.get_cog(ChannelCog.__cog_name__):
        if isinstance(cog, ChannelCog):
            return cog


log = logging.getLogger(__name__)

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
    async with (
        aiofiles.open(path, "rb") as src,
        aiofiles.open(path.with_suffix(""), "wb") as dst,
    ):
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
    await process.wait()


async def convert_wav(vocal_path: Path, jacket_path: Path):
    process = await asyncio.subprocess.create_subprocess_exec(
        "/usr/bin/ffmpeg",
        "-y",
        "-loop",
        "1",
        "-r",
        "1",
        "-i",
        jacket_path,
        "-i",
        vocal_path,
        "-c:v",
        "libx264",
        "-profile:v",
        "baseline",
        "-level",
        "3.0",
        "-pix_fmt",
        "yuv420p",
        "-shortest",
        vocal_path.with_suffix(".mp4"),
    )
    await process.wait()
    return vocal_path.with_suffix(".mp4")


async def extract(directory: Path, path: str, obj: UnityPy.files.ObjectReader):
    log.info(f"extracting {path}")

    dst = directory / path
    await aiofiles.os.makedirs(dst.parent, exist_ok=True)

    export_obj(obj, dst)  # type: ignore

    match dst.suffixes:
        case [".acb", ".bytes"]:
            await extract_acb_bytes(dst)


class PjskClientCog(Cog):
    client: BotClient
    pjsk_client: Client
    last_update_data_exc: Exception | None

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
            user_data_file_path=str((pjsk_path / "user-data.msgpack").resolve()),
            asset_directory=str((pjsk_path / "asset").resolve()),
        )

        self.musics_dict: dict[int, Music] = {}
        self.vocals_dict: dict[int, MusicVocal] = {}
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

        self.last_update_data_exc = None

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

            self.vocals_dict.clear()
            if music_vocals := master_data.music_vocals:
                for vocal in music_vocals:
                    if vocal_id := vocal.id:
                        self.vocals_dict[vocal_id] = vocal

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
                                    self.music_resource_boxes_dict[resource_id] = (
                                        resource_box
                                    )

            self.music_tags_dict.clear()
            if tags := master_data.music_tags:
                for tag in tags:
                    if (music_id := tag.music_id) and (music_tag := tag.music_tag):
                        self.music_tags_dict[music_id].add(music_tag)

            self.music_vocal_dict.clear()
            for vocal in self.vocals_dict.values():
                if music_id := vocal.music_id:
                    self.music_vocal_dict[music_id].append(vocal)

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
                log.info(f"downloading bundle {asset_bundle_str}")
            else:
                try:
                    async with aiofiles.open(
                        directory / "hash" / asset_bundle_str, "r"
                    ) as f:
                        if await f.read() == bundle_hash:
                            log.info(f"bundle {asset_bundle_str} already updated")
                            async with aiofiles.open(
                                directory / "path" / asset_bundle_str, "r"
                            ) as f:
                                return (await f.read()).splitlines()
                        else:
                            log.info(f"updating bundle {asset_bundle_str}")
                except FileNotFoundError:
                    log.info(f"downloading bundle {asset_bundle_str}")

            paths: list[str] = []
            tasks: list[asyncio.Task] = []

            async with self.pjsk_client.download_asset_bundle(
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

            log.info(f"updated bundle {asset_bundle_str}")
            return paths

        return []

    async def add_music_embed_thumbnail(self, music: MusicData, embed: discord.Embed):
        img_path = await self.load_asset(f"music/jacket/{music.asset_bundle_name}")

        if img_path and (directory := self.pjsk_client.asset_directory):
            filename = Path(img_path[0]).name
            file = discord.File(directory / img_path[0], filename=filename)
            embed.set_thumbnail(url=f"attachment://{filename}")
            return file

    async def add_music_random_crop_thumbnail(
        self, music: MusicData, embed: discord.Embed
    ):
        img_path = await self.load_asset(f"music/jacket/{music.asset_bundle_name}")

        if img_path and (directory := self.pjsk_client.asset_directory):
            filename = Path(img_path[0]).name
            filepath = directory / img_path[0]

            img = cv2.imread(str(filepath))

            img_dim = min(img.shape[0], img.shape[1])

            while True:
                center = (
                    np.random.randint(low=1, high=img_dim - 1),
                    np.random.randint(low=1, high=img_dim - 1),
                )
                width = np.random.randint(low=96, high=128)
                angle = np.random.randint(low=0, high=360)
                rect = (center, (width, width), angle)
                image_cropped = crop_rotated_rectangle(image=img, rect=rect)
                if image_cropped is not None:
                    file = discord.File(
                        BytesIO(
                            cv2.imencode(filepath.suffix, image_cropped)[1].tobytes()
                        ),
                        filename=filename,
                    )
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

    async def add_music_vocal_embed_fields(
        self, music_vocal: MusicVocalData, embed: discord.Embed, set_publish_info=False
    ):
        embed.add_field(
            name=music_vocal.caption,
            value=music_vocal.character_str(),
            inline=False,
        )
        if set_publish_info:
            embed.add_field(
                name="publish at", value=music_vocal.publish_at_str(), inline=False
            )
            embed.add_field(
                name="release condition",
                value=music_vocal.release_condition_str(),
                inline=False,
            )

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
            release_condition=(
                self.release_conditions_dict.get(music.release_condition_id)
                if music.release_condition_id
                else None
            ),
            asset_bundle_name=music.asset_bundle_name,
        )

    def music_vocal_data_from_music_vocal(self, music_vocal: MusicVocal):
        character_list: list[str] = []
        if characters := music_vocal.characters:
            for character in characters:
                if character_id := character.character_id:
                    match character.character_type:
                        case CharacterType.GAME_CHARACTER:
                            if game_character := self.game_character_dict.get(
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
                                outside_character := self.outside_character_dict.get(
                                    character_id
                                )
                            ) and (name := outside_character.name):
                                character_list.append(f"{name}")
                            else:
                                character_list.append("<unknown>")
                        case _:
                            character_list.append("<unknown>")

        if music := self.musics_dict.get(music_vocal.music_id):
            return MusicVocalData(
                music=self.music_data_from_music(music),
                caption=music_vocal.caption,
                character_list=character_list,
                publish_at=music_vocal.archive_published_at,
                release_condition=(
                    self.release_conditions_dict.get(music_vocal.release_condition_id)
                    if music_vocal.release_condition_id
                    else None
                ),
            )

    async def diff_musics(self, old_musics: dict[int, Music]):
        new_musics = self.musics_dict.copy()

        musics_diff = YouchamaJsonDiffer(old_musics, new_musics).get_diff()
        if "dict:add" in musics_diff:
            for diff in musics_diff["dict:add"]:
                if len(diff["right_path"]) == 1:
                    music: Music = diff["right"]
                    music_data = self.music_data_from_music(music)

                    for music_channel in await get_channel_cog(
                        self.client
                    ).get_channels(ChannelIntentEnum.MUSIC_LEAK):
                        out_embed = self.client.generate_embed(
                            title=f"new music found!"
                        )
                        out_embed_file = await self.add_music_embed_fields(
                            music_data, out_embed, set_title=False
                        )
                        if out_embed_file:
                            await music_channel.send(
                                file=out_embed_file, embed=out_embed
                            )
                        else:
                            await music_channel.send(embed=out_embed)

    async def diff_vocals(self, old_vocals: dict[int, MusicVocal]):
        new_vocals = self.vocals_dict.copy()

        music_vocals_diff = YouchamaJsonDiffer(old_vocals, new_vocals).get_diff()
        if "dict:add" in music_vocals_diff:
            for diff in music_vocals_diff["dict:add"]:
                if len(diff["right_path"]) == 1:
                    vocal: MusicVocal = diff["right"]
                    if vocal_data := self.music_vocal_data_from_music_vocal(vocal):
                        for vocal_channel in await get_channel_cog(
                            self.client
                        ).get_channels(ChannelIntentEnum.VOCAL_LEAK):
                            out_embed = self.client.generate_embed(
                                title=f"new vocal found!"
                            )
                            await self.add_music_vocal_embed_fields(
                                vocal_data, out_embed, set_publish_info=True
                            )
                            out_embed_file = await self.add_music_embed_thumbnail(
                                vocal_data.music, out_embed
                            )
                            if out_embed_file:
                                await vocal_channel.send(
                                    file=out_embed_file, embed=out_embed
                                )
                            else:
                                await vocal_channel.send(embed=out_embed)

                            vocal_paths = await self.load_asset(
                                f"music/long/{vocal.asset_bundle_name}"
                            )
                            jacket_paths = await self.load_asset(
                                f"music/jacket/{vocal_data.music.asset_bundle_name}"
                            )

                            music_path = None
                            if (
                                vocal_paths
                                and jacket_paths
                                and (directory := self.pjsk_client.asset_directory)
                                and (
                                    vocal_path := next(
                                        (directory / vocal_paths[0]).parent.glob(
                                            "*.wav"
                                        ),
                                        None,
                                    )
                                )
                            ):
                                jacket_path = directory / jacket_paths[0]
                                music_path = await convert_wav(vocal_path, jacket_path)
                                filename = f"{vocal_data.music.title}_{vocal.asset_bundle_name}.mp4"
                                file = discord.File(music_path, filename=filename)
                                await vocal_channel.send(file=file)

    async def load_i18n(self):
        kks = kakasi()
        text_sources = {}
        text_sources["jp_title"] = {k: v.title for k, v in self.musics_dict.items()}
        text_sources["jp_pronounciation"] = {
            k: v.title for k, v in self.musics_dict.items()
        }
        text_sources["jp_roma"] = {
            k: " ".join(i["hepburn"] for i in kks.convert(v))
            for k, v in text_sources["jp_pronounciation"].items()
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://raw.githubusercontent.com/Sekai-World/sekai-i18n/main/en/music_titles.json"
            ) as response:
                text_sources["en_title"] = {
                    int(k): v
                    for k, v in (await response.json(content_type=None)).items()
                }

        if "PJSK_METADATA" in os.environ:
            try:
                with open(
                    Path(os.environ["PJSK_METADATA"]) / "music.json", encoding="utf-8"
                ) as f:
                    text_sources["metadata"] = {
                        int(k): v for k, v in json.load(f).items()
                    }
            except FileNotFoundError:
                pass

        result = {}
        for source, texts in text_sources.items():
            for k, v in texts.items():
                d = result.get(k, {})
                d[source] = v
                result[k] = d

        list_result = [{"id": k, **v} for k, v in result.items()]

        index = self.client.meilisearch_client.index("musics")
        index.add_documents(list_result, "id")
        index.update_searchable_attributes(
            ["jp_title", "jp_pronounciation", "jp_roma", "en_title", "metadata"]
        )

    @tasks.loop(seconds=300)
    async def update_data(self):
        try:
            old_musics = self.musics_dict.copy()
            old_vocals = self.vocals_dict.copy()

            await self.pjsk_client.update_all()

            await self.prepare_data_dicts()
            await self.pjsk_client.set_master_data(MasterData.create(), write=False)

            await self.diff_musics(old_musics)
            await self.diff_vocals(old_vocals)
            await self.load_i18n()

            self.last_update_data_exc = None
        except Exception as e:
            log.exception("exception while trying to update data")
            if not self.last_update_data_exc:
                out_embed = self.client.generate_embed(
                    color=discord.Color.red(),
                    title="exception while trying to update data",
                    description=f"```{traceback.format_exc()}```",
                )

                for announce_channel in await get_channel_cog(self.client).get_channels(
                    ChannelIntentEnum.ANNOUNCE
                ):
                    await announce_channel.send(embed=out_embed)

                self.last_update_data_exc = e

                await self.pjsk_client.close()
                pjsk_path = (
                    Path(os.environ["PJSK_DATA"])
                    if "PJSK_DATA" in os.environ
                    else Path.cwd()
                )
                self.pjsk_client = Client(
                    bytes(os.environ["KEY"], encoding="utf-8"),
                    bytes(os.environ["IV"], encoding="utf-8"),
                    system_info_file_path=str(
                        (pjsk_path / "system-info.msgpack").resolve()
                    ),
                    master_data_file_path=str(
                        (pjsk_path / "master-data.msgpack").resolve()
                    ),
                    user_data_file_path=str(
                        (pjsk_path / "user-data.msgpack").resolve()
                    ),
                    asset_directory=str((pjsk_path / "asset").resolve()),
                )
                await self.pjsk_client.start()

    @update_data.before_loop
    async def before_diff_musics(self):
        await self.client.wait_until_ready()


async def setup(client: BotClient):
    await client.add_cog(PjskClientCog(client))
