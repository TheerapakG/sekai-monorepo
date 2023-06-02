# SPDX-FileCopyrightText: 2013-2023 Chaim Leib Halbert
# SPDX-FileCopyrightText: 2014 Konstantin Tretyakov
# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

import builtins
from collections.abc import Iterable
from copy import copy
from typing import Any, Callable, Generic, Optional, TypeVar, overload

from .interval import Interval
from .node import Node
from .sorted_dict import SortedDict
from .types import SupportsInterval

_T = TypeVar("_T")

_T_SupportsInterval = TypeVar("_T_SupportsInterval", bound=SupportsInterval)


class IntervalTree(Generic[_T_SupportsInterval, _T]):
    @classmethod
    def from_tuples(
        cls, tups: Iterable[tuple[_T_SupportsInterval, _T_SupportsInterval, _T]]
    ):
        ivs = [Interval(*t) for t in tups]
        return cls(ivs)

    def __init__(
        self, intervals: Optional[Iterable[Interval[_T_SupportsInterval, _T]]] = None
    ):
        intervals = set(intervals) if intervals is not None else set()
        for iv in intervals:
            if iv.is_null():
                raise ValueError(
                    "IntervalTree: Null Interval objects not allowed in IntervalTree:"
                    " {0}".format(iv)
                )
        self.all_intervals = intervals
        self.top_node = Node.from_intervals(self.all_intervals)
        self.boundary_table = SortedDict[_T_SupportsInterval, int]()
        for iv in self.all_intervals:
            self._add_boundaries(iv)

    def copy(self):
        return IntervalTree(iv.copy() for iv in self)

    def _add_boundaries(self, interval: Interval[_T_SupportsInterval, _T]):
        begin = interval.begin
        end = interval.end
        if begin in self.boundary_table:
            self.boundary_table[begin] += 1
        else:
            self.boundary_table[begin] = 1

        if end in self.boundary_table:
            self.boundary_table[end] += 1
        else:
            self.boundary_table[end] = 1

    def _remove_boundaries(self, interval: Interval[_T_SupportsInterval, _T]):
        begin = interval.begin
        end = interval.end
        if self.boundary_table[begin] == 1:
            del self.boundary_table[begin]
        else:
            self.boundary_table[begin] -= 1

        if self.boundary_table[end] == 1:
            del self.boundary_table[end]
        else:
            self.boundary_table[end] -= 1

    def add(self, interval: Interval[_T_SupportsInterval, _T]):
        if interval in self:
            return

        if interval.is_null():
            raise ValueError(
                "IntervalTree: Null Interval objects not allowed in IntervalTree:"
                " {0}".format(interval)
            )

        if not self.top_node:
            self.top_node = Node.from_interval(interval)
        else:
            self.top_node = self.top_node.add(interval)
        self.all_intervals.add(interval)
        self._add_boundaries(interval)

    append = add

    def addi(self, begin: _T_SupportsInterval, end: _T_SupportsInterval, data: _T):
        return self.add(Interval(begin, end, data))

    appendi = addi

    def update(self, intervals: Iterable[Interval[_T_SupportsInterval, _T]]):
        for iv in intervals:
            self.add(iv)

    def remove(self, interval: Interval[_T_SupportsInterval, _T]):
        if not self.top_node or interval not in self:
            raise ValueError
        self.top_node = self.top_node.remove(interval)
        self.all_intervals.remove(interval)
        self._remove_boundaries(interval)

    def removei(self, begin: _T_SupportsInterval, end: _T_SupportsInterval, data: _T):
        return self.remove(Interval(begin, end, data))

    def discard(self, interval: Interval[_T_SupportsInterval, _T]):
        if not self.top_node or interval not in self:
            return
        self.all_intervals.discard(interval)
        self.top_node = self.top_node.discard(interval)
        self._remove_boundaries(interval)

    def discardi(self, begin: _T_SupportsInterval, end: _T_SupportsInterval, data: _T):
        return self.discard(Interval(begin, end, data))

    def difference(self, other: "Iterable[Interval[_T_SupportsInterval, _T]]"):
        other = set(other)
        ivs = set()
        for iv in self:
            if iv not in other:
                ivs.add(iv)
        return IntervalTree(ivs)

    def difference_update(self, other: "Iterable[Interval[_T_SupportsInterval, _T]]"):
        for iv in other:
            self.discard(iv)

    def union(self, other: "Iterable[Interval[_T_SupportsInterval, _T]]"):
        return IntervalTree(set(self).union(other))

    def intersection(self, other: "Iterable[Interval[_T_SupportsInterval, _T]]"):
        other = set(other)
        ivs = set()
        shorter, longer = sorted([self, other], key=len)
        for iv in shorter:
            if iv in longer:
                ivs.add(iv)
        return IntervalTree(ivs)

    def intersection_update(self, other: "Iterable[Interval[_T_SupportsInterval, _T]]"):
        other = set(other)
        ivs = list(self)
        for iv in ivs:
            if iv not in other:
                self.remove(iv)

    def symmetric_difference(
        self, other: "Iterable[Interval[_T_SupportsInterval, _T]]"
    ):
        other = set(other)
        me = set(self)
        ivs = me.difference(other).union(other.difference(me))
        return IntervalTree(ivs)

    def symmetric_difference_update(
        self, other: "Iterable[Interval[_T_SupportsInterval, _T]]"
    ):
        other = set(other)
        ivs = list(self)
        for iv in ivs:
            if iv in other:
                self.remove(iv)
                other.remove(iv)
        self.update(other)

    def remove_overlap(
        self, begin: _T_SupportsInterval, end: Optional[_T_SupportsInterval] = None
    ):
        hitlist = self.at(begin) if end is None else self.overlap(begin, end)
        for iv in hitlist:
            self.remove(iv)

    def remove_envelop(self, begin: _T_SupportsInterval, end: _T_SupportsInterval):
        hitlist = self.envelop(begin, end)
        for iv in hitlist:
            self.remove(iv)

    def chop(
        self,
        begin: _T_SupportsInterval,
        end: _T_SupportsInterval,
        datafunc: Optional[
            Callable[
                [Interval[_T_SupportsInterval, _T], bool],
                Interval[_T_SupportsInterval, _T],
            ]
        ] = None,
    ):
        insertions = set()
        begin_hits = [iv for iv in self.at(begin) if iv.begin < begin]
        end_hits = [iv for iv in self.at(end) if iv.end > end]

        if datafunc:
            for iv in begin_hits:
                insertions.add(Interval(iv.begin, begin, datafunc(iv, True)))
            for iv in end_hits:
                insertions.add(Interval(end, iv.end, datafunc(iv, False)))
        else:
            for iv in begin_hits:
                insertions.add(Interval(iv.begin, begin, iv.data))
            for iv in end_hits:
                insertions.add(Interval(end, iv.end, iv.data))

        self.remove_envelop(begin, end)
        self.difference_update(begin_hits)
        self.difference_update(end_hits)
        self.update(insertions)

    def slice(
        self,
        point: _T_SupportsInterval,
        datafunc: Optional[
            Callable[
                [Interval[_T_SupportsInterval, _T], bool],
                Interval[_T_SupportsInterval, _T],
            ]
        ] = None,
    ):
        hitlist = set(iv for iv in self.at(point) if iv.begin < point)
        insertions = set()
        if datafunc:
            for iv in hitlist:
                insertions.add(Interval(iv.begin, point, datafunc(iv, True)))
                insertions.add(Interval(point, iv.end, datafunc(iv, False)))
        else:
            for iv in hitlist:
                insertions.add(Interval(iv.begin, point, iv.data))
                insertions.add(Interval(point, iv.end, iv.data))
        self.difference_update(hitlist)
        self.update(insertions)

    def clear(self):
        self.__init__()

    def find_nested(self):
        result = dict[
            Interval[_T_SupportsInterval, _T], set[Interval[_T_SupportsInterval, _T]]
        ]()

        long_ivs = sorted(
            self.all_intervals,
            key=Interval[_T_SupportsInterval, _T].length,
            reverse=True,
        )
        for i, parent in enumerate(long_ivs):
            for child in long_ivs[i + 1 :]:
                if parent.contains_interval(child):
                    if parent not in result:
                        result[parent] = set()
                    result[parent].add(child)
        return result

    @overload
    def overlaps(self, begin: Interval[_T_SupportsInterval, Any]) -> bool:
        ...

    @overload
    def overlaps(
        self, begin: _T_SupportsInterval, end: Optional[_T_SupportsInterval] = None
    ) -> bool:
        ...

    def overlaps(
        self,
        begin: Interval[_T_SupportsInterval, Any] | _T_SupportsInterval,
        end: Optional[_T_SupportsInterval] = None,
    ) -> bool:
        if end is not None:
            assert not isinstance(begin, Interval)
            return self.overlaps_range(begin, end)
        elif isinstance(begin, Interval):
            return self.overlaps_range(begin.begin, begin.end)
        else:
            return self.overlaps_point(begin)

    def overlaps_point(self, p: _T_SupportsInterval) -> bool:
        if not self.top_node:
            return False
        return self.top_node.contains_point(p)

    def overlaps_range(self, begin: _T_SupportsInterval, end: _T_SupportsInterval):
        if self.is_empty():
            return False
        elif begin >= end:
            return False
        elif self.overlaps_point(begin):
            return True
        return any(
            self.overlaps_point(bound)
            for bound in self.boundary_table
            if begin < bound < end
        )

    def split_overlaps(self):
        if not self:
            return
        if len(self.boundary_table) == 2:
            return

        bounds = sorted(self.boundary_table)

        new_ivs = set()
        for lbound, ubound in zip(bounds[:-1], bounds[1:]):
            for iv in self[lbound]:
                new_ivs.add(Interval(lbound, ubound, iv.data))

        self.__init__(new_ivs)

    @overload
    def merge_overlaps(
        self, data_reducer: Callable[[Optional[_T], _T], _T], *, strict: bool = True
    ):
        ...

    @overload
    def merge_overlaps(
        self,
        data_reducer: Callable[[_T, _T], _T],
        data_initializer: _T,
        *,
        strict: bool = True
    ):
        ...

    def merge_overlaps(
        self,
        data_reducer: Callable[[Any, _T], _T],
        data_initializer: Optional[_T] = None,
        *,
        strict: bool = True
    ):
        if not self:
            return

        sorted_intervals = sorted(self.all_intervals)
        merged = list[Interval[_T_SupportsInterval, _T]]()
        current_reduced: Optional[_T] = None

        def new_series(
            current_reduced: Optional[_T], higher: Interval[_T_SupportsInterval, _T]
        ):
            if data_initializer is None:
                current_reduced = higher.data
                merged.append(higher)
            else:  # data_initializer is not None
                current_reduced = copy(data_initializer)
                current_reduced = data_reducer(current_reduced, higher.data)
                merged.append(Interval(higher.begin, higher.end, current_reduced))
            return current_reduced

        for higher in sorted_intervals:
            if merged:  # series already begun
                lower = merged[-1]
                if (
                    higher.begin < lower.end or not strict and higher.begin == lower.end
                ):  # should merge
                    upper_bound = max(lower.end, higher.end)
                    current_reduced = data_reducer(current_reduced, higher.data)
                    merged[-1] = Interval(lower.begin, upper_bound, current_reduced)
                else:
                    current_reduced = new_series(current_reduced, higher)
            else:  # not merged; is first of Intervals to merge
                new_series(current_reduced, higher)

        self.__init__(merged)

    @overload
    def merge_equals(self, data_reducer: Callable[[Optional[_T], _T], _T]):
        ...

    @overload
    def merge_equals(self, data_reducer: Callable[[_T, _T], _T], data_initializer: _T):
        ...

    def merge_equals(
        self,
        data_reducer: Callable[[Any, _T], _T],
        data_initializer: Optional[_T] = None,
    ):
        if not self:
            return

        sorted_intervals = sorted(self.all_intervals)
        merged = list[Interval[_T_SupportsInterval, _T]]()
        current_reduced: Optional[_T] = None

        def new_series(
            current_reduced: Optional[_T], higher: Interval[_T_SupportsInterval, _T]
        ):
            if data_initializer is None:
                current_reduced = higher.data
                merged.append(higher)
            else:  # data_initializer is not None
                current_reduced = copy(data_initializer)
                current_reduced = data_reducer(current_reduced, higher.data)
                merged.append(Interval(higher.begin, higher.end, current_reduced))
            return current_reduced

        for higher in sorted_intervals:
            if merged:  # series already begun
                lower = merged[-1]
                if higher.range_matches(lower):  # should merge
                    upper_bound = max(lower.end, higher.end)
                    current_reduced = data_reducer(current_reduced, higher.data)
                    merged[-1] = Interval(lower.begin, upper_bound, current_reduced)
                else:
                    current_reduced = new_series(current_reduced, higher)
            else:  # not merged; is first of Intervals to merge
                current_reduced = new_series(current_reduced, higher)

        self.__init__(merged)

    def items(self) -> set[Interval[_T_SupportsInterval, _T]]:
        return self.all_intervals.copy()

    def is_empty(self):
        return 0 == len(self)

    def at(self, p: _T_SupportsInterval) -> list[Interval[_T_SupportsInterval, _T]]:
        root = self.top_node
        if not root:
            return []
        return root.search_point(p)

    @overload
    def envelop(
        self, begin: Interval[_T_SupportsInterval, Any]
    ) -> set[Interval[_T_SupportsInterval, _T]]:
        ...

    @overload
    def envelop(
        self, begin: _T_SupportsInterval, end: _T_SupportsInterval
    ) -> set[Interval[_T_SupportsInterval, _T]]:
        ...

    def envelop(
        self,
        begin: Interval[_T_SupportsInterval, Any] | _T_SupportsInterval,
        end: Optional[_T_SupportsInterval] = None,
    ) -> set[Interval[_T_SupportsInterval, _T]]:
        root = self.top_node
        if not root:
            return set()

        if end is None:
            assert isinstance(begin, Interval)
            return self.envelop(begin.begin, begin.end)
        else:
            assert not isinstance(begin, Interval)

        if begin >= end:
            return set()

        result = set(root.search_point(begin))  # bound_begin might be greater
        boundary_table = self.boundary_table
        bound_begin = boundary_table.bisect_left(begin)
        bound_end = boundary_table.bisect_left(end)  # up to, but not including end
        result.update(root.search_overlap(boundary_table.keys()[bound_begin:bound_end]))

        return {iv for iv in result if iv.begin >= begin and iv.end <= end}

    @overload
    def overlap(
        self, begin: Interval[_T_SupportsInterval, Any]
    ) -> set[Interval[_T_SupportsInterval, _T]]:
        ...

    @overload
    def overlap(
        self, begin: _T_SupportsInterval, end: _T_SupportsInterval
    ) -> set[Interval[_T_SupportsInterval, _T]]:
        ...

    def overlap(
        self,
        begin: Interval[_T_SupportsInterval, Any] | _T_SupportsInterval,
        end: Optional[_T_SupportsInterval] = None,
    ) -> set[Interval[_T_SupportsInterval, _T]]:
        root = self.top_node
        if not root:
            return set()

        if end is None:
            assert isinstance(begin, Interval)
            return self.overlap(begin.begin, begin.end)
        else:
            assert not isinstance(begin, Interval)

        if begin >= end:
            return set()

        result = set(root.search_point(begin))  # bound_begin might be greater
        boundary_table = self.boundary_table
        bound_begin = boundary_table.bisect_left(begin)
        bound_end = boundary_table.bisect_left(end)  # up to, but not including end
        result.update(root.search_overlap(boundary_table.keys()[bound_begin:bound_end]))

        return result

    def begin(self):
        if not self.boundary_table:
            return None
        return self.boundary_table.keys()[0]

    def end(self):
        if not self.boundary_table:
            return None
        return self.boundary_table.keys()[-1]

    def range(self):
        begin = self.begin()
        end = self.end()
        if begin is None or end is None:
            return None
        return Interval(begin, end, None)

    def span(self):
        begin = self.begin()
        end = self.end()
        if begin is None or end is None:
            return None
        return end - begin

    def __getitem__(self, index: builtins.slice | _T_SupportsInterval):
        if isinstance(index, slice):
            start, stop = index.start, index.stop
            if start is None:
                start = self.begin()
                if stop is None:
                    return set(self)
            if stop is None:
                stop = self.end()

            if start is None or stop is None:
                return set()

            return set(self.overlap(start, stop))  # type: ignore
        else:
            return set(self.at(index))

    def __setitem__(self, index: builtins.slice, value: _T):
        self.addi(index.start, index.stop, value)

    def __delitem__(self, point: _T_SupportsInterval):
        self.remove_overlap(point)

    def __contains__(self, item: object):
        return item in self.all_intervals

    def containsi(self, begin: _T_SupportsInterval, end: _T_SupportsInterval, data: _T):
        return Interval(begin, end, data) in self

    def __iter__(self):
        return iter(self.all_intervals)

    iter = __iter__

    def __len__(self):
        return len(self.all_intervals)

    def __eq__(self, other):
        return (
            isinstance(other, IntervalTree)
            and self.all_intervals == other.all_intervals
        )

    def __repr__(self):
        ivs = sorted(self)
        if not ivs:
            return "IntervalTree()"
        else:
            return "IntervalTree({0})".format(ivs)

    __str__ = __repr__

    def __reduce__(self):
        return IntervalTree, (sorted(self.all_intervals),)
