import discord
import discord.ext.tasks as tasks
from async_pjsekai.models.master_data import Music

import jycm.helper

jycm.helper.make_json_path_key = lambda l: l
from jycm.jycm import YouchamaJsonDiffer

from ..bot.client import BOT_VERSION, BotClient
from ..cogs.pjsekai_client import get_pjsk_client_cog
from ..models.music import MusicData
from ..models.task import Task


async def diff_musics(client: BotClient):
    if pjsk_client_cog := get_pjsk_client_cog(client):
        musics = pjsk_client_cog.musics_dict.copy()

        if await pjsk_client_cog.pjsk_client.update_all():
            await pjsk_client_cog.prepare_data_dicts()
            new_musics = pjsk_client_cog.musics_dict.copy()

            musics_diff = YouchamaJsonDiffer(musics, new_musics).get_diff()
            if "dict:add" in musics_diff:
                for diff in musics_diff["dict:add"]:
                    if len(diff["right_path"]) == 1:
                        music: Music = diff["right"]
                        music_data = MusicData.from_music(pjsk_client_cog, music)
                        if announce_channel := client.announce_channel:
                            out_embed = discord.Embed(title=f"new music found!")
                            out_embed.set_footer(text=BOT_VERSION)
                            out_embed_file = await music_data.add_embed_fields(
                                pjsk_client_cog, out_embed, set_title=False
                            )
                            if out_embed_file:
                                await announce_channel.send(
                                    file=out_embed_file, embed=out_embed
                                )
                            else:
                                await announce_channel.send(embed=out_embed)


diff_musics_task = Task(
    task=tasks.loop(seconds=60)(diff_musics), stop_on_disconnect=True
)
