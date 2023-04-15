from collections import defaultdict
from dataclasses import dataclass
import datetime
import discord
import discord.ext.tasks as tasks
from dotenv import load_dotenv
import git
import os
from pathlib import Path
from pjsekai.client import Client
from pjsekai.enums.enums import MusicDifficultyType
from pjsekai.enums.unknown import Unknown
from pjsekai.models.master_data import Music, MusicCategory, MusicDifficulty, MusicDifficultyType, ReleaseCondition, ResourceBox, ResourceBoxPurpose, ResourceBoxType, ResourceType
import shutil
import subprocess
from typing import Optional, Literal

import jycm.helper
jycm.helper.make_json_path_key = lambda l: l
from jycm.jycm import YouchamaJsonDiffer

load_dotenv()

repo = git.Repo(search_parent_directories=True) # type: ignore
date = repo.head.commit.committed_datetime
sha = repo.head.commit.hexsha
BOT_VERSION = f"TiaraPJSKBot-{date.date().isoformat()}-{sha[:7]}"

CATEGORY = {MusicCategory.MV_2D.value: "2d", MusicCategory.MV.value: "3d", MusicCategory.ORIGINAL.value: "original"}

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

print("starting pjsk client ...")
pjsk_path = Path(os.environ["PJSK_DATA"]) if "PJSK_DATA" in os.environ else Path.cwd()
pjsk_client = Client(
    bytes(os.environ["KEY"], encoding="utf-8"),
    bytes(os.environ["IV"], encoding="utf-8"),
    system_info_file_path=str((pjsk_path / "system-info.json").absolute()),
    master_data_file_path=str((pjsk_path / "master-data.json").absolute()),
    user_data_file_path=str((pjsk_path / "user-data.json").absolute()),
    asset_directory=str((pjsk_path / "asset").absolute()),
)

import UnityPy
import UnityPy.config
from UnityPy.tools.extractor import EXPORT_TYPES, export_obj

UnityPy.config.FALLBACK_UNITY_VERSION = pjsk_client.platform.unity_version

export_types_keys = list(EXPORT_TYPES.keys())

def defaulted_export_index(type):
    try:
        return export_types_keys.index(type)
    except (IndexError, ValueError):
        return 999

musics_dict: dict[int, Music] = {}
difficulties_dict: dict[int, dict[MusicDifficultyType | Unknown, MusicDifficulty]] = {}
release_conditions_dict: dict[int, ReleaseCondition] = {}
music_resource_boxes_dict: dict[int, ResourceBox] = {}
music_tags_dict: defaultdict[int, set[str]] = defaultdict(set)

def prepare_music_data_dicts():
    musics_dict.clear()
    if musics := pjsk_client.master_data.musics:
        for music in musics:
            if music_id := music.id:
                musics_dict[music_id] = music

    difficulties_dict.clear()
    if difficulties := pjsk_client.master_data.music_difficulties:
        for difficulty in difficulties:
            if (music_id := difficulty.music_id) and (music_difficulty := difficulty.music_difficulty):
                difficulty_types_dict = difficulties_dict.get(music_id, {})
                difficulty_types_dict[music_difficulty] = difficulty
                difficulties_dict[music_id] = difficulty_types_dict
    
    release_conditions_dict.clear()
    if release_conditions := pjsk_client.master_data.release_conditions:
        for condition in release_conditions:
            if (condition_id := condition.id):
                release_conditions_dict[condition_id] = condition
    
    music_resource_boxes_dict.clear()
    if resource_boxes := pjsk_client.master_data.resource_boxes:
        for resource_box in resource_boxes:
            if resource_box.resource_box_purpose == ResourceBoxPurpose.SHOP_ITEM and resource_box.resource_box_type == ResourceBoxType.EXPAND:
                if details := resource_box.details:
                    for detail in details:
                        if (detail.resource_type == ResourceType.MUSIC) and (resource_id := detail.resource_id):
                            music_resource_boxes_dict[resource_id] = resource_box

    music_tags_dict.clear()
    if tags := pjsk_client.master_data.music_tags:
        for tag in tags:
            if (music_id := tag.music_id) and (music_tag := tag.music_tag):
                music_tags_dict[music_id].add(music_tag)

prepare_music_data_dicts()

def load_asset(asset_bundle_str: str, force: bool = False) -> list[str]:
    if directory := pjsk_client.asset_directory:
        if (asset := pjsk_client.asset) and (asset_bundle_info := asset.asset_bundle_info) and (bundles := asset_bundle_info.bundles):
            bundle_hash = bundles[asset_bundle_str].hash if asset_bundle_str in bundles else None
            if not bundle_hash:
                bundle_hash = ""
            
            if (directory / "bundle" / f"{asset_bundle_str}.unity3d").exists():
                try:
                    with open(directory / "hash" / asset_bundle_str, "r") as f:
                        if f.read() == bundle_hash and not force:
                            print(f"bundle {asset_bundle_str} already updated")
                            with open(directory / "path" / asset_bundle_str, "r") as f:
                                return f.readlines()
                except FileNotFoundError:
                    pass
                
                print(f"updating bundle {asset_bundle_str}")
            else:
                print(f"downloading bundle {asset_bundle_str}")

            paths: list[str] = []

            with pjsk_client.api_manager.download_asset_bundle(asset_bundle_str) as asset_bundle:
                (directory / "bundle" / asset_bundle_str).parent.mkdir(parents=True, exist_ok=True)
                with open(directory / "bundle" / f"{asset_bundle_str}.unity3d", "wb") as f:
                    for chunk in asset_bundle.chunks:
                        f.write(chunk)

                env = UnityPy.load(str(directory / "bundle" / f"{asset_bundle_str}.unity3d"))
                container = sorted(
                    env.container.items(), key=lambda x: defaulted_export_index(x[1].type)
                )

                for obj_path, obj in container:
                    obj_path = "/".join(x for x in obj_path.split("/") if x)
                    obj_dest = directory / obj_path
                    obj_dest.parent.mkdir(parents=True, exist_ok=True)

                    paths.append(obj_path)

                    print(f"extracting {obj_path}")

                    export_obj(
                        obj, # type: ignore
                        obj_dest,
                    )

                    if obj_dest.suffixes == [".acb", ".bytes"]:
                        shutil.copy(obj_dest, obj_dest.with_suffix(""))
                        subprocess.run(["./vgmstream-cli", "-o", obj_dest.parent / "?n.wav", "-S", "0", obj_dest.with_suffix("")])
            
            (directory / "path" / asset_bundle_str).parent.mkdir(parents=True, exist_ok=True)
            with open(directory / "path" / asset_bundle_str, "w") as f:
                f.writelines(paths)

            (directory / "hash" / asset_bundle_str).parent.mkdir(parents=True, exist_ok=True)
            with open(directory / "hash" / asset_bundle_str, "w") as f:
                f.write(bundle_hash)
                    
            print(f"updated bundle {asset_bundle_str}")
            return paths
    return []

class MyClient(discord.Client):
    announce_channel: Optional[discord.TextChannel]
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)
        self.announce_channel = None

    async def setup_guild(self, guild: discord.Guild):
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

    @tasks.loop(seconds=60)
    async def diff_musics(self):
        musics = pjsk_client.master_data.musics
        if not musics:
            musics = []

        if pjsk_client.update_all():
            new_musics = pjsk_client.master_data.musics
            if not new_musics:
                new_musics = []
                
            musics_diff = YouchamaJsonDiffer(musics, new_musics).get_diff()
            if musics_diff["list:add"]:
                prepare_music_data_dicts()
            for diff in musics_diff["list:add"]:
                if len(diff["right_path"]) == 1:
                    music: Music = diff["right"]
                    music_data = MusicData.from_music(music)
                    if announce_channel := self.announce_channel:
                        out_embed = discord.Embed(title=f"new music found!")
                        out_embed.set_footer(text=BOT_VERSION)
                        out_embed_file = music_data.add_embed_fields(out_embed, set_title=False)
                        if out_embed_file:
                            await announce_channel.send(file=out_embed_file, embed=out_embed)
                        else:
                            await announce_channel.send(embed=out_embed)

intents = discord.Intents.default()
client = MyClient(intents=intents)

@client.event
async def on_ready():
    if "TEST" not in os.environ:
        await client.tree.sync()
    for guild in client.guilds:
        await client.setup_guild(guild)
    announce_channel = client.get_channel(int(os.environ["ANNOUNCE_CHANNEL"])) if "ANNOUNCE_CHANNEL" in os.environ else None
    if announce_channel and isinstance(announce_channel, discord.TextChannel):
        client.announce_channel = announce_channel
    print("CONNECTED: starting pjsk polling")
    client.diff_musics.start()

@client.event
async def on_disconnect():
    print("DISCONNECTED: canceling pjsk polling")
    client.diff_musics.cancel()

@client.event
async def on_guild_join(guild: discord.Guild):
    await client.setup_guild(guild)

@dataclass
class MusicData:
    title: str | None
    asset_bundle_name: str | None
    categories: list[MusicCategory]
    tags: list[str]
    publish_at: datetime.datetime | None
    difficulties: list[MusicDifficulty | None]
    ids: dict[str, int]
    release_condition: ReleaseCondition | None

    def title_str(self):
        return self.title if self.title else "??"
    
    def category_strs(self):
        return [CATEGORY[category.value] for category in self.categories if category.value and CATEGORY.get(category.value)]
    
    def tag_short_strs(self):
        return [name for tag, name in TAG_SHORT.items() if tag in self.tags]
    
    def tag_long_strs(self):
        return [name for tag, name in TAG_LONG.items() if tag in self.tags]

    def publish_at_str(self):
        return f"<t:{int(self.publish_at.timestamp())}:f>" if self.publish_at else "??"
    
    def difficulty_short_strs(self):
        return [f"{e.play_level if e.play_level else '??'} ({e.totalNoteCount if e.totalNoteCount else '??'})" if e else "?? (??)" for e in self.difficulties] # type: ignore
    
    def difficulty_long_strs(self):
        return [f"{e.music_difficulty.value}: {e.play_level if e.play_level else '??'} ({e.totalNoteCount if e.totalNoteCount else '??'})" if e else "?? (??)" for e in self.difficulties] # type: ignore
    
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
        return " | ".join([
            " ".join([
                s 
                for s 
                in [
                    f"**{self.title_str()}**",
                    f"[{'|'.join(categories)}]" if categories else None,
                    f"[{'|'.join(tags)}]" if tags else None,
                    self.publish_at_str()
                ]
                if s
            ]),
            f"LV: {'/'.join(self.difficulty_short_strs())}",
            self.ids_str(),
            self.release_condition_str()
        ])
    
    def add_embed_fields(self, embed: discord.Embed, set_title=True):
        categories = self.category_strs()
        categories_str = f"{', '.join(categories)}" if categories else None
        tags = self.tag_long_strs()
        tag_str = f"{', '.join(tags)}" if tags else None

        if set_title:
            embed.title = self.title_str()
        else:
            embed.add_field(name="title", value=self.title_str())

        embed.add_field(name="ids", value=self.ids_str(), inline=False)
        embed.add_field(name="categories", value=categories_str, inline=False)
        embed.add_field(name="tags", value=tag_str)
        embed.add_field(name="publish at", value=self.publish_at_str(), inline=False)
        embed.add_field(name="difficulties", value="\n".join(self.difficulty_long_strs()), inline=False)
        embed.add_field(name="release condition",value=self.release_condition_str(), inline=False)

        img_path = load_asset(f"music/jacket/{self.asset_bundle_name}")

        if img_path and (directory := pjsk_client.asset_directory):
            filename = Path(img_path[0]).name
            file = discord.File(directory / img_path[0], filename=filename)
            embed.set_thumbnail(url=f"attachment://{filename}")
            return file
    
    @classmethod
    def from_music(cls, music: Music):
        music_categories: list[MusicCategory] = [category for category in music.categories if isinstance(category, MusicCategory) and category != MusicCategory.IMAGE] if music.categories else []
        music_tags: list[str] = []
        music_ids: dict[str, int] = {}
        music_difficulties: list[MusicDifficulty | None] = []
        if music.id:
            music_tags = [tag for tag in music_tags_dict[music.id]] if music_tags_dict[music.id] else []
            music_ids["m"] = music.id
            if (music_resource_box := music_resource_boxes_dict.get(music.id)) and music_resource_box.id:
                music_ids["r"] = music_resource_box.id
            _music_difficulties = difficulties_dict.get(music.id, {})
            music_difficulties = [_music_difficulties.get(difficulty) for difficulty in MusicDifficultyType]

        return cls(
            title=music.title,
            asset_bundle_name=music.asset_bundle_name,
            categories=music_categories,
            tags=music_tags,
            publish_at=music.published_at,
            difficulties=music_difficulties,
            ids=music_ids,
            release_condition=release_conditions_dict.get(music.release_condition_id) if music.release_condition_id else None,
        )

class MusicGroup(discord.app_commands.Group):
    @discord.app_commands.command()
    async def list(self, interaction: discord.Interaction, design: Optional[Literal["quote", "embed"]]=None):
        await interaction.response.defer(thinking=True)
        music_datas: list[MusicData] = []
        current = datetime.datetime.now(datetime.timezone.utc)
        musics = sorted(filter(lambda music: music.published_at and music.published_at > current, musics_dict.values()), key=lambda music: music.published_at if music.published_at else -1)
        music_datas = [MusicData.from_music(m) for m in musics]

        if design == "quote":
            out_strs = [m.get_str() for m in music_datas] if music_datas else ["None!"]
            await interaction.followup.send("\n".join(["```", *out_strs, "```"]))
        elif design == "embed":
            if not music_datas:
                out_embed = discord.Embed(title=f"Music releasing after <t:{int(current.timestamp())}:f> ({len(music_datas)})", description="None!")
                out_embed.set_footer(text=BOT_VERSION)
                await interaction.followup.send(embed=out_embed)
            elif len(music_datas) > 10:
                out_embed = discord.Embed(title=f"Music releasing after <t:{int(current.timestamp())}:f> ({len(music_datas)})", description="Too many music in the list to show! Try using other design")
                out_embed.set_footer(text=BOT_VERSION)
                await interaction.followup.send(embed=out_embed)
            else:
                out_embeds: list[discord.Embed] = []
                out_embed_files: list[discord.File] = []
                for i, music_data in enumerate(music_datas, 1):
                    out_embed = discord.Embed(title=f"Music releasing after <t:{int(current.timestamp())}:f> ({i}/{len(music_datas)})")
                    out_embed.set_footer(text=BOT_VERSION)
                    out_embed_file = music_data.add_embed_fields(out_embed, set_title=False)
                    out_embeds.append(out_embed)
                    if out_embed_file:
                        out_embed_files.append(out_embed_file)
                await interaction.followup.send(files=out_embed_files, embeds=out_embeds)
        else:
            out_strs = [m.get_str() for m in music_datas] if music_datas else ["None!"]
            await interaction.followup.send("\n".join(out_strs))

    @discord.app_commands.command()
    async def view(self, interaction: discord.Interaction, id: int):
        await interaction.response.defer(thinking=True)

        if music := musics_dict.get(id):
            music_data = MusicData.from_music(music)
            out_embed = discord.Embed()
            out_embed.set_footer(text=BOT_VERSION)
            out_embed_file = music_data.add_embed_fields(out_embed)
            if out_embed_file:
                await interaction.followup.send(file=out_embed_file, embed=out_embed)
            else:
                await interaction.followup.send(embed=out_embed)
        else:
            await interaction.followup.send("Not found!")

client.tree.add_command(MusicGroup(name="music"))

client.run(os.environ["TOKEN"])
