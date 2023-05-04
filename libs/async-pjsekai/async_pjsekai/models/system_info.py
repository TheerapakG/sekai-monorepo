# SPDX-FileCopyrightText: 2022-present Erik Chan <erikchan002@gmail.com>
# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field, fields
from typing import Optional, Union, Type, TypeVar

from async_pjsekai.enums.enums import AppVersionStatus
from async_pjsekai.enums.unknown import Unknown


T_SystemInfo = TypeVar("T_SystemInfo", bound="SystemInfo")


@dataclass(frozen=True, slots=True)
class SystemInfo:
    system_profile: Optional[str] = field(default=None)
    app_version: Optional[str] = field(default=None)
    multi_play_version: Optional[str] = field(default=None)
    data_version: Optional[str] = field(default=None)
    asset_version: Optional[str] = field(default=None)
    app_hash: Optional[str] = field(default=None)
    asset_hash: Optional[str] = field(default=None)
    app_version_status: Union[AppVersionStatus, Unknown, None] = field(default=None)

    @classmethod
    def create(cls: Type[T_SystemInfo]) -> T_SystemInfo:
        return cls(**{field.name: None for field in fields(cls)})
