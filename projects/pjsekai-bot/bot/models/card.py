# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
import datetime
from functools import partial
from io import BytesIO
from typing import Optional

import cv2
import discord

from async_pjsekai.client import Client
from async_pjsekai.enums.enums import MusicCategory, CardRarityType, CardAttr, Unit
from async_pjsekai.models.master_data import CardParameter, Skill

from .game_character import GameCharacterData
from ..utils.asset import load_asset


CATEGORY = {
    MusicCategory.MV_2D.value: "2d",
    MusicCategory.MV.value: "3d",
    MusicCategory.ORIGINAL.value: "original",
}

RARITY = {
    "rarity_1": "1*",
    "rarity_2": "2*",
    "rarity_3": "3*",
    "rarity_4": "4*",
    "rarity_birthday": "birthday",
}

UNIT_SHORT = {
    "piapro": "vir",
    "light_sound": "mor",
    "idol": "mor",
    "street": "viv",
    "theme_park": "won",
    "school_refusal": "25j",
    "none": "none",
    "any": "any",
}

UNIT_LONG = {
    "piapro": "VIRTUAL SINGERS",
    "light_sound": "Leo/need",
    "idol": "MORE MORE JUMP!",
    "street": "Vivid BAD SQUAD",
    "theme_park": "Wonderlands x Showtime",
    "school_refusal": "25-ji, Nightcord de.",
    "none": "none",
    "any": "any",
}

CARD_ORDERING = ["card_normal", "card_after_training"]


@dataclass
class CardData:
    title: Optional[str]  # prefix
    ids: dict[str, int]
    character: Optional[GameCharacterData]
    rarity: Optional[CardRarityType]
    attr: Optional[CardAttr]
    support_unit: Optional[Unit]
    skill_name: Optional[str]
    skill: Optional[Skill]
    gacha_phrase: Optional[str]
    flavor_text: Optional[str]
    release_at: Optional[datetime.datetime]
    archive_published_at: Optional[datetime.datetime]
    card_parameters: Optional[list[CardParameter]]
    asset_bundle_name: Optional[str]

    def title_str(self):
        return self.title if self.title else "??"

    def ids_str(self):
        return " ".join(f"{k}: {v}" for k, v in self.ids.items() if k and v)

    def character_str(self):
        return self.character.name_long_str() if self.character else "??"

    def rarity_str(self):
        return RARITY[self.rarity.value] if self.rarity else "??"

    def attr_str(self):
        return self.attr.value if self.attr else "??"

    def support_unit_short_str(self):
        return UNIT_SHORT[self.support_unit.value] if self.support_unit else "??"

    def support_unit_long_str(self):
        return UNIT_LONG[self.support_unit.value] if self.support_unit else "??"

    def skill_name_str(self):
        return self.skill_name if self.skill_name else "??"

    def skill_str(self):
        return (
            (self.skill.description if self.skill.description else "??")
            if self.skill
            else "??"
        )

    def gacha_phrase_str(self):
        return self.gacha_phrase if self.gacha_phrase else "??"

    def flavor_text_str(self):
        return self.flavor_text if self.flavor_text else "??"

    def release_at_str(self):
        return f"<t:{int(self.release_at.timestamp())}:f>" if self.release_at else "??"

    def archive_published_at_str(self):
        return (
            f"<t:{int(self.archive_published_at.timestamp())}:f>"
            if self.archive_published_at
            else "??"
        )

    def _apply_embed_fields(self, set_title: bool, embed: discord.Embed):
        if set_title:
            embed.title = f"{self.title_str()}: {self.character_str()}"
        else:
            embed.add_field(name=self.title_str(), value=self.character_str())

        embed.add_field(name="ids", value=self.ids_str(), inline=False)
        embed.add_field(name="rarity", value=self.rarity_str())
        embed.add_field(name="attribute", value=self.attr_str())
        embed.add_field(
            name="support unit",
            value=self.support_unit_long_str(),
            inline=False,
        )
        embed.add_field(
            name=f"skill: {self.skill_name_str()}",
            value=self.skill_str(),
            inline=False,
        )
        embed.add_field(
            name="gacha phrase",
            value=self.gacha_phrase_str(),
            inline=False,
        )
        embed.add_field(
            name="release at",
            value=self.release_at_str(),
            inline=False,
        )
        embed.add_field(
            name="archive published at",
            value=self.archive_published_at_str(),
        )

    def apply_embed_fields(self, set_title: bool = True):
        return partial(self._apply_embed_fields, set_title)

    async def get_images(self, client: Client) -> list[tuple[BytesIO, str]]:
        img_path = await load_asset(
            client, f"character/member/{self.asset_bundle_name}"
        )

        if not img_path:
            return []

        filepaths_unordered = [p for p in img_path[0].parent.glob("*.png")]
        filepaths_ordering = [
            [p for p in filepaths_unordered if p.stem == s] for s in CARD_ORDERING
        ]
        filepaths = [p for ps in filepaths_ordering for p in ps]
        for p in filepaths_unordered:
            if p not in filepaths:
                filepaths.append(p)
        filepath = filepaths[0]
        filename = f"{self.asset_bundle_name}.{filepath.suffix}"
        image_concat = cv2.hconcat([cv2.imread(str(p)) for p in filepaths])
        return [
            (
                BytesIO(cv2.imencode(filepath.suffix, image_concat)[1].tobytes()),
                filename,
            )
        ]
