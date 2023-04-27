# SPDX-FileCopyrightText: 2022-2023 Erik Chan <erikchan002@gmail.com>
# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict

from pjsekai.enums import *


@dataclass(slots=True)
class Bundle:
    bundle_name: Optional[str] = field(default=None)
    cache_directory_name: Optional[str] = field(default=None)
    hash: Optional[str] = field(default=None)
    category: Union[BundleCategory, Unknown, None] = field(default=None)
    crc: Optional[int] = field(default=None)
    file_size: Optional[int] = field(default=None)
    dependencies: Optional[List[str]] = field(default=None)
    paths: Optional[List[str]] = field(default=None)
    is_builtin: Optional[bool] = field(default=None)


@dataclass(slots=True)
class AssetBundleInfo:
    version: Optional[str] = field(default=None)
    os: Union[AssetOS, Unknown, None] = field(default=None)
    bundles: Optional[Dict[str, Bundle]] = field(default=None)
