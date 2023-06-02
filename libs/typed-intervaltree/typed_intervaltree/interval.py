# SPDX-FileCopyrightText: 2013-2023 Chaim Leib Halbert
# SPDX-FileCopyrightText: 2014 Konstantin Tretyakov
# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass, astuple, replace
from typing import Any, Generic, Optional, TypeVar, overload

from .types import SupportsInterval

_T = TypeVar("_T")

_T_SupportsInterval = TypeVar("_T_SupportsInterval", bound=SupportsInterval)


@dataclass(slots=True, order=True)
class Interval(Generic[_T_SupportsInterval, _T]):
    begin: _T_SupportsInterval
    end: _T_SupportsInterval
    data: _T

    @overload
    def overlaps(self, begin: "Interval[_T_SupportsInterval, Any]") -> bool:
        ...

    @overload
    def overlaps(
        self, begin: _T_SupportsInterval, end: Optional[_T_SupportsInterval] = None
    ) -> bool:
        ...

    def overlaps(
        self,
        begin: "Interval[_T_SupportsInterval, Any] | _T_SupportsInterval",
        end: Optional[_T_SupportsInterval] = None,
    ):
        if end is not None:
            assert not isinstance(begin, Interval)
            return begin < self.end and end > self.begin
        if isinstance(begin, Interval):
            return self.overlaps(begin.begin, begin.end)
        return self.contains_point(begin)

    @overload
    def overlap_size(
        self, begin: "Interval[_T_SupportsInterval, Any]"
    ) -> Optional["Interval[_T_SupportsInterval, None]"]:
        ...

    @overload
    def overlap_size(
        self, begin: _T_SupportsInterval, end: _T_SupportsInterval
    ) -> Optional["Interval[_T_SupportsInterval, None]"]:
        ...

    def overlap_size(self, begin, end=None):
        overlaps = self.overlaps(begin, end)
        if not overlaps:
            return None

        if end is not None:
            return Interval(max(self.begin, begin), min(self.end, end), None)
        return Interval(max(self.begin, begin.begin), min(self.end, begin.end), None)

    def contains_point(self, p: _T_SupportsInterval) -> bool:
        return self.begin <= p < self.end

    def range_matches(self, other: "Interval[_T_SupportsInterval, Any]") -> bool:
        return self.begin == other.begin and self.end == other.end

    def contains_interval(self, other: "Interval[_T_SupportsInterval, Any]") -> bool:
        return self.begin <= other.begin and self.end >= other.end

    def distance_to(
        self, other: "Interval[_T_SupportsInterval, Any] | _T_SupportsInterval"
    ) -> Optional["Interval[_T_SupportsInterval, None]"]:
        if self.overlaps(other):
            return None

        if isinstance(other, Interval):
            if self.begin < other.begin:
                return Interval(self.end, other.begin, None)
            return Interval(other.end, self.begin, None)

        if self.overlaps(other):
            if self.end <= other:
                return Interval(self.end, other, None)
            else:
                return Interval(other, self.begin, None)

    def is_null(self) -> bool:
        return self.begin >= self.end

    def length(self):
        return abs(self.end - self.begin)

    def __hash__(self):
        return hash((self.begin, self.end))

    def _raise_if_null(
        self,
        other: Optional["Interval[_T_SupportsInterval, Any]" | _T_SupportsInterval],
    ):
        if self.is_null():
            raise ValueError("Cannot compare null Intervals!")
        if isinstance(other, Interval) and other.is_null():
            raise ValueError("Cannot compare null Intervals!")

    def lt(self, other: "Interval[_T_SupportsInterval, Any]" | _T_SupportsInterval):
        self._raise_if_null(other)
        if isinstance(other, Interval):
            return self.end <= other.begin
        return self.end <= other

    def le(self, other: "Interval[_T_SupportsInterval, Any]" | _T_SupportsInterval):
        self._raise_if_null(other)
        if isinstance(other, Interval):
            return self.end <= other.end
        return self.end <= other

    def gt(self, other: "Interval[_T_SupportsInterval, Any]" | _T_SupportsInterval):
        """
        Strictly greater than. Returns True if no part of this Interval
        extends lower than or into other.
        :raises ValueError: if either self or other is a null Interval
        :param other: Interval or point
        :return: True or False
        :rtype: bool
        """
        self._raise_if_null(other)
        if isinstance(other, Interval):
            return self.begin >= other.end
        else:
            return self.begin > other

    def ge(self, other: "Interval[_T_SupportsInterval, Any]" | _T_SupportsInterval):
        """
        Greater than or overlaps. Returns True if no part of this Interval
        extends lower than other.
        :raises ValueError: if either self or other is a null Interval
        :param other: Interval or point
        :return: True or False
        :rtype: bool
        """
        self._raise_if_null(other)
        if isinstance(other, Interval):
            return self.begin >= other.begin
        return self.begin >= other

    def _get_fields(self) -> tuple[_T_SupportsInterval, _T_SupportsInterval, _T]:
        return astuple(self)

    def copy(self) -> "Interval[_T_SupportsInterval, _T]":
        return replace(self)

    def __reduce__(self):
        return Interval, self._get_fields()
