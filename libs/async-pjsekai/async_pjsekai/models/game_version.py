# SPDX-FileCopyrightText: 2022-2023 Erik Chan <erikchan002@gmail.com>
# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field, fields
from typing import Optional, Type, TypeVar

T_GameVersion = TypeVar("T_GameVersion", bound="GameVersion")


@dataclass(slots=True)
class GameVersion:
    profile: Optional[str] = field(default=None)
    asset_bundle_host_hash: Optional[str] = field(default=None)
    domain: Optional[str] = field(default=None)

    @classmethod
    def create(cls: Type[T_GameVersion]) -> T_GameVersion:
        return cls(**{field.name: None for field in fields(cls)})
