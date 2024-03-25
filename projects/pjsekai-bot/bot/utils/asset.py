# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

import asyncio
import logging
from pathlib import Path

import aiofiles
from async_pjsekai.client import Client
from async_pjsekai.enums.platform import Platform

import UnityPy
import UnityPy.config
import UnityPy.files
from UnityPy.tools.extractor import EXPORT_TYPES, export_obj

log = logging.getLogger(__name__)

UnityPy.config.FALLBACK_UNITY_VERSION = Platform.ANDROID.unity_version

export_types_keys = list(EXPORT_TYPES.keys())


def defaulted_export_index(type):
    try:
        return export_types_keys.index(type)
    except (IndexError, ValueError):
        return 999


async def extract_acb_bytes(path: Path):
    async with (
        aiofiles.open(path, "rb") as src,
        aiofiles.open(path.with_suffix(""), "wb") as dst,
    ):
        await aiofiles.os.sendfile(
            dst.fileno(), src.fileno(), 0, (await aiofiles.os.stat(path)).st_size
        )
    process = await asyncio.subprocess.create_subprocess_exec(
        "/usr/bin/vgmstream-cli",
        "-o",
        path.parent / "?n.wav",
        "-S",
        "0",
        path.with_suffix(""),
    )
    await process.wait()


async def convert_wav(vocal_path: Path, jacket_path: Path):
    process = await asyncio.subprocess.create_subprocess_exec(
        "/usr/bin/ffmpeg",
        "-y",
        "-loop",
        "1",
        "-r",
        "1",
        "-i",
        jacket_path,
        "-i",
        vocal_path,
        "-c:v",
        "libx264",
        "-profile:v",
        "baseline",
        "-level",
        "3.0",
        "-pix_fmt",
        "yuv420p",
        "-shortest",
        vocal_path.with_suffix(".mp4"),
    )
    await process.wait()
    return vocal_path.with_suffix(".mp4")


async def extract(directory: Path, path: str, obj: UnityPy.files.ObjectReader):
    log.info(f"extracting {path}")

    dst = directory / path
    await aiofiles.os.makedirs(dst.parent, exist_ok=True)

    export_obj(obj, dst)  # type: ignore

    match dst.suffixes:
        case [".acb", ".bytes"]:
            await extract_acb_bytes(dst)


async def load_asset(
    client: Client, asset_bundle_str: str, force: bool = False
) -> list[Path]:
    if (directory := client.asset_directory) and (asset := client.asset):
        async with asset.asset_bundle_info as (asset_bundle_info, sync):
            bundle_hash = None
            if asset_bundle_info and (bundles := asset_bundle_info.bundles):
                if asset_bundle_str in bundles:
                    bundle_hash = bundles[asset_bundle_str].hash

        if bundle_hash is None:
            bundle_hash = ""

        if force:
            log.info(f"downloading bundle {asset_bundle_str}")
        else:
            try:
                async with aiofiles.open(
                    directory / "hash" / asset_bundle_str, "r"
                ) as f:
                    if await f.read() == bundle_hash:
                        log.info(f"bundle {asset_bundle_str} already updated")
                        async with aiofiles.open(
                            directory / "path" / asset_bundle_str, "r"
                        ) as f:
                            return [
                                directory / p for p in (await f.read()).splitlines()
                            ]
                    else:
                        log.info(f"updating bundle {asset_bundle_str}")
            except FileNotFoundError:
                log.info(f"downloading bundle {asset_bundle_str}")

        paths: list[str] = []
        tasks: list[asyncio.Task] = []

        async with client.download_asset_bundle(asset_bundle_str) as asset_bundle:
            await aiofiles.os.makedirs(
                (directory / "bundle" / asset_bundle_str).parent, exist_ok=True
            )
            async with aiofiles.open(
                directory / "bundle" / f"{asset_bundle_str}.unity3d", "wb"
            ) as f:
                async for chunk in asset_bundle.chunks:
                    await f.write(chunk)

        env = UnityPy.load(str(directory / "bundle" / f"{asset_bundle_str}.unity3d"))
        container = sorted(
            env.container.items(),
            key=lambda x: defaulted_export_index(x[1].type),
        )

        await aiofiles.os.makedirs(
            (directory / "path" / asset_bundle_str).parent, exist_ok=True
        )
        async with aiofiles.open(directory / "path" / asset_bundle_str, "w") as f:
            for obj_path, obj in container:
                obj_path = "/".join(x for x in obj_path.split("/") if x)
                paths.append(obj_path)
                await f.write(obj_path + "\n")

                tasks.append(asyncio.create_task(extract(directory, obj_path, obj)))

        await asyncio.gather(*tasks)

        await aiofiles.os.makedirs(
            (directory / "hash" / asset_bundle_str).parent, exist_ok=True
        )
        async with aiofiles.open(directory / "hash" / asset_bundle_str, "w") as f:
            await f.write(bundle_hash)

        log.info(f"updated bundle {asset_bundle_str}")
        return [(directory / p) for p in paths]

    return []
