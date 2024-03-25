# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

from collections.abc import Awaitable, Callable
from functools import partial
import inspect
from io import BufferedIOBase, IOBase
from os import PathLike
from pathlib import Path
from typing import Union, overload
import discord
from discord.ext.commands import Context

from ..bot.client import BotClient


def _apply_embed_thumbnail(
    fp: Union[str, PathLike[str], BufferedIOBase],
    fname: str | None,
    embed: discord.Embed,
):
    if fname is None:
        if isinstance(fp, IOBase):
            raise ValueError("IOBase fp requires fname")
        fname = Path(fp).name

    file = discord.File(fp, filename=fname)
    embed.set_thumbnail(url=f"attachment://{fname}")
    return file


@overload
def apply_embed_thumbnail(
    fp: Union[str, PathLike[str]],
    fname: str | None = None,
) -> Callable[[discord.Embed], discord.File]: ...


@overload
def apply_embed_thumbnail(
    fp: Union[BufferedIOBase],
    fname: str,
) -> Callable[[discord.Embed], discord.File]: ...


def apply_embed_thumbnail(
    fp: Union[str, PathLike[str], BufferedIOBase], fname: str | None = None
):
    return partial(_apply_embed_thumbnail, fp, fname)


def _apply_embed_image(
    fp: Union[str, PathLike[str], BufferedIOBase],
    fname: str | None,
    embed: discord.Embed,
):
    if fname is None:
        if isinstance(fp, IOBase):
            raise ValueError("IOBase fp requires fname")
        fname = Path(fp).name

    file = discord.File(fp, filename=fname)
    embed.set_image(url=f"attachment://{fname}")
    return file


@overload
def apply_embed_image(
    fp: Union[str, PathLike[str]],
    fname: str | None = None,
) -> Callable[[discord.Embed], discord.File]: ...


@overload
def apply_embed_image(
    fp: Union[BufferedIOBase],
    fname: str,
) -> Callable[[discord.Embed], discord.File]: ...


def apply_embed_image(
    fp: Union[str, PathLike[str], BufferedIOBase], fname: str | None = None
):
    return partial(_apply_embed_image, fp, fname)


async def populate_embed_and_send(
    ctx: Context[BotClient],
    embed: discord.Embed,
    *args: Callable[
        [discord.Embed],
        discord.File
        | list[discord.File]
        | None
        | Awaitable[discord.File | list[discord.File] | None],
    ]
    | None,
):
    files_nested = [
        maybe_fs if isinstance(maybe_fs, list) else [maybe_fs]
        for c in args
        if c and (maybe_fs := (await aw if inspect.isawaitable(aw := c(embed)) else aw))
    ]
    files = [f for fs in files_nested for f in fs]
    await ctx.send(embed=embed, files=files if files else None)
