# SPDX-FileCopyrightText: 2013-2023 Chaim Leib Halbert
# SPDX-FileCopyrightText: 2014 Konstantin Tretyakov
# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Iterable, Sequence, Set
from dataclasses import dataclass, field
from operator import attrgetter
from typing import Any, Generic, Optional, TypeVar

from .interval import Interval
from .types import SupportsInterval

_T = TypeVar("_T")

_T_SupportsInterval = TypeVar("_T_SupportsInterval", bound=SupportsInterval)


@dataclass(slots=True)
class Node(Generic[_T_SupportsInterval, _T]):
    x_center: _T_SupportsInterval
    s_center: set[Interval[_T_SupportsInterval, _T]] = field(default_factory=set)
    left_node: Optional["Node[_T_SupportsInterval, _T]"] = field(default=None)
    right_node: Optional["Node[_T_SupportsInterval, _T]"] = field(default=None)
    depth: int = field(default=0)

    def __post_init__(self):
        self.rotate()

    @property
    def balance(self):
        left_depth = self.left_node.depth if self.left_node else 0
        right_depth = self.right_node.depth if self.right_node else 0
        return right_depth - left_depth

    @classmethod
    def from_interval(cls, interval: Interval[_T_SupportsInterval, _T]):
        return cls(x_center=interval.begin, s_center={interval})

    @classmethod
    def from_intervals(cls, intervals: Set[Interval[_T_SupportsInterval, _T]]):
        return cls.from_sorted_intervals(sorted(intervals))

    @classmethod
    def from_sorted_intervals(
        cls, intervals: Sequence[Interval[_T_SupportsInterval, _T]]
    ):
        if not intervals:
            return None
        center_iv = intervals[len(intervals) // 2]
        node = cls(x_center=center_iv.begin)
        s_left = []
        s_right = []
        for k in intervals:
            if k.end <= node.x_center:
                s_left.append(k)
            elif k.begin > node.x_center:
                s_right.append(k)
            else:
                node.s_center.add(k)
        node.left_node = cls.from_sorted_intervals(s_left)
        node.right_node = cls.from_sorted_intervals(s_right)
        return node.rotate()

    def center_hit(self, interval: Interval[_T_SupportsInterval, Any]):
        return interval.contains_point(self.x_center)

    def hit_branch(self, interval: Interval[_T_SupportsInterval, Any]):
        return interval.begin > self.x_center

    def refresh_depth(self):
        left_depth = self.left_node.depth if self.left_node else 0
        right_depth = self.right_node.depth if self.right_node else 0
        self.depth = 1 + max(left_depth, right_depth)

    def rotate(self):
        self.refresh_depth()
        balance = self.balance

        if abs(balance) < 2:
            return self

        my_heavy = balance > 0
        child = self.right_node if balance > 0 else self.left_node
        assert child
        child_heavy = child.balance > 0
        if my_heavy == child_heavy or child.balance == 0:
            return self.srotate()
        else:
            return self.drotate()

    def srotate(self):
        balance = self.balance

        if balance > 0:
            assert self.right_node
            save = self.right_node
            self.right_node = save.left_node
            node = self.rotate()
            save.left_node = node
        else:
            assert self.left_node
            save = self.left_node
            self.left_node = save.right_node
            node = self.rotate()
            save.right_node = node

        promotees = [iv for iv in node.s_center if save.center_hit(iv)]
        for iv in promotees:
            if balance > 0:
                save.left_node = node.remove(iv)
            else:
                save.right_node = node.remove(iv)
        save.s_center.update(promotees)
        save.refresh_depth()
        return save

    def drotate(self):
        if self.balance > 0:
            assert self.right_node
            self.right_node = self.right_node.srotate()
        else:
            assert self.left_node
            self.left_node = self.left_node.srotate()

        self.refresh_depth()
        return self.srotate()

    def add(self, interval: Interval[_T_SupportsInterval, _T]):
        if self.center_hit(interval):
            self.s_center.add(interval)
            return self
        else:
            if self.hit_branch(interval):
                self.right_node = (
                    self.right_node.add(interval)
                    if self.right_node
                    else Node.from_interval(interval)
                )
                return self.rotate()
            else:
                self.left_node = (
                    self.left_node.add(interval)
                    if self.left_node
                    else Node.from_interval(interval)
                )
                return self.rotate()

    def remove(self, interval: Interval[_T_SupportsInterval, _T]):
        return self.remove_interval_helper(interval, should_raise_error=True)[0]

    def discard(self, interval: Interval[_T_SupportsInterval, _T]):
        return self.remove_interval_helper(interval, should_raise_error=False)[0]

    def remove_interval_helper(
        self, interval: Interval[_T_SupportsInterval, _T], should_raise_error: bool
    ):
        if self.center_hit(interval):
            if not should_raise_error and interval not in self.s_center:
                return self, True
            try:
                self.s_center.remove(interval)
            except:
                raise KeyError(interval)
            if self.s_center:
                return self, True
            return self.prune(), False
        else:
            direction = self.hit_branch(interval)
            node = self.right_node if direction else self.left_node

            if not node:
                if should_raise_error:
                    raise ValueError
                return self, True

            node, done = node.remove_interval_helper(interval, should_raise_error)
            if direction:
                self.right_node = node
            else:
                self.left_node = node

            if not done:
                return self.rotate(), False
            return self, True

    def search_overlap(
        self, point_list: Iterable[_T_SupportsInterval]
    ) -> list[Interval[_T_SupportsInterval, _T]]:
        result = list[Interval[_T_SupportsInterval, _T]]()
        for j in point_list:
            result.extend(self.search_point(j))
        return result

    def search_point(
        self, point: _T_SupportsInterval
    ) -> list[Interval[_T_SupportsInterval, _T]]:
        result = list[Interval[_T_SupportsInterval, _T]]()
        for k in self.s_center:
            if k.begin <= point < k.end:
                result.append(k)
        if point < self.x_center and self.left_node:
            result.extend(self.left_node.search_point(point))
            return result
        if point > self.x_center and self.right_node:
            result.extend(self.right_node.search_point(point))
            return result
        return result

    def prune(self):
        if not self.left_node:
            return self.right_node
        elif not self.right_node:
            return self.left_node
        else:
            heir, self.left_node = self.left_node.pop_greatest_child()

            heir.left_node, heir.right_node = self.left_node, self.right_node
            heir.refresh_depth()
            heir = heir.rotate()
            return heir

    def pop_greatest_child(
        self,
    ) -> tuple[
        "Node[_T_SupportsInterval, _T]", Optional["Node[_T_SupportsInterval, _T]"]
    ]:
        if not self.right_node:
            ivs = sorted(self.s_center, key=attrgetter("end", "begin"))
            max_iv = ivs.pop()
            new_x_center = self.x_center
            for next_max_iv in reversed(ivs):
                if next_max_iv.end == max_iv.end:
                    continue
                new_x_center = max(new_x_center, next_max_iv.end)
                break

            child = Node(
                x_center=new_x_center,
                s_center=set(
                    iv for iv in self.s_center if iv.contains_point(new_x_center)
                ),
            )
            self.s_center -= child.s_center

            if self.s_center:
                return child, self
            else:
                return child, self.left_node

        else:
            greatest_child, self.right_node = self.right_node.pop_greatest_child()

            for iv in self.s_center.copy():
                if iv.contains_point(greatest_child.x_center):
                    self.s_center.remove(iv)
                    greatest_child.add(iv)

            if self.s_center:
                self.refresh_depth()
                new_self = self.rotate()
                return greatest_child, new_self
            else:
                new_self = self.prune()
                return greatest_child, new_self

    def contains_point(self, p: _T_SupportsInterval) -> bool:
        """
        Returns whether this node or a child overlaps p.
        """
        for iv in self.s_center:
            if iv.contains_point(p):
                return True
        branch = self.right_node if p > self.x_center else self.left_node
        return branch.contains_point(p) if branch else False

    def all_children(self) -> set["Interval[_T_SupportsInterval, _T]"]:
        result = self.s_center.copy()
        if self.left_node:
            result.update(self.left_node.all_children())
        if self.right_node:
            result.update(self.right_node.all_children())
        return result

    def __str__(self):
        return "Node<{0}, depth={1}, balance={2}>".format(
            self.x_center, self.depth, self.balance
        )

    def count_nodes(self):
        count = 1
        if self.left_node:
            count += self.left_node.count_nodes()
        if self.right_node:
            count += self.right_node.count_nodes()
        return count
