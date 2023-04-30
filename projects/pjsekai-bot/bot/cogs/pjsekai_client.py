from collections import defaultdict
from dataclasses import astuple
import discord
from discord.ext.commands import Cog
import discord.ext.tasks as tasks
import os
from pathlib import Path
from async_pjsekai.client import Client
from pjsekai.enums.enums import MusicDifficultyType
from pjsekai.enums.platform import Platform
from pjsekai.enums.unknown import Unknown
from async_pjsekai.models.master_data import (
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

from ..bot.client import BOT_VERSION, BotClient
from ..models.music import MusicData


import jycm.helper

jycm.helper.make_json_path_key = lambda l: l
from jycm.jycm import YouchamaJsonDiffer

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


class PjskClientCog(Cog):
    def __init__(self, client: BotClient) -> None:
        super().__init__()

        self.client = client

        pjsk_path = (
            Path(os.environ["PJSK_DATA"]) if "PJSK_DATA" in os.environ else Path.cwd()
        )
        self.pjsk_client = Client(
            bytes(os.environ["KEY"], encoding="utf-8"),
            bytes(os.environ["IV"], encoding="utf-8"),
            system_info_file_path=str((pjsk_path / "system-info.msgpack").absolute()),
            master_data_file_path=str((pjsk_path / "master-data.msgpack").absolute()),
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

    async def cog_load(self):
        await self.pjsk_client.start()
        update = False
        async with self.pjsk_client.master_data as master_data:
            if not any(astuple(master_data)):
                update = True
        if update:
            await self.pjsk_client.update_all()
        await self.prepare_data_dicts()
        self.diff_musics.start()

    async def cog_unload(self):
        self.diff_musics.cancel()
        await self.pjsk_client.close()

    async def prepare_data_dicts(self):
        async with self.pjsk_client.master_data as master_data:
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
            async with asset.asset_bundle_info as asset_bundle_info:
                if asset_bundle_info and (bundles := asset_bundle_info.bundles):
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

    @tasks.loop(seconds=60)
    async def diff_musics(self):
        musics = self.musics_dict.copy()

        if await self.pjsk_client.update_all():
            await self.prepare_data_dicts()
            new_musics = self.musics_dict.copy()

            musics_diff = YouchamaJsonDiffer(musics, new_musics).get_diff()
            if "dict:add" in musics_diff:
                for diff in musics_diff["dict:add"]:
                    if len(diff["right_path"]) == 1:
                        music: Music = diff["right"]
                        music_data = self.music_data_from_music(music)
                        if announce_channel := self.client.announce_channel:
                            out_embed = discord.Embed(title=f"new music found!")
                            out_embed.set_footer(text=BOT_VERSION)
                            out_embed_file = await self.add_music_embed_fields(
                                music_data, out_embed, set_title=False
                            )
                            if out_embed_file:
                                await announce_channel.send(
                                    file=out_embed_file, embed=out_embed
                                )
                            else:
                                await announce_channel.send(embed=out_embed)

    @diff_musics.before_loop
    async def before_diff_musics(self):
        await self.client.wait_until_ready()


def get_pjsk_client_cog(client: BotClient):
    if cog := client.get_cog("PjskClientCog"):
        if isinstance(cog, PjskClientCog):
            return cog
