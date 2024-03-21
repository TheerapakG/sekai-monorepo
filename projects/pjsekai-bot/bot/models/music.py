# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
import datetime
from io import BytesIO
from typing import Optional

from async_pjsekai.client import Client
from async_pjsekai.enums.enums import MusicCategory
from async_pjsekai.models.master_data import (
    MusicDifficulty,
    ReleaseCondition,
)

import cv2
import discord
import numpy as np

from ..utils.asset import load_asset
from ..utils.crop import crop_rotated_rectangle


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

    def ids_str(self):
        return " ".join(f"{k}: {v}" for k, v in self.ids.items() if k and v)

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
        return [f"{str(e.music_difficulty)}: {e.play_level if e.play_level else '??'} ({e.total_note_count if e.total_note_count else '??'})" if e else "?? (??)" for e in self.difficulties]  # type: ignore

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
            name="lyricist",
            value=self.lyricist if self.lyricist else "-",
            inline=False,
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

    async def add_embed_thumbnail(self, client: Client, embed: discord.Embed):
        img_path = await load_asset(client, f"music/jacket/{self.asset_bundle_name}")
        if img_path:
            filepath = img_path[0]
            filename = filepath.name
            file = discord.File(img_path[0], filename=filename)
            embed.set_thumbnail(url=f"attachment://{filename}")
            return file

    async def add_embed_random_crop_thumbnail(
        self, client: Client, embed: discord.Embed
    ):
        img_path = await load_asset(client, f"music/jacket/{self.asset_bundle_name}")

        if img_path:
            filepath = img_path[0]
            filename = filepath.name

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
