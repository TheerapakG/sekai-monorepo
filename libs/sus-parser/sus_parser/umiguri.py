# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field
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
    BarLength,
    BPM,
    TimeFraction,
    Note as SUSNote,
    AnySpeedDefinition,
    HoldChannel,
    HoldPath as SUSHoldPath,
)


class NoteType(IntEnum):
    Null = 0
    Tap = 1
    ExTap = 2
    Flick = 3
    Ignore = 4


class ModifierType(IntEnum):
    Null = 0
    AirUp = 1
    AirDown = 2
    AirUpLeft = 3
    AirDownLeft = 4
    AirUpRight = 5
    AirDownRight = 6


class HoldType(IntEnum):
    Start = 1
    End = 2
    Relay = 3
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
class UmiguriSUS:
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
    hold_notes: list[HoldNote] = field(default_factory=list)
    slide_notes: list[HoldNote] = field(default_factory=list)
    air_notes: list[HoldNote] = field(default_factory=list)

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
            bar_lengths=sus.bar_lengths.copy(),
            bpms=sus.bpms.copy(),
        )

        self.speeds = dict()
        for k, v in sus.speeds.items():
            self.speeds[k] = v.copy()

        for n in sus.tap_notes:
            self.tap_notes.append(
                Note(
                    lane_info=n.lane_info,
                    note_type=NoteType(n.note_type)
                    if n.note_type is not None
                    else NoteType.Null,
                    modifier_type=ModifierType(n.modifier_type)
                    if n.modifier_type is not None
                    else ModifierType.Null,
                    speed_definition=n.speed_definition,
                )
            )

        for channel in sus.hold_channels[0]:
            current_path: list[HoldPath] = []
            for n in channel.path:
                current_path.append(
                    HoldPath(
                        lane_info=n.lane_info,
                        note_type=NoteType(n.note_type)
                        if n.note_type is not None
                        else NoteType.Null,
                        modifier_type=ModifierType(n.modifier_type)
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

        for channel in sus.hold_channels[1]:
            current_path: list[HoldPath] = []
            for n in channel.path:
                current_path.append(
                    HoldPath(
                        lane_info=n.lane_info,
                        note_type=NoteType(n.note_type)
                        if n.note_type is not None
                        else NoteType.Null,
                        modifier_type=ModifierType(n.modifier_type)
                        if n.modifier_type is not None
                        else ModifierType.Null,
                        hold_type=HoldType(n.hold_type),
                        speed_definition=n.speed_definition,
                    )
                )

                if current_path[-1].hold_type == HoldType.End:
                    self.slide_notes.append(HoldNote(path=current_path))
                    current_path = []

            if current_path:
                print(f"leftover slide path {current_path}")

        for channel in sus.hold_channels[2]:
            current_path: list[HoldPath] = []
            for n in channel.path:
                current_path.append(
                    HoldPath(
                        lane_info=n.lane_info,
                        note_type=NoteType(n.note_type)
                        if n.note_type is not None
                        else NoteType.Null,
                        modifier_type=ModifierType(n.modifier_type)
                        if n.modifier_type is not None
                        else ModifierType.Null,
                        hold_type=HoldType(n.hold_type),
                        speed_definition=n.speed_definition,
                    )
                )

                if current_path[-1].hold_type == HoldType.End:
                    self.air_notes.append(HoldNote(path=current_path))
                    current_path = []

            if current_path:
                print(f"leftover air path {current_path}")

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
            bar_lengths=self.bar_lengths.copy(),
            bpms=self.bpms.copy(),
        )

        sus.speeds = dict()
        for k, v in self.speeds.items():
            sus.speeds[k] = v.copy()

        for n in self.tap_notes:
            sus.tap_notes.append(
                SUSNote(
                    lane_info= n.lane_info,
                    note_type=int(n.note_type)
                    if n.note_type != NoteType.Null
                    else None,
                    modifier_type=int(n.modifier_type)
                    if n.modifier_type != ModifierType.Null
                    else None,
                    speed_definition=n.speed_definition,
                )
            )

        hold_channels: list[list[tuple[TimeFraction, HoldChannel]]] = [[], [], []]
        hold_notes = [self.hold_notes, self.slide_notes, self.air_notes]
        for category, hold_category_notes in enumerate(hold_notes):
            for hold_note in sorted(hold_category_notes, key=lambda h: h.path[0].lane_info):
                hold_path = [
                    SUSHoldPath(
                        lane_info=n.lane_info,
                        note_type=int(n.note_type)
                        if n.note_type != NoteType.Null
                        else None,
                        modifier_type=int(n.modifier_type)
                        if n.modifier_type != ModifierType.Null
                        else None,
                        hold_type=int(n.hold_type),
                        speed_definition=n.speed_definition,
                    )
                    for n in hold_note.path
                ]

                if hold_channels[category] and hold_channels[category][0][0] < hold_path[0].lane_info.time:
                    new_channel = (hold_path[-1].lane_info.time, hold_channels[category][0][1])
                    new_channel[1].path.extend(hold_path)
                    heapq.heapreplace(hold_channels[category], new_channel)
                else:
                    heapq.heappush(
                        hold_channels[category],
                        (hold_path[-1].lane_info.time, HoldChannel(path=hold_path)),
                    )

        sus.hold_channels = [[c for _, c in hold_category_channels] for hold_category_channels in hold_channels]

        return sus

    @classmethod
    def load(cls, f: TextIOWrapper):
        return cls.from_sus(SUS.load(f))

    def dump(self, f: TextIOWrapper):
        self.to_sus().dump(f)
