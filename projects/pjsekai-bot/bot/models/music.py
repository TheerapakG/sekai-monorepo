# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
import datetime
from async_pjsekai.enums.enums import MusicCategory
from async_pjsekai.models.master_data import (
    MusicDifficulty,
    ReleaseCondition,
)
from typing import Optional


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
