# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

import asyncio
from collections import defaultdict
from dataclasses import astuple
import json
import logging
import os
from pathlib import Path
import traceback
from typing import TYPE_CHECKING

import aiohttp
import discord
from discord.ext.commands import Cog
import discord.ext.tasks as tasks
from pykakasi import kakasi

from async_pjsekai.client import Client
from async_pjsekai.enums.enums import (
    CharacterType,
    MusicCategory,
    MusicDifficultyType,
    ResourceBoxPurpose,
    ResourceBoxType,
    ResourceType,
)
from async_pjsekai.enums.unknown import Unknown
from async_pjsekai.models.master_data import (
    Card,
    MasterData,
    Music,
    MusicDifficulty,
    MusicVocal,
    OutsideCharacter,
    ReleaseCondition,
    ResourceBox,
    Skill,
)

from ..bot.client import BotClient
from ..models.card import CardData
from ..models.game_character import GameCharacterData
from ..models.music import MusicData
from ..models.music_vocal import MusicVocalData
from ..schema.schema import ChannelIntentEnum
from ..utils.asset import load_asset, convert_wav
from ..utils.discord import apply_embed_thumbnail, apply_embed_image


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
        self.cards_dict: dict[int, CardData] = {}
        self.musics_by_publish_at_list: list[Music] = []
        self.difficulties_dict: dict[
            int, dict[MusicDifficultyType | Unknown, MusicDifficulty]
        ] = {}
        self.release_conditions_dict: dict[int, ReleaseCondition] = {}
        self.music_resource_boxes_dict: dict[int, ResourceBox] = {}
        self.music_tags_dict: defaultdict[int, set[str]] = defaultdict(set)
        self.music_vocal_dict: defaultdict[int, list[MusicVocal]] = defaultdict(list)
        self.game_character_dict: dict[int, GameCharacterData] = {}
        self.outside_character_dict: dict[int, OutsideCharacter] = {}
        self.skills_dict: dict[int, Skill] = {}

        self.last_update_data_exc = None

    async def cog_load(self):
        await self.pjsk_client.start()
        update = False
        async with self.pjsk_client.master_data as (master_data, sync):
            if not any(astuple(master_data)):
                async with self.pjsk_client.replace_system_info(data_version=None):
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
                        self.game_character_dict[character_id] = GameCharacterData(
                            ids={"gc": character.id},
                            first_name=character.first_name,
                            given_name=character.given_name,
                            first_name_ruby=character.first_name_ruby,
                            given_name_ruby=character.given_name_ruby,
                        )

            self.outside_character_dict.clear()
            if outside_characters := master_data.outside_characters:
                for character in outside_characters:
                    if character_id := character.id:
                        self.outside_character_dict[character_id] = character

            self.skills_dict.clear()
            if skills := master_data.skills:
                for skill in skills:
                    if skill_id := skill.id:
                        self.skills_dict[skill_id] = skill

            self.cards_dict.clear()
            if cards := master_data.cards:
                for card in cards:
                    if card_id := card.id:
                        self.cards_dict[card_id] = CardData(
                            title=card.prefix,
                            ids={"c": card.id},
                            character=(
                                self.game_character_dict.get(card.character_id)
                                if card.character_id
                                else None
                            ),
                            rarity=card.card_rarity_type,
                            attr=card.attr,
                            support_unit=card.support_unit,
                            skill_name=card.card_skill_name,
                            skill=(
                                self.skills_dict.get(card.skill_id)
                                if card.skill_id
                                else None
                            ),
                            gacha_phrase=card.gacha_phrase,
                            flavor_text=card.flavor_text,
                            release_at=card.release_at,
                            archive_published_at=card.archive_published_at,
                            card_parameters=card.card_parameters,
                            asset_bundle_name=card.asset_bundle_name,
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
                                character_list.append(game_character.name_long_str())
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

        return MusicVocalData(
            music=(
                self.music_data_from_music(music)
                if (music_id := music_vocal.music_id)
                and (music := self.musics_dict.get(music_id))
                else None
            ),
            caption=music_vocal.caption,
            character_list=character_list,
            publish_at=music_vocal.archive_published_at,
            release_condition=(
                self.release_conditions_dict.get(music_vocal.release_condition_id)
                if music_vocal.release_condition_id
                else None
            ),
            asset_bundle_name=music_vocal.asset_bundle_name,
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
                        music_data.apply_embed_fields(set_title=False)(out_embed)

                        if images := await music_data.get_images(self.pjsk_client):
                            out_embed_file = apply_embed_thumbnail(images[0])(out_embed)
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
                            vocal_data.apply_embed_fields(set_publish_info=True)(
                                out_embed
                            )
                            images, vocals = await asyncio.gather(
                                vocal_data.get_images(self.pjsk_client),
                                vocal_data.get_vocals(self.pjsk_client),
                            )

                            if images:
                                out_embed_file = apply_embed_thumbnail(images[0])(
                                    out_embed
                                )
                                await vocal_channel.send(
                                    file=out_embed_file, embed=out_embed
                                )
                            else:
                                await vocal_channel.send(embed=out_embed)

                            music_path = None
                            if (
                                images
                                and vocals
                                and (
                                    vocal_path := next(
                                        vocals[0].parent.glob("*.wav"),
                                        None,
                                    )
                                )
                            ):
                                music_path = await convert_wav(vocal_path, images[0])
                                filename = f"{vocal_data.music.title}_{vocal.asset_bundle_name}.mp4"
                                file = discord.File(music_path, filename=filename)
                                await vocal_channel.send(file=file)

    async def diff_cards(self, old_cards: dict[int, CardData]):
        new_cards = self.cards_dict.copy()

        cards_diff = YouchamaJsonDiffer(old_cards, new_cards).get_diff()
        if "dict:add" in cards_diff:
            for diff in cards_diff["dict:add"]:
                if len(diff["right_path"]) == 1:
                    card: CardData = diff["right"]
                    for card_channel in await get_channel_cog(self.client).get_channels(
                        ChannelIntentEnum.CARD_LEAK
                    ):
                        out_embed = self.client.generate_embed(title=f"new card found!")
                        card.apply_embed_fields(set_title=False)(out_embed)
                        images = await card.get_images(self.pjsk_client)

                        if images:
                            out_embed_file = apply_embed_image(*(images[0]))(out_embed)
                            await card_channel.send(
                                file=out_embed_file, embed=out_embed
                            )
                        else:
                            await card_channel.send(embed=out_embed)

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
        index.update_ranking_rules(
            ["exactness", "words", "typo", "proximity", "attribute", "sort"]
        )
        index.add_documents(list_result, "id")
        index.update_searchable_attributes(
            ["jp_title", "jp_pronounciation", "jp_roma", "en_title", "metadata"]
        )

    @tasks.loop(seconds=120)
    async def update_data(self):
        try:
            old_musics = self.musics_dict.copy()
            old_vocals = self.vocals_dict.copy()
            old_cards = self.cards_dict.copy()

            await self.pjsk_client.update_all()

            await self.prepare_data_dicts()
            await self.pjsk_client.set_master_data(MasterData.create(), write=False)

            await self.diff_musics(old_musics)
            await self.diff_vocals(old_vocals)
            await self.diff_cards(old_cards)
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
