# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

import json
from typing import TYPE_CHECKING, Optional

from discord.ext.commands import hybrid_group, is_owner, Cog, Context
import jq

from ..bot.client import BotClient

if TYPE_CHECKING:
    from .pjsekai_client import PjskClientCog


def get_pjsk_client_cog(client: BotClient):
    from .pjsekai_client import PjskClientCog  # get fresh version of cog

    if cog := client.get_cog(PjskClientCog.__cog_name__):
        if isinstance(cog, PjskClientCog):
            return cog


class DumpCog(Cog):
    @hybrid_group()
    async def dump(self, ctx: Context[BotClient]):
        pass

    @dump.command()
    @is_owner()
    async def master_data(self, ctx: Context[BotClient], pattern: str):
        await ctx.defer()
        if pjsk_client_cog := get_pjsk_client_cog(ctx.bot):
            async with pjsk_client_cog.pjsk_client.system_info as system_info:
                await ctx.send(
                    "\n".join(
                        [
                            "```",
                            json.dumps(
                                jq.compile(pattern)
                                .input_value(
                                    await pjsk_client_cog.pjsk_client.api_manager.get_master_data(
                                        system_info
                                    )
                                )
                                .all()
                            ),
                            "```",
                        ]
                    )
                )


async def setup(client: BotClient):
    await client.add_cog(DumpCog())
