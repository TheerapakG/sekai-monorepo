# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Protocol


class SupportsDunderComparisons(Protocol):
    def __lt__(self, __other) -> bool:
        ...

    def __le__(self, __other) -> bool:
        ...

    def __eq__(self, __other) -> bool:
        ...


class SupportsDunderSub(Protocol):
    def __sub__(self, __other) -> Any:
        ...


class SupportsInterval(SupportsDunderComparisons, SupportsDunderSub, Protocol):
    ...
