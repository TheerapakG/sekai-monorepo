# SPDX-FileCopyrightText: 2022-2023 Erik Chan <erikchan002@gmail.com>
# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

from asyncio.locks import Lock
from contextlib import asynccontextmanager
from typing import Optional
from pathlib import Path

from async_pjsekai.api import API
from async_pjsekai.models.asset_bundle_info import AssetBundleInfo

from .models.converters import msgpack_converter


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

    _asset_bundle_info: Optional[AssetBundleInfo]
    _asset_bundle_info_lock: Lock

    @property
    @asynccontextmanager
    async def asset_bundle_info(self):
        async with self._asset_bundle_info_lock:
            yield self._asset_bundle_info

    @asset_bundle_info.setter
    def asset_bundle_info(self, new_value: Optional[AssetBundleInfo]) -> None:
        self._asset_bundle_info = new_value
        if self.path is not None and new_value is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.joinpath("AssetBundleInfo.msgpack").open("wb") as f:
                f.write(msgpack_converter.dumps(new_value, AssetBundleInfo))

    def __init__(
        self, version: str, hash: str, asset_directory: Optional[str] = None
    ) -> None:
        self._path = None
        if asset_directory is not None:
            p = Path(asset_directory)
            if p.exists() and not p.is_dir():
                raise NotADirectoryError
            self._path = p

        self._version = version
        self._hash = hash

        self._asset_bundle_info_lock = Lock()

        if self.path is not None:
            try:
                with self.path.joinpath("AssetBundleInfo.msgpack").open("rb") as f:
                    self._asset_bundle_info = msgpack_converter.loads(
                        f.read(), AssetBundleInfo
                    )
            except FileNotFoundError:
                self.asset_bundle_info = None
        else:
            self.asset_bundle_info = None

    async def get_asset_bundle_info(self, api_manager: API) -> AssetBundleInfo:
        async with self._asset_bundle_info_lock:
            del self._asset_bundle_info
            self.asset_bundle_info = msgpack_converter.loads(
                await api_manager.get_asset_bundle_info_packed(self._version),
                AssetBundleInfo,
            )
            return self._asset_bundle_info
