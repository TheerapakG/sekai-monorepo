# SPDX-FileCopyrightText: 2022-2023 Erik Chan <erikchan002@gmail.com>
# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field
from typing import Optional, Union

from async_pjsekai.enums.enums import BundleCategory
from async_pjsekai.enums.platform import AssetOS
from async_pjsekai.enums.unknown import Unknown


@dataclass(slots=True)
class Bundle:
    bundle_name: Optional[str] = field(default=None)
    cache_directory_name: Optional[str] = field(default=None)
    hash: Optional[str] = field(default=None)
    category: Union[BundleCategory, Unknown, None] = field(default=None)
    crc: Optional[int] = field(default=None)
    file_size: Optional[int] = field(default=None)
    dependencies: Optional[list[str]] = field(default=None)
    paths: Optional[list[str]] = field(default=None)
    is_builtin: Optional[bool] = field(default=None)


@dataclass(slots=True)
class AssetBundleInfo:
    version: Optional[str] = field(default=None)
    os: Union[AssetOS, Unknown, None] = field(default=None)
    bundles: Optional[dict[str, Bundle]] = field(default=None)
