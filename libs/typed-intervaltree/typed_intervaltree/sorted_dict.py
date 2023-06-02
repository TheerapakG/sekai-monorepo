# SPDX-FileCopyrightText: 2014-2023 Grant Jenks
# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

import bisect
from collections.abc import Iterator, KeysView, MutableMapping, Sequence
from typing import SupportsIndex, TypeVar, overload

from .types import SupportsDunderComparisons

_T = TypeVar("_T")


class SortedDictKeysView(KeysView[_T], Sequence[_T]):
    def __init__(self, keys: list[_T]):
        self._keys = keys

    @overload
    def __getitem__(self, index: SupportsIndex) -> _T:
        ...

    @overload
    def __getitem__(self, index: slice) -> list[_T]:
        ...

    def __getitem__(self, index: SupportsIndex | slice):
        return self._keys[index]

    def __contains__(self, key: object) -> bool:
        return key in self._keys

    def __iter__(self) -> Iterator[_T]:
        return iter(self._keys)

    def __len__(self) -> int:
        return len(self._keys)


_K = TypeVar("_K", bound=SupportsDunderComparisons)
_V = TypeVar("_V")


class SortedDict(MutableMapping[_K, _V]):
    def __init__(self):
        self._dict = dict[_K, _V]()
        self._keys = list[_K]()

    def __getitem__(self, __key: _K) -> _V:
        return self._dict[__key]

    def __setitem__(self, __key: _K, __value: _V):
        self._dict[__key] = __value
        pos = bisect.bisect_left(self._keys, __key)
        if pos == len(self._keys) or self._keys[pos] != __key:
            self._keys.insert(pos, __key)

    def __delitem__(self, __key: _K) -> None:
        del self._dict[__key]
        self._keys.pop(bisect.bisect_left(self._keys, __key))

    def __iter__(self) -> Iterator[_K]:
        return iter(self._keys)

    def __len__(self) -> int:
        return len(self._keys)

    def keys(self) -> SortedDictKeysView[_K]:
        return SortedDictKeysView(self._keys)

    def bisect_left(self, value: _K) -> int:
        return bisect.bisect_left(self._keys, value)

    def bisect_rightt(self, value: _K) -> int:
        return bisect.bisect_right(self._keys, value)
