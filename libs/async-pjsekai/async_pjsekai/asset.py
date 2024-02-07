# SPDX-FileCopyrightText: 2022-2023 Erik Chan <erikchan002@gmail.com>
# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

import aiofiles
import aiofiles.os
from asyncio.locks import Lock
from contextlib import asynccontextmanager
from pathlib import Path
from types import TracebackType
from typing import AsyncIterator, Coroutine, Optional, Type

from async_pjsekai.api import API
from async_pjsekai.models.asset_bundle_info import AssetBundleInfo
from async_pjsekai.models.system_info import SystemInfo

from async_pjsekai.models.converters import msgpack_converter


class AssetBundleInfoMutex:
    _lock: Lock
    _sync: bool
    _asset_bundle_info: Optional[AssetBundleInfo]
    _asset_bundle_info_file_path: Optional[Path]

    def __init__(self, asset_bundle_info_file_path: Optional[Path]) -> None:
        self._lock = Lock()
        self._sync = False
        self._asset_bundle_info = None
        self._asset_bundle_info_file_path = asset_bundle_info_file_path

    @property
    def sync(self):
        return self._sync

    @property
    def asset_bundle_info(self):
        return self._asset_bundle_info

    @property
    def asset_bundle_info_file_path(self):
        return self._asset_bundle_info_file_path

    async def __aenter__(self):
        await self._lock.acquire()
        return self._asset_bundle_info, self._sync

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ):
        self._lock.release()

    async def _loads(self, data: bytes):
        await self._set_value(None, write=False)
        new_value = msgpack_converter.loads(data, AssetBundleInfo)
        await self._set_value(new_value)
        return new_value

    @asynccontextmanager
    async def loads(self, data: bytes):
        async with self._lock:
            yield await self._loads(data)

    async def _loads_coro(self, data: Coroutine[None, None, bytes]):
        await self._set_value(None, write=False)
        new_value = msgpack_converter.loads(await data, AssetBundleInfo)
        await self._set_value(new_value)
        return new_value

    @asynccontextmanager
    async def loads_coro(self, data: Coroutine[None, None, bytes]):
        async with self._lock:
            yield await self._loads_coro(data)

    async def load(self):
        async with self._lock:
            if self.asset_bundle_info_file_path is not None:
                try:
                    async with aiofiles.open(
                        self.asset_bundle_info_file_path, "rb"
                    ) as f:
                        await self._loads_coro(f.read())
                except FileNotFoundError:
                    await self._set_value(None)
            else:
                await self._set_value(None)

    async def _write(self):
        if (
            self._asset_bundle_info is not None
            and self.asset_bundle_info_file_path is not None
        ):
            await aiofiles.os.makedirs(
                self.asset_bundle_info_file_path.parent, exist_ok=True
            )
            temp_path = self.asset_bundle_info_file_path.with_suffix(
                self.asset_bundle_info_file_path.suffix + ".tmp"
            )
            async with aiofiles.open(temp_path, "wb") as f:
                await f.write(
                    msgpack_converter.dumps(self._asset_bundle_info, AssetBundleInfo)
                )
            await aiofiles.os.replace(temp_path, self.asset_bundle_info_file_path)
        self._sync = True

    async def _set_value(self, new_value: Optional[AssetBundleInfo], write=True):
        self._sync = False
        self._asset_bundle_info = new_value
        if write:
            await self._write()

    async def set_value(self, new_value: Optional[AssetBundleInfo]):
        async with self._lock:
            await self._set_value(new_value)


class Asset:
    _path: Optional[Path]

    @property
    def path(self) -> Optional[Path]:
        return self._path

    _version: str

    @property
    def version(self) -> str:
        return self._version

    _hash: str

    @property
    def hash(self) -> str:
        return self._hash

    _asset_bundle_info: AssetBundleInfoMutex

    @property
    @asynccontextmanager
    async def asset_bundle_info(self):
        async with self._asset_bundle_info as asset_bundle_info:
            yield asset_bundle_info

    async def set_asset_bundle_info(self, new_value: Optional[AssetBundleInfo]) -> None:
        await self._asset_bundle_info.set_value(new_value)

    def __init__(
        self, version: str, hash: str, asset_directory: Optional[Path] = None
    ) -> None:
        self._path = None
        if asset_directory is not None:
            self._path = asset_directory

        self._version = version
        self._hash = hash

        if p := self.path:
            self._asset_bundle_info = AssetBundleInfoMutex(
                p / "AssetBundleInfo.msgpack"
            )
        else:
            self._asset_bundle_info = AssetBundleInfoMutex(None)

    async def load(self):
        await self._asset_bundle_info.load()

    @asynccontextmanager
    async def get_asset_bundle_info(
        self, system_info: SystemInfo, api_manager: API
    ) -> AsyncIterator[AssetBundleInfo]:
        async with self._asset_bundle_info.loads_coro(
            api_manager.get_asset_bundle_info_packed(system_info, self._version)
        ) as asset_bundle_info:
            yield asset_bundle_info
