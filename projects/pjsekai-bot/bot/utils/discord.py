# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

from io import BufferedIOBase, IOBase
from os import PathLike
from pathlib import Path
from typing import Union, overload
import discord


@overload
def add_embed_thumbnail(
    embed: discord.Embed,
    fp: Union[str, PathLike[str]],
    fname: str | None = None,
) -> discord.File: ...


@overload
def add_embed_thumbnail(
    embed: discord.Embed,
    fp: Union[BufferedIOBase],
    fname: str,
) -> discord.File: ...


def add_embed_thumbnail(
    embed: discord.Embed,
    fp: Union[str, PathLike[str], BufferedIOBase],
    fname: str | None = None,
):
    if fname is None:
        if isinstance(fp, IOBase):
            raise ValueError("IOBase fp requires fname")
        fname = Path(fp).name

    file = discord.File(fp, filename=fname)
    embed.set_thumbnail(url=f"attachment://{fname}")
    return file


@overload
def add_embed_image(
    embed: discord.Embed,
    fp: Union[str, PathLike[str]],
    fname: str | None = None,
): ...


@overload
def add_embed_image(
    embed: discord.Embed,
    fp: Union[BufferedIOBase],
    fname: str,
): ...


def add_embed_image(
    embed: discord.Embed,
    fp: Union[str, PathLike[str], BufferedIOBase],
    fname: str | None = None,
):
    if fname is None:
        if isinstance(fp, IOBase):
            raise ValueError("IOBase fp requires fname")
        fname = Path(fp).name

    file = discord.File(fp, filename=fname)
    embed.set_image(url=f"attachment://{fname}")
    return file
