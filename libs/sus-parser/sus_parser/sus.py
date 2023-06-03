# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

from collections import defaultdict
from dataclasses import dataclass, field, replace
from datetime import timedelta
from fractions import Fraction
from functools import cache
from io import TextIOWrapper
from pathlib import Path
import re
import shlex
from typing import Optional


@dataclass(slots=True, order=True, frozen=True, unsafe_hash=True)
class PlayLevel:
    level: int
    plus: bool


@dataclass(slots=True, order=True, frozen=True, unsafe_hash=True)
class Request:
    ticks_per_beat: Optional[int] = field(default=None)
    enable_priority: Optional[bool] = field(default=None)


@dataclass(slots=True, order=True, frozen=True, unsafe_hash=True)
class Time:
    measure: int
    tick: int

    def __repr__(self):
        return f"{self.__class__.__name__}({self.measure}'{self.tick})"


@dataclass(slots=True, order=True, frozen=True, unsafe_hash=True)
class TimeFraction:
    measure: int
    fraction: Fraction

    def __repr__(self):
        return f"{self.__class__.__name__}({self.measure}:{self.fraction})"


@dataclass(slots=True, order=True, frozen=True, unsafe_hash=True)
class Speed:
    time: Time
    speed: float


@dataclass(slots=True, order=True, frozen=True, unsafe_hash=True)
class Barlength:
    measure: int
    length: int


@dataclass(slots=True, order=True, frozen=True, unsafe_hash=True)
class BPM:
    time: TimeFraction
    bpm: float


@dataclass(slots=True, order=True, frozen=True, unsafe_hash=True)
class Lane:
    start: int
    length: int

    @property
    def end(self):
        return self.start + self.length

    def __repr__(self):
        return f"{self.__class__.__name__}({self.start}, {self.end})"


@dataclass(slots=True, order=True, frozen=True, unsafe_hash=True)
class LaneInfo:
    time: TimeFraction
    lane: Lane


class AnySpeedDefinition:
    @cache
    def __new__(cls):
        return super().__new__(cls)


@dataclass(slots=True, order=True, frozen=True, unsafe_hash=True)
class NoteInfo:
    lane_info: LaneInfo
    note_type: int
    speed_definition: Optional[str | AnySpeedDefinition]


@dataclass(slots=True, order=True, frozen=True, unsafe_hash=True)
class ModifierInfo:
    lane_info: LaneInfo
    modifier_type: int
    speed_definition: Optional[str | AnySpeedDefinition]


@dataclass(slots=True, order=True, frozen=True, unsafe_hash=True)
class HoldInfo:
    lane_info: LaneInfo
    hold_type: int
    speed_definition: Optional[str | AnySpeedDefinition]


@dataclass(slots=True, order=True, frozen=True, unsafe_hash=True)
class Note:
    lane_info: LaneInfo
    note_type: Optional[int]
    modifier_type: Optional[int]
    speed_definition: Optional[str | AnySpeedDefinition]


@dataclass(slots=True, order=True, frozen=True)
class HoldPath(Note):
    hold_type: int


@dataclass(slots=True, order=True)
class HoldChannel:
    path: list[HoldPath]


@dataclass(slots=True)
class SUS:
    title: Optional[str] = field(default=None)
    subtitle: Optional[str] = field(default=None)
    artist: Optional[str] = field(default=None)
    genre: Optional[str] = field(default=None)
    designer: Optional[str] = field(default=None)
    difficulty: Optional[int] = field(default=None)
    play_level: Optional[PlayLevel] = field(default=None)
    song_id: Optional[str] = field(default=None)
    wave: Optional[Path] = field(default=None)
    wave_offset: Optional[timedelta] = field(default=None)
    jacket: Optional[Path] = field(default=None)
    background: Optional[Path] = field(default=None)
    movie: Optional[Path] = field(default=None)
    movie_offset: Optional[timedelta] = field(default=None)
    base_bpm: Optional[float] = field(default=None)
    request: Request = field(default_factory=Request)
    speeds: defaultdict[str, list[Speed]] = field(
        default_factory=lambda: defaultdict(list)
    )
    barlengths: list[Barlength] = field(default_factory=list)
    bpms: list[BPM] = field(default_factory=list)
    tap_notes: list[Note] = field(default_factory=list)
    hold_channels: list[HoldChannel] = field(default_factory=list)

    @classmethod
    def read(cls, f: TextIOWrapper):
        self = cls()

        measure_base: int = 0
        current_speed_def: Optional[str] = None
        bpm_dict: dict[str, float] = {}
        note_info_dict: dict[LaneInfo, NoteInfo] = {}
        modifier_info_dict: dict[LaneInfo, ModifierInfo] = {}
        hold_info_dict: defaultdict[str, dict[LaneInfo, HoldInfo]] = defaultdict(dict)

        for line in f:
            if not line.startswith("#"):
                continue

            sh_line = shlex.split(line[1:].replace(":", " ", 1).lower())
            header = sh_line[0]
            data = sh_line[1] if len(sh_line) > 1 else ""
            header = header.rstrip(":")

            match header:
                case "title":
                    self.title = data
                    continue
                case "subtitle":
                    self.subtitle = data
                    continue
                case "artist":
                    self.artist = data
                    continue
                case "genre":
                    self.genre = data
                    continue
                case "designer":
                    self.designer = data
                    continue
                case "difficulty":
                    self.difficulty = int(data)
                    continue
                case "playlevel":
                    if data:
                        self.play_level = (
                            PlayLevel(level=int(data[:-1]), plus=True)
                            if data[-1] == "+"
                            else PlayLevel(level=int(data), plus=False)
                        )
                    continue
                case "songid":
                    self.song_id = data
                    continue
                case "wave":
                    self.wave = Path(data)
                    continue
                case "waveoffset":
                    self.wave_offset = timedelta(seconds=float(data))
                    continue
                case "jacket":
                    self.jacket = Path(data)
                    continue
                case "backgrond":
                    self.background = Path(data)
                    continue
                case "movie":
                    self.movie = Path(data)
                    continue
                case "movieoffset":
                    self.movie_offset = timedelta(seconds=float(data))
                    continue
                case "basebpm":
                    self.base_bpm = float(data)
                    continue
                case "request":
                    data = data.split()
                    match data[0]:
                        case "ticks_per_beat":
                            self.request = replace(
                                self.request, ticks_per_beat=int(data[1])
                            )
                        case "enable_priority":
                            match data[1]:
                                case "true":
                                    self.request = replace(
                                        self.request, enable_priority=True
                                    )
                                case "false":
                                    self.request = replace(
                                        self.request, enable_priority=False
                                    )
                    continue
                case "measurebs":
                    measure_base = int(data)
                    continue
                case "measurehs":
                    current_speed_def = data
                    continue
                case "hispeed":
                    current_speed_def = data
                    continue
                case "nospeed":
                    current_speed_def = None
                    continue

            match header[:3]:
                case "bpm":
                    bpm_dict[header[3:]] = float(data)
                    continue
                case "til":
                    for match in re.finditer(r"(\d+)'(\d+):(\d*)(?:\.(\d*))?", data):
                        match = match.groups("0")
                        self.speeds[header[3:]].append(
                            Speed(
                                time=Time(
                                    measure=measure_base + int(match[0]),
                                    tick=int(match[1]),
                                ),
                                speed=float(f"{match[2]}.{match[3]}"),
                            )
                        )
                    continue

            match len(header):
                case 5:
                    match header[-2]:
                        case "0":
                            match header[-1]:
                                case "2":
                                    self.barlengths.append(
                                        Barlength(
                                            measure=measure_base + int(header[:-2]),
                                            length=int(data),
                                        )
                                    )
                                    continue
                                case "8":
                                    length = len(data) // 2
                                    for i, data_unit in enumerate(
                                        "".join(t) for t in zip(data[::2], data[1::2])
                                    ):
                                        if data_unit == "00":
                                            continue
                                        self.bpms.append(
                                            BPM(
                                                time=TimeFraction(
                                                    measure=measure_base
                                                    + int(header[:-2]),
                                                    fraction=Fraction(i, length),
                                                ),
                                                bpm=bpm_dict[data_unit],
                                            )
                                        )
                                    continue
                        case "1":
                            length = len(data) // 2
                            lane = header[-1]
                            for i, data_unit in enumerate(
                                "".join(t) for t in zip(data[::2], data[1::2])
                            ):
                                if data_unit == "00":
                                    continue
                                lane_info = LaneInfo(
                                    time=TimeFraction(
                                        measure=measure_base + int(header[:-2]),
                                        fraction=Fraction(i, length),
                                    ),
                                    lane=Lane(
                                        start=int(lane, 36),
                                        length=int(data_unit[1], 36),
                                    ),
                                )
                                note_info = NoteInfo(
                                    lane_info=lane_info,
                                    note_type=int(data_unit[0], 36),
                                    speed_definition=current_speed_def,
                                )
                                if lane_info in note_info_dict:
                                    print(
                                        f"duplicated note {note_info} and {note_info_dict[lane_info]}"
                                    )
                                    continue
                                note_info_dict[lane_info] = note_info
                            continue
                        case "5":
                            length = len(data) // 2
                            lane = header[-1]
                            for i, data_unit in enumerate(
                                "".join(t) for t in zip(data[::2], data[1::2])
                            ):
                                if data_unit == "00":
                                    continue
                                lane_info = LaneInfo(
                                    time=TimeFraction(
                                        measure=measure_base + int(header[:-2]),
                                        fraction=Fraction(i, length),
                                    ),
                                    lane=Lane(
                                        start=int(lane, 36),
                                        length=int(data_unit[1], 36),
                                    ),
                                )
                                modifier_info = ModifierInfo(
                                    lane_info=lane_info,
                                    modifier_type=int(data_unit[0], 36),
                                    speed_definition=current_speed_def,
                                )
                                if lane_info in modifier_info_dict:
                                    print(
                                        f"duplicated modifier {modifier_info} and {modifier_info_dict[lane_info]}"
                                    )
                                    continue
                                modifier_info_dict[lane_info] = modifier_info
                            continue
                case 6:
                    length = len(data) // 2
                    lane = header[-2]
                    channel = header[-1]
                    for i, data_unit in enumerate(
                        "".join(t) for t in zip(data[::2], data[1::2])
                    ):
                        if data_unit == "00":
                            continue
                        lane_info = LaneInfo(
                            time=TimeFraction(
                                measure=measure_base + int(header[:-3]),
                                fraction=Fraction(i, length),
                            ),
                            lane=Lane(
                                start=int(lane, 36), length=int(data_unit[1], 36)
                            ),
                        )
                        hold_info = HoldInfo(
                            lane_info=lane_info,
                            hold_type=int(data_unit[0], 36),
                            speed_definition=current_speed_def,
                        )
                        if lane_info in hold_info_dict[channel]:
                            print(
                                f"duplicated hold {hold_info} and {hold_info_dict[channel][lane_info]}"
                            )
                            continue
                        hold_info_dict[channel][lane_info] = hold_info
                    continue

            print(f"unrecognized header {header}")

        note_dict: dict[LaneInfo, Note] = {}

        for lane_info, note_info in note_info_dict.items():
            modifier_info = modifier_info_dict.pop(lane_info, None)
            if (
                modifier_info
                and modifier_info.speed_definition != note_info.speed_definition
            ):
                print(f"speed definition conflict on {note_info} and {modifier_info}")
            note_dict[lane_info] = Note(
                lane_info=lane_info,
                note_type=note_info.note_type,
                modifier_type=modifier_info.modifier_type if modifier_info else None,
                speed_definition=note_info.speed_definition,
            )

        for lane_info, modifier_info in modifier_info_dict.items():
            note_dict[lane_info] = Note(
                lane_info=lane_info,
                note_type=None,
                modifier_type=modifier_info.modifier_type if modifier_info else None,
                speed_definition=modifier_info.speed_definition,
            )

        for channel_dict in hold_info_dict.values():
            hold_channel = HoldChannel(path=[])
            for hold_info in sorted(channel_dict.values()):
                note = note_dict.pop(hold_info.lane_info, None)
                if note and hold_info.speed_definition != note.speed_definition:
                    print(f"speed definition conflict on {note} and {hold_info}")
                hold_path = HoldPath(
                    lane_info=hold_info.lane_info,
                    note_type=note.note_type if note else None,
                    modifier_type=note.modifier_type if note else None,
                    speed_definition=note.speed_definition
                    if note
                    else hold_info.speed_definition,
                    hold_type=hold_info.hold_type,
                )
                hold_channel.path.append(hold_path)
            self.hold_channels.append(hold_channel)

        self.tap_notes = sorted(note_dict.values())

        return self