import asyncio
import discord
from dotenv import load_dotenv
import os

from bot.bot.client import BotClient
from bot.cogs.pjsekai_client import PjskClientCog
from bot.cogs.music import MusicCog
from bot.tasks.music import diff_musics_task


def main():
    load_dotenv()

    intents = discord.Intents.default()
    client = BotClient(
        [PjskClientCog(), MusicCog()], [diff_musics_task], intents=intents
    )

    client.run(os.environ["TOKEN"])


if __name__ == "__main__":
    main()
