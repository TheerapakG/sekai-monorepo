# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
from typing import Optional


@dataclass
class GameCharacterData:
    ids: dict[str, int]
    first_name: Optional[str]
    given_name: Optional[str]
    given_name_ruby: Optional[str]
    first_name_ruby: Optional[str]

    def ids_str(self):
        return " ".join(f"{k}: {v}" for k, v in self.ids.items() if k and v)

    def name_str(self):
        return " ".join(
            n
            for n in [
                self.first_name,
                self.given_name,
            ]
            if n
        )

    def ruby_name_str(self):
        return " ".join(
            n
            for n in [
                self.first_name_ruby,
                self.given_name_ruby,
            ]
            if n
        )

    def name_long_str(self):
        return f"{self.name_str()} ({self.ruby_name_str()})"
