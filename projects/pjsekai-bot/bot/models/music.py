from dataclasses import dataclass
import datetime
import discord
from pathlib import Path
from pjsekai.enums.enums import MusicDifficultyType
from async_pjsekai.models.master_data import (
    Music,
    MusicCategory,
    MusicDifficulty,
    MusicDifficultyType,
    ReleaseCondition,
)
from typing import Optional

from ..cogs.pjsekai_client import PjskClientCog


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

    async def add_embed_thumbnail(
        self, pjsk_client_cog: PjskClientCog, embed: discord.Embed
    ):
        img_path = await pjsk_client_cog.load_asset(
            f"music/jacket/{self.asset_bundle_name}"
        )

        if img_path and (directory := pjsk_client_cog.pjsk_client.asset_directory):
            filename = Path(img_path[0]).name
            file = discord.File(directory / img_path[0], filename=filename)
            embed.set_thumbnail(url=f"attachment://{filename}")
            return file

    async def add_embed_fields(
        self, pjsk_client_cog: PjskClientCog, embed: discord.Embed, set_title=True
    ):
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

        return await self.add_embed_thumbnail(pjsk_client_cog, embed)

    @classmethod
    def from_music(cls, pjsk_client_cog: PjskClientCog, music: Music):
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
                [tag for tag in pjsk_client_cog.music_tags_dict[music.id]]
                if pjsk_client_cog.music_tags_dict[music.id]
                else []
            )
            music_ids["m"] = music.id
            if (
                music_resource_box := pjsk_client_cog.music_resource_boxes_dict.get(
                    music.id
                )
            ) and music_resource_box.id:
                music_ids["r"] = music_resource_box.id
            _music_difficulties = pjsk_client_cog.difficulties_dict.get(music.id, {})
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
            release_condition=pjsk_client_cog.release_conditions_dict.get(
                music.release_condition_id
            )
            if music.release_condition_id
            else None,
            asset_bundle_name=music.asset_bundle_name,
        )
