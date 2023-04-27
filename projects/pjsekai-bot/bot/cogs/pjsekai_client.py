from collections import defaultdict
from dataclasses import astuple
from discord.ext.commands import Cog
import os
from pathlib import Path
from async_pjsekai.client import Client
from pjsekai.enums.enums import MusicDifficultyType
from pjsekai.enums.platform import Platform
from pjsekai.enums.unknown import Unknown
from async_pjsekai.models.master_data import (
    GameCharacter,
    Music,
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

from ..bot.client import BotClient

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
    def __init__(self) -> None:
        super().__init__()

        pjsk_path = (
            Path(os.environ["PJSK_DATA"]) if "PJSK_DATA" in os.environ else Path.cwd()
        )
        self.pjsk_client = Client(
            bytes(os.environ["KEY"], encoding="utf-8"),
            bytes(os.environ["IV"], encoding="utf-8"),
            system_info_file_path=str((pjsk_path / "system-info.json").absolute()),
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


def get_pjsk_client_cog(client: BotClient):
    if cog := client.get_cog("PjskClientCog"):
        if isinstance(cog, PjskClientCog):
            return cog
