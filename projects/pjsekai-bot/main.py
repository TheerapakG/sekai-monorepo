# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

import asyncio
import discord
from dotenv import load_dotenv
import os

from bot.bot.client import BotClient

EXTS = [
    "bot.exts.ext_loader",
    "bot.exts.pjsekai_client",
    "bot.exts.music",
]


async def async_main():
    load_dotenv()

    discord.utils.setup_logging(root=True)

    intents = discord.Intents.default()
    client = BotClient(intents=intents)

    async with client:
        try:
            await asyncio.gather(*(client.load_extension(ext) for ext in EXTS))
            await client.start(os.environ["TOKEN"])
        finally:
            await client.close()
            await asyncio.gather(
                *(client.unload_extension(ext) for ext in client.extensions.keys())
            )


def main():
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        return


if __name__ == "__main__":
    main()
