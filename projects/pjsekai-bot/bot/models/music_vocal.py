# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
import datetime
from functools import partial
from typing import Optional

from async_pjsekai.client import Client
from async_pjsekai.models.master_data import (
    ReleaseCondition,
)
import discord

from .music import MusicData
from ..utils.asset import load_asset


@dataclass
class MusicVocalData:
    music: Optional[MusicData]
    caption: Optional[str]
    character_list: list[str]
    publish_at: Optional[datetime.datetime]
    release_condition: Optional[ReleaseCondition]
    asset_bundle_name: Optional[str]

    def character_str(self):
        return ", ".join(self.character_list)

    def publish_at_str(self):
        return f"<t:{int(self.publish_at.timestamp())}:f>" if self.publish_at else "??"

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
            case 9:
                return "shop: 4"
            case 10:
                return "present"
            case _:
                return f"{self.release_condition.id}: {self.release_condition.sentence}"

    def _apply_embed_fields(self, set_publish_info: bool, embed: discord.Embed):
        embed.add_field(
            name=self.caption,
            value=self.character_str(),
            inline=False,
        )
        if set_publish_info:
            embed.add_field(
                name="publish at", value=self.publish_at_str(), inline=False
            )
            embed.add_field(
                name="release condition",
                value=self.release_condition_str(),
                inline=False,
            )

    def apply_embed_fields(self, set_publish_info: bool = True):
        return partial(self._apply_embed_fields, set_publish_info)

    async def get_images(self, client: Client):
        return await self.music.get_images(client) if self.music else []

    async def get_vocals(self, client: Client):
        return (
            await load_asset(client, f"music/long/{self.asset_bundle_name}")
            if self.asset_bundle_name
            else []
        )
