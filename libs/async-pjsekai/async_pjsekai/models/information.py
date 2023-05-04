# SPDX-FileCopyrightText: 2022-present Erik Chan <erikchan002@gmail.com>
# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Union

from async_pjsekai.enums.unknown import Unknown
from async_pjsekai.enums.information import (
    BrowseType,
    InformationPlatform,
    InformationTag,
    InformationType,
)


@dataclass(slots=True)
class Information:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    display_order: Optional[int] = field(default=None)
    information_type: Union[InformationType, Unknown, None] = field(default=None)
    information_tag: Union[InformationTag, Unknown, None] = field(default=None)
    browse_type: Union[BrowseType, Unknown, None] = field(default=None)
    platform: Union[InformationPlatform, Unknown, None] = field(default=None)
    title: Optional[str] = field(default=None)
    path: Optional[str] = field(default=None)
    start_at: Optional[datetime] = field(default=None)
    banner_asset_bundle_name: Optional[str] = field(default=None)
    end_at: Optional[datetime] = field(default=None)
