# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

from collections import defaultdict
from dataclasses import dataclass, field, replace
from datetime import timedelta
from enum import Enum, auto
from fractions import Fraction
from importlib import metadata
from io import TextIOWrapper
from math import lcm
from pathlib import Path
import re
import shlex
from typing import Optional

from .utils import as_base36


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
class BarLength:
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


class AnySpeedDefinition(Enum):
    _value = auto()


any_speed_definition = AnySpeedDefinition._value


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
    bar_lengths: list[BarLength] = field(default_factory=list)
    bpms: list[BPM] = field(default_factory=list)
    speeds: dict[str, list[Speed]] = field(default_factory=dict)
    tap_notes: list[Note] = field(default_factory=list)
    hold_channels: list[list[HoldChannel]] = field(default_factory=lambda:[[], [], []])

    @classmethod
    def load(cls, f: TextIOWrapper):
        self = cls()

        measure_base: int = 0
        current_speed_def: Optional[str] = None
        bpm_dict: dict[str, float] = {}
        note_info_dict: dict[LaneInfo, NoteInfo] = {}
        modifier_info_dict: dict[LaneInfo, ModifierInfo] = {}
        hold_info_dict: list[defaultdict[str, dict[LaneInfo, HoldInfo]]] = [defaultdict(dict), defaultdict(dict), defaultdict(dict)]

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
                    self.speeds[header[3:]] = []
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
                                    self.bar_lengths.append(
                                        BarLength(
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
                    match header[-3]:
                        case "2" | "3" | "4":
                            length = len(data) // 2
                            hold_category = int(header[-3]) -2
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
                                if lane_info in hold_info_dict[hold_category][channel]:
                                    print(
                                        f"duplicated hold {hold_info} and {hold_info_dict[hold_category][channel][lane_info]}"
                                    )
                                    continue
                                hold_info_dict[hold_category][channel][lane_info] = hold_info
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

        for hold_category, hold_info_category_dict in enumerate(hold_info_dict):
            for channel_dict in hold_info_category_dict.values():
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
                self.hold_channels[hold_category].append(hold_channel)

        self.tap_notes = sorted(note_dict.values())

        return self

    def dump(self, f: TextIOWrapper):
        f.write(
            f"This file was generated by TheerapakG/sus-parser {metadata.version(__package__)}\n"
        )

        if self.title is not None:
            f.write(f'#TITLE "{self.title}"\n')
        if self.subtitle is not None:
            f.write(f'#SUBTITLE "{self.subtitle}"\n')
        if self.artist is not None:
            f.write(f'#ARTIST "{self.artist}"\n')
        if self.genre is not None:
            f.write(f'#GENRE "{self.genre}"\n')
        if self.designer is not None:
            f.write(f'#DESIGNER "{self.designer}"\n')
        if self.difficulty is not None:
            f.write(f"#DIFFICULTY {self.difficulty}\n")
        if self.play_level is not None:
            f.write(
                f'#PLAYLEVEL {self.play_level.level}{"+" if self.play_level.plus else ""}\n'
            )
        if self.song_id is not None:
            f.write(f'#SONGID "{self.song_id}"\n')
        if self.wave is not None:
            f.write(f'#WAVE "{self.wave}"\n')
        if self.wave_offset is not None:
            f.write(f"#WAVEOFFSET {self.wave_offset.total_seconds()}\n")
        if self.jacket is not None:
            f.write(f'#JACKET "{self.jacket}"\n')
        if self.background is not None:
            f.write(f'#BACKGROUND "{self.background}"\n')
        if self.movie is not None:
            f.write(f'#MOVIE "{self.movie}"\n')
        if self.movie_offset is not None:
            f.write(f"#MOVIEOFFSET {self.movie_offset.total_seconds()}\n")
        if self.base_bpm is not None:
            f.write(f"#BASEBPM {self.base_bpm}\n")

        if self.request.ticks_per_beat is not None:
            f.write(f'#REQUEST "ticks_per_beat {self.request.ticks_per_beat}"\n')
        if self.request.enable_priority is not None:
            f.write(
                f'#REQUEST "enable_priority {"true" if self.request.enable_priority else "false"}"\n'
            )

        measure_base: int = 0

        def get_write_measure(measure: int):
            nonlocal measure_base
            current_measure_base = measure // 1000
            if current_measure_base != measure_base:
                measure_base = current_measure_base
                f.write(f"#MEASUREBS {measure_base * 1000}")
            return f"{measure % 1000:03d}"

        for bar_length in self.bar_lengths:
            f.write(
                f"#{get_write_measure(bar_length.measure)}02: {bar_length.length}\n"
            )

        bpm_id_dict = {
            bpm: i for i, bpm in enumerate({bpm.bpm for bpm in self.bpms}, 1)
        }
        for bpm, i in bpm_id_dict.items():
            f.write(f"#BPM{as_base36(i):>02}: {bpm}\n")

        measure_bpm_dict: defaultdict[int, list[BPM]] = defaultdict(list)
        for bpm in self.bpms:
            measure_bpm_dict[bpm.time.measure].append(bpm)

        for measure, bpms in sorted(measure_bpm_dict.items()):
            bpms = sorted(bpms, key=lambda bpm: bpm.time.fraction.denominator)
            while bpms:
                greatest_denom = bpms[-1].time.fraction.denominator
                current_pass_bpms = [
                    bpm
                    for bpm in bpms
                    if lcm(bpm.time.fraction.denominator, greatest_denom)
                    == greatest_denom
                ]
                bpms = [
                    bpm
                    for bpm in bpms
                    if lcm(bpm.time.fraction.denominator, greatest_denom)
                    != greatest_denom
                ]

                fraction_bpm_dict = {
                    bpm.time.fraction: bpm for bpm in current_pass_bpms
                }
                data = "".join(
                    f"{as_base36(bpm_id_dict[fraction_bpm_dict[fraction].bpm]):>02}"
                    if (fraction := Fraction(i, greatest_denom)) in fraction_bpm_dict
                    else "00"
                    for i in range(greatest_denom)
                )

                f.write(f"#{get_write_measure(measure)}08: {data}\n")

        for speed_id, speeds in self.speeds.items():
            data = ", ".join(
                f"{speed.time.measure}'{speed.time.tick}:{speed.speed}"
                for speed in speeds
            )
            f.write(f'#TIL{speed_id}: "{data}"\n')

        note_info_dict: defaultdict[Optional[str], list[NoteInfo]] = defaultdict(list)
        modifier_info_dict: defaultdict[
            Optional[str], list[ModifierInfo]
        ] = defaultdict(list)
        hold_info_dict: list[defaultdict[
            Optional[str], defaultdict[int, list[HoldInfo]]
        ]] = [defaultdict(lambda: defaultdict(list)), defaultdict(lambda: defaultdict(list)), defaultdict(lambda: defaultdict(list))]

        for n in self.tap_notes:
            if n.note_type is not None:
                note_info_dict[
                    n.speed_definition
                    if not isinstance(n.speed_definition, AnySpeedDefinition)
                    else None
                ].append(
                    NoteInfo(
                        lane_info=n.lane_info,
                        note_type=n.note_type,
                        speed_definition=n.speed_definition,
                    )
                )
            if n.modifier_type is not None:
                modifier_info_dict[
                    n.speed_definition
                    if not isinstance(n.speed_definition, AnySpeedDefinition)
                    else None
                ].append(
                    ModifierInfo(
                        lane_info=n.lane_info,
                        modifier_type=n.modifier_type,
                        speed_definition=n.speed_definition,
                    )
                )

        for category, hold_category_channel in enumerate(self.hold_channels):
            for i, c in enumerate(hold_category_channel):
                for n in c.path:
                    if n.note_type is not None:
                        note_info_dict[
                            n.speed_definition
                            if not isinstance(n.speed_definition, AnySpeedDefinition)
                            else None
                        ].append(
                            NoteInfo(
                                lane_info=n.lane_info,
                                note_type=n.note_type,
                                speed_definition=n.speed_definition,
                            )
                        )
                    if n.modifier_type is not None:
                        modifier_info_dict[
                            n.speed_definition
                            if not isinstance(n.speed_definition, AnySpeedDefinition)
                            else None
                        ].append(
                            ModifierInfo(
                                lane_info=n.lane_info,
                                modifier_type=n.modifier_type,
                                speed_definition=n.speed_definition,
                            )
                        )
                    hold_info_dict[category][
                        n.speed_definition
                        if not isinstance(n.speed_definition, AnySpeedDefinition)
                        else None
                    ][i].append(
                        HoldInfo(
                            lane_info=n.lane_info,
                            hold_type=n.hold_type,
                            speed_definition=n.speed_definition,
                        )
                    )

        speed_definition_set = {
            *note_info_dict.keys(),
            *modifier_info_dict.keys(),
            *(k for hold_info_category_dict in hold_info_dict for k in hold_info_category_dict.keys()),
        }
        speed_definitions: list[Optional[str]] = [
            None,
            *(i for i in speed_definition_set if i is not None),
        ]
        for speed_definition in speed_definitions:
            if speed_definition is not None:
                f.write(f"HISPEED: {speed_definition}\n")
                f.write(f"MEASUREHS: {speed_definition}\n")

            measure_note_dict: defaultdict[int, list[NoteInfo]] = defaultdict(list)

            for n in note_info_dict[speed_definition]:
                measure_note_dict[n.lane_info.time.measure].append(n)

            for measure, measure_note_list in sorted(measure_note_dict.items()):
                lane_note_dict: defaultdict[int, list[NoteInfo]] = defaultdict(list)

                for n in measure_note_list:
                    lane_note_dict[n.lane_info.lane.start].append(n)

                for start, lane_note_list in sorted(lane_note_dict.items()):
                    notes: list[NoteInfo] = sorted(
                        lane_note_list,
                        key=lambda n: n.lane_info.time.fraction.denominator,
                    )
                    while notes:
                        greatest_denom = notes[-1].lane_info.time.fraction.denominator
                        current_pass_notes = [
                            n
                            for n in notes
                            if lcm(
                                n.lane_info.time.fraction.denominator, greatest_denom
                            )
                            == greatest_denom
                        ]
                        notes = [
                            n
                            for n in notes
                            if lcm(
                                n.lane_info.time.fraction.denominator, greatest_denom
                            )
                            != greatest_denom
                        ]

                        fraction_note_dict = {
                            n.lane_info.time.fraction: n for n in current_pass_notes
                        }
                        data = "".join(
                            f"{as_base36(fraction_note_dict[fraction].note_type)}{as_base36(fraction_note_dict[fraction].lane_info.lane.length)}"
                            if (fraction := Fraction(i, greatest_denom))
                            in fraction_note_dict
                            else "00"
                            for i in range(greatest_denom)
                        )

                        f.write(
                            f"#{get_write_measure(measure)}1{as_base36(start)}: {data}\n"
                        )

            measure_modifier_dict: defaultdict[int, list[ModifierInfo]] = defaultdict(
                list
            )

            for n in modifier_info_dict[speed_definition]:
                measure_modifier_dict[n.lane_info.time.measure].append(n)

            for measure, measure_modifier_list in sorted(measure_modifier_dict.items()):
                lane_modifier_dict: defaultdict[int, list[ModifierInfo]] = defaultdict(
                    list
                )

                for n in measure_modifier_list:
                    lane_modifier_dict[n.lane_info.lane.start].append(n)

                for start, lane_modifier_list in sorted(lane_modifier_dict.items()):
                    modifiers: list[ModifierInfo] = sorted(
                        lane_modifier_list,
                        key=lambda n: n.lane_info.time.fraction.denominator,
                    )
                    while modifiers:
                        greatest_denom = modifiers[
                            -1
                        ].lane_info.time.fraction.denominator
                        current_pass_modifiers = [
                            n
                            for n in modifiers
                            if lcm(
                                n.lane_info.time.fraction.denominator, greatest_denom
                            )
                            == greatest_denom
                        ]
                        modifiers = [
                            n
                            for n in modifiers
                            if lcm(
                                n.lane_info.time.fraction.denominator, greatest_denom
                            )
                            != greatest_denom
                        ]

                        fraction_modifier_dict = {
                            n.lane_info.time.fraction: n for n in current_pass_modifiers
                        }
                        data = "".join(
                            f"{as_base36(fraction_modifier_dict[fraction].modifier_type)}{as_base36(fraction_modifier_dict[fraction].lane_info.lane.length)}"
                            if (fraction := Fraction(i, greatest_denom))
                            in fraction_modifier_dict
                            else "00"
                            for i in range(greatest_denom)
                        )

                        f.write(
                            f"#{get_write_measure(measure)}5{as_base36(start)}: {data}\n"
                        )

            for category, hold_info_category_dict in enumerate(hold_info_dict):
                for c, hold_channel in hold_info_category_dict[speed_definition].items():
                    measure_hold_dict: defaultdict[int, list[HoldInfo]] = defaultdict(list)

                    for n in hold_channel:
                        measure_hold_dict[n.lane_info.time.measure].append(n)

                    for measure, measure_hold_list in sorted(measure_hold_dict.items()):
                        lane_hold_dict: defaultdict[int, list[HoldInfo]] = defaultdict(list)

                        for n in measure_hold_list:
                            lane_hold_dict[n.lane_info.lane.start].append(n)

                        for start, lane_hold_list in sorted(lane_hold_dict.items()):
                            holds: list[HoldInfo] = sorted(
                                lane_hold_list,
                                key=lambda n: n.lane_info.time.fraction.denominator,
                            )
                            while holds:
                                greatest_denom = holds[
                                    -1
                                ].lane_info.time.fraction.denominator
                                current_pass_holds = [
                                    n
                                    for n in holds
                                    if lcm(
                                        n.lane_info.time.fraction.denominator,
                                        greatest_denom,
                                    )
                                    == greatest_denom
                                ]
                                holds = [
                                    n
                                    for n in holds
                                    if lcm(
                                        n.lane_info.time.fraction.denominator,
                                        greatest_denom,
                                    )
                                    != greatest_denom
                                ]

                                fraction_hold_dict = {
                                    n.lane_info.time.fraction: n for n in current_pass_holds
                                }
                                data = "".join(
                                    f"{as_base36(fraction_hold_dict[fraction].hold_type)}{as_base36(fraction_hold_dict[fraction].lane_info.lane.length)}"
                                    if (fraction := Fraction(i, greatest_denom))
                                    in fraction_hold_dict
                                    else "00"
                                    for i in range(greatest_denom)
                                )

                                f.write(
                                    f"#{get_write_measure(measure)}{category + 2}{as_base36(start)}{as_base36(c)}: {data}\n"
                                )
