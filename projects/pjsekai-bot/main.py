# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

import asyncio
import discord
from dotenv import load_dotenv
import os

from bot.bot.client import BotClient
from bot.cogs.pjsekai_client import PjskClientCog
from bot.cogs.music import MusicCog


async def async_main():
    load_dotenv()

    discord.utils.setup_logging(root=False)

    intents = discord.Intents.default()
    client = BotClient(intents=intents)

    cogs = [PjskClientCog(client), MusicCog()]

    async with client:
        try:
            await asyncio.gather(*(client.add_cog(cog) for cog in cogs))
            await client.start(os.environ["TOKEN"])
        finally:
            await client.close()
            await asyncio.gather(
                *(client.remove_cog(cog) for cog in client.cogs.keys())
            )


def main():
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        return


if __name__ == "__main__":
    main()
