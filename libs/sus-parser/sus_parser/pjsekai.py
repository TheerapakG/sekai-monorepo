# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

from collections import defaultdict
from dataclasses import dataclass, field, replace
from datetime import timedelta
from enum import IntEnum
import heapq
from io import TextIOWrapper
from pathlib import Path
from typing import Optional

from .sus import (
    LaneInfo,
    SUS,
    PlayLevel,
    Request,
    Speed,
    Barlength,
    BPM,
    TimeFraction,
    Note as SUSNote,
    Lane,
    AnySpeedDefinition,
    HoldChannel,
    HoldPath as SUSHoldPath,
)


class FeverType(IntEnum):
    On = 1
    Off = 2


@dataclass(slots=True, order=True, frozen=True, unsafe_hash=True)
class Fever:
    time: TimeFraction
    fever_type: FeverType


class NoteType(IntEnum):
    Null = 0
    Normal = 1
    ToggleCritical = 2
    HoldIgnore = 3


class ModifierType(IntEnum):
    Null = 0
    FlickUp = 1
    EaseIn = 2
    FlickUpLeft = 3
    FlickUpRight = 4
    EaseOut = 5


MODIFIER_MAPPING = [
    ModifierType.Null,
    ModifierType.FlickUp,
    ModifierType.EaseIn,
    ModifierType.FlickUpLeft,
    ModifierType.FlickUpRight,
    ModifierType.EaseOut,
    ModifierType.EaseOut,
]
MODIFIER_FLICK = {
    ModifierType.FlickUp,
    ModifierType.FlickUpLeft,
    ModifierType.FlickUpRight,
}
MODIFIER_EASE = {ModifierType.EaseIn, ModifierType.EaseOut}


class HoldType(IntEnum):
    Start = 1
    End = 2
    Visible = 3
    Invisible = 5


@dataclass(slots=True, order=True, frozen=True, unsafe_hash=True)
class Note:
    lane_info: LaneInfo
    note_type: NoteType
    modifier_type: ModifierType
    speed_definition: Optional[str | AnySpeedDefinition]


@dataclass(slots=True, order=True, frozen=True)
class HoldPath(Note):
    hold_type: HoldType


@dataclass(slots=True, order=True)
class HoldNote:
    path: list[HoldPath]


@dataclass(slots=True)
class PjsekaiSUS:
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
    skills: list[TimeFraction] = field(default_factory=list)
    fevers: list[Fever] = field(default_factory=list)
    tap_notes: list[Note] = field(default_factory=list)
    hold_notes: list[HoldNote] = field(default_factory=list)

    @classmethod
    def from_sus(cls, sus: SUS):
        self = cls(
            title=sus.title,
            subtitle=sus.subtitle,
            artist=sus.artist,
            genre=sus.genre,
            designer=sus.designer,
            difficulty=sus.difficulty,
            play_level=sus.play_level,
            song_id=sus.song_id,
            wave=sus.wave,
            wave_offset=sus.wave_offset,
            jacket=sus.jacket,
            background=sus.background,
            movie=sus.movie,
            movie_offset=sus.movie_offset,
            base_bpm=sus.base_bpm,
            request=sus.request,
            barlengths=sus.barlengths.copy(),
            bpms=sus.bpms.copy(),
        )

        self.speeds = defaultdict(list)
        for k, v in sus.speeds.items():
            self.speeds[k] = v.copy()

        for n in sus.tap_notes:
            match n.lane_info.lane:
                case 0:
                    self.skills.append(n.lane_info.time)
                case 15:
                    self.fevers.append(
                        Fever(time=n.lane_info.time, fever_type=FeverType(n.note_type))
                    )
                case _:
                    self.tap_notes.append(
                        Note(
                            lane_info=replace(n.lane_info, lane=n.lane_info.lane - 2),
                            note_type=NoteType(n.note_type)
                            if n.note_type is not None
                            else NoteType.Null,
                            modifier_type=MODIFIER_MAPPING[n.modifier_type]
                            if n.modifier_type is not None
                            else ModifierType.Null,
                            speed_definition=n.speed_definition,
                        )
                    )

        for channel in sus.hold_channels:
            current_path: list[HoldPath] = []
            for n in channel.path:
                current_path.append(
                    HoldPath(
                        lane_info=replace(n.lane_info, lane=n.lane_info.lane - 2),
                        note_type=NoteType(n.note_type)
                        if n.note_type is not None
                        else NoteType.Null,
                        modifier_type=MODIFIER_MAPPING[n.modifier_type]
                        if n.modifier_type is not None
                        else ModifierType.Null,
                        hold_type=HoldType(n.hold_type),
                        speed_definition=n.speed_definition,
                    )
                )

                if current_path[-1].hold_type == HoldType.End:
                    self.hold_notes.append(HoldNote(path=current_path))
                    current_path = []

            if current_path:
                print(f"leftover hold path {current_path}")

        return self

    def to_sus(self):
        sus = SUS(
            title=self.title,
            subtitle=self.subtitle,
            artist=self.artist,
            genre=self.genre,
            designer=self.designer,
            difficulty=self.difficulty,
            play_level=self.play_level,
            song_id=self.song_id,
            wave=self.wave,
            wave_offset=self.wave_offset,
            jacket=self.jacket,
            background=self.background,
            movie=self.movie,
            movie_offset=self.movie_offset,
            base_bpm=self.base_bpm,
            request=self.request,
            speeds=self.speeds,
            barlengths=self.barlengths,
            bpms=self.bpms,
        )

        for t in self.skills:
            sus.tap_notes.append(
                SUSNote(
                    lane_info=LaneInfo(
                        time=t,
                        lane=Lane(0, 1),
                    ),
                    note_type=4,
                    modifier_type=None,
                    speed_definition=AnySpeedDefinition(),
                )
            )

        for f in self.fevers:
            sus.tap_notes.append(
                SUSNote(
                    lane_info=LaneInfo(
                        time=f.time,
                        lane=Lane(15, 1),
                    ),
                    note_type=int(f.fever_type),
                    modifier_type=None,
                    speed_definition=AnySpeedDefinition(),
                )
            )

        for n in self.tap_notes:
            sus.tap_notes.append(
                SUSNote(
                    lane_info=replace(n.lane_info, lane=n.lane_info.lane + 2),
                    note_type=int(n.note_type),
                    modifier_type=int(n.modifier_type),
                    speed_definition=n.speed_definition,
                )
            )

        hold_channels: list[HoldChannel] = []
        for hold_note in sorted(self.hold_notes, key=lambda h: h.path[0].lane_info):
            hold_path = [
                SUSHoldPath(
                    lane_info=replace(n.lane_info, lane=n.lane_info.lane + 2),
                    note_type=int(n.note_type),
                    modifier_type=int(n.modifier_type),
                    hold_type=int(n.hold_type),
                    speed_definition=n.speed_definition,
                )
                for n in hold_note.path
            ]

            if (
                hold_channels
                and hold_channels[0].path[-1].lane_info.time
                < hold_path[0].lane_info.time
            ):
                channel = hold_channels[0]
                channel.path.extend(hold_path)
                heapq.heapreplace(hold_channels, channel)
            else:
                heapq.heappush(hold_channels, HoldChannel(path=hold_path))

        sus.hold_channels = hold_channels

        return sus

    @classmethod
    def read(cls, f: TextIOWrapper):
        return cls.from_sus(SUS.read(f))
