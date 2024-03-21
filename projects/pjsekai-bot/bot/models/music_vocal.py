# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
import datetime
from typing import Optional

from async_pjsekai.client import Client
from async_pjsekai.models.master_data import (
    ReleaseCondition,
)
import discord

from .music import MusicData


@dataclass
class MusicVocalData:
    music: Optional[MusicData]
    caption: Optional[str]
    character_list: list[str]
    publish_at: Optional[datetime.datetime]
    release_condition: Optional[ReleaseCondition]

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

    async def add_embed_thumbnail(self, client: Client, embed: discord.Embed):
        if self.music:
            return await self.music.add_embed_thumbnail(client, embed)
