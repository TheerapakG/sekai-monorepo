# SPDX-FileCopyrightText: 2022-2023 Erik Chan <erikchan002@gmail.com>
# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT


from datetime import datetime
from functools import partial
from typing import List, Optional, Union, get_args, get_origin

from attrs import Factory, define, has, fields

from pjsekai.enums import *
from pjsekai.models.model import to_pjsekai_camel

from cattrs.converters import BaseConverter
from cattrs.preconf.json import make_converter as make_json_converter
from cattrs.preconf.msgpack import make_converter as make_msgpack_converter
from cattrs.gen import make_dict_unstructure_fn, make_dict_structure_fn, override

json_converter = make_json_converter()
msgpack_converter = make_msgpack_converter()


def to_pjsekai_camel_unstructure(converter: BaseConverter, cls):
    return make_dict_unstructure_fn(
        cls,
        converter,
        **{a.name: override(rename=to_pjsekai_camel(a.name)) for a in fields(cls)}
    )


def to_pjsekai_camel_structure(converter: BaseConverter, cls):
    return make_dict_structure_fn(
        cls,
        converter,
        **{a.name: override(rename=to_pjsekai_camel(a.name)) for a in fields(cls)}
    )


def is_union_unknown(cls):
    if get_origin(cls) is not Union:
        return False
    args = list(get_args(cls))
    try:
        args.remove(Unknown)
    except ValueError:
        pass
    try:
        args.remove(type(None))
    except ValueError:
        pass
    return len(args) < 2


def to_union_unknown(converter: BaseConverter, data, cls):
    args = get_args(cls)
    not_unknown = next(
        (value for value in args if value is not Unknown and value is not type(None))
    )
    if data is None:
        return None
    try:
        if not_unknown is datetime and isinstance(data, int):
            data = data / 1000
        return converter.structure(data, not_unknown)
    except ValueError:
        return Unknown(data)


def to_union_dict_str_int(data, cls):
    if isinstance(data, Union[dict, str, int]):
        return data
    raise ValueError()


json_converter.register_unstructure_hook_factory(
    has, partial(to_pjsekai_camel_unstructure, json_converter)
)
json_converter.register_structure_hook_factory(
    has, partial(to_pjsekai_camel_structure, json_converter)
)
json_converter.register_structure_hook_func(
    is_union_unknown, partial(to_union_unknown, json_converter)
)
json_converter.register_structure_hook(Union[dict, str, int], to_union_dict_str_int)

msgpack_converter.register_unstructure_hook_factory(
    has, partial(to_pjsekai_camel_unstructure, msgpack_converter)
)
msgpack_converter.register_structure_hook_factory(
    has, partial(to_pjsekai_camel_structure, msgpack_converter)
)
msgpack_converter.register_structure_hook_func(
    is_union_unknown, partial(to_union_unknown, msgpack_converter)
)
msgpack_converter.register_structure_hook(Union[dict, str, int], to_union_dict_str_int)


@define
class GameCharacter:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    resource_id: Optional[int] = Factory(lambda: None)
    first_name: Optional[str] = Factory(lambda: None)
    given_name: Optional[str] = Factory(lambda: None)
    first_name_ruby: Optional[str] = Factory(lambda: None)
    given_name_ruby: Optional[str] = Factory(lambda: None)
    gender: Optional[Union[Gender, Unknown]] = Factory(lambda: None)
    height: Optional[float] = Factory(lambda: None)
    live2d_height_adjustment: Optional[float] = Factory(lambda: None)
    figure: Optional[Union[Figure, Unknown]] = Factory(lambda: None)
    breast_size: Optional[Union[BreastSize, Unknown]] = Factory(lambda: None)
    model_name: Optional[str] = Factory(lambda: None)
    unit: Optional[Union[Unit, Unknown]] = Factory(lambda: None)
    support_unit_type: Optional[Union[SupportUnitType, Unknown]] = Factory(lambda: None)


@define
class GameCharacterUnit:
    id: Optional[int] = Factory(lambda: None)
    game_character_id: Optional[int] = Factory(lambda: None)
    unit: Optional[Union[Unit, Unknown]] = Factory(lambda: None)
    color_code: Optional[str] = Factory(lambda: None)
    skin_color_code: Optional[str] = Factory(lambda: None)
    skin_shadow_color_code1: Optional[str] = Factory(lambda: None)
    skin_shadow_color_code2: Optional[str] = Factory(lambda: None)


@define
class OutsideCharacter:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)


@define
class Character3d:
    id: Optional[int] = Factory(lambda: None)
    character_type: Optional[Union[CharacterType, Unknown]] = Factory(lambda: None)
    character_id: Optional[int] = Factory(lambda: None)
    unit: Optional[Union[Unit, Unknown]] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    head_costume3d_id: Optional[int] = Factory(lambda: None)
    hair_costume3d_id: Optional[int] = Factory(lambda: None)
    body_costume3d_id: Optional[int] = Factory(lambda: None)


@define
class Character2d:
    id: Optional[int] = Factory(lambda: None)
    character_type: Optional[Union[CharacterType, Unknown]] = Factory(lambda: None)
    character_id: Optional[int] = Factory(lambda: None)
    unit: Optional[Union[Unit, Unknown]] = Factory(lambda: None)
    asset_name: Optional[str] = Factory(lambda: None)


@define
class CharacterProfile:
    character_id: Optional[int] = Factory(lambda: None)
    character_voice: Optional[str] = Factory(lambda: None)
    birthday: Optional[str] = Factory(lambda: None)
    height: Optional[str] = Factory(lambda: None)
    school: Optional[str] = Factory(lambda: None)
    school_year: Optional[str] = Factory(lambda: None)
    hobby: Optional[str] = Factory(lambda: None)
    special_skill: Optional[str] = Factory(lambda: None)
    favorite_food: Optional[str] = Factory(lambda: None)
    hated_food: Optional[str] = Factory(lambda: None)
    weak: Optional[str] = Factory(lambda: None)
    introduction: Optional[str] = Factory(lambda: None)
    scenario_id: Optional[str] = Factory(lambda: None)


@define
class Bond:
    id: Optional[int] = Factory(lambda: None)
    group_id: Optional[int] = Factory(lambda: None)
    character_id1: Optional[int] = Factory(lambda: None)
    character_id2: Optional[int] = Factory(lambda: None)


@define
class Live2d:
    id: Optional[int] = Factory(lambda: None)
    character_id: Optional[int] = Factory(lambda: None)
    unit: Optional[Union[Unit, Unknown]] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    motion: Optional[str] = Factory(lambda: None)
    expression: Optional[str] = Factory(lambda: None)
    weight: Optional[int] = Factory(lambda: None)


@define
class BondsLive2d(Live2d):
    default_flg: Optional[bool] = Factory(lambda: None)


@define
class BondsRankUpLive2d(Live2d):
    default_flg: Optional[bool] = Factory(lambda: None)


@define
class UnitProfile:
    unit: Optional[Union[Unit, Unknown]] = Factory(lambda: None)
    unit_name: Optional[str] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    profile_sentence: Optional[str] = Factory(lambda: None)
    color_code: Optional[str] = Factory(lambda: None)


@define
class ActionSet:
    id: Optional[int] = Factory(lambda: None)
    area_id: Optional[int] = Factory(lambda: None)
    script_id: Optional[str] = Factory(lambda: None)
    character_ids: Optional[List[int]] = Factory(lambda: None)
    archive_display_type: Optional[Union[ArchiveDisplayType, Unknown]] = Factory(
        lambda: None
    )
    archive_published_at: Optional[datetime] = Factory(lambda: None)
    release_condition_id: Optional[datetime] = Factory(lambda: None)
    scenario_id: Optional[str] = Factory(lambda: None)
    action_set_type: Optional[Union[ActionSetType, Unknown]] = Factory(lambda: None)
    special_season_id: Optional[int] = Factory(lambda: None)


@define
class Area:
    id: Optional[int] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    area_type: Optional[Union[AreaType, Unknown]] = Factory(lambda: None)
    view_type: Optional[Union[ViewType, Unknown]] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    release_condition_id: Optional[int] = Factory(lambda: None)
    label: Optional[str] = Factory(lambda: None)
    start_at: Optional[datetime] = Factory(lambda: None)
    end_at: Optional[datetime] = Factory(lambda: None)


@define
class AreaPlaylist:
    id: Optional[int] = Factory(lambda: None)
    area_id: Optional[int] = Factory(lambda: None)
    music_id: Optional[int] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    bgm_name: Optional[str] = Factory(lambda: None)
    release_condition_id: Optional[int] = Factory(lambda: None)


@define
class MobCharacter:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    gender: Optional[Union[Gender, Unknown]] = Factory(lambda: None)


@define
class CharacterCostume:
    id: Optional[int] = Factory(lambda: None)
    character_id: Optional[int] = Factory(lambda: None)
    costume_id: Optional[int] = Factory(lambda: None)
    sd_asset_bundle_name: Optional[str] = Factory(lambda: None)
    live2d_asset_bundle_name: Optional[str] = Factory(lambda: None)


@define
class CardCostume3d:
    card_id: Optional[int] = Factory(lambda: None)
    costume3d_id: Optional[int] = Factory(lambda: None)


@define
class CardParameter:
    id: Optional[int] = Factory(lambda: None)
    card_id: Optional[int] = Factory(lambda: None)
    card_level: Optional[int] = Factory(lambda: None)
    card_parameter_type: Optional[Union[CardParameterType, Unknown]] = Factory(
        lambda: None
    )
    power: Optional[int] = Factory(lambda: None)


@define
class Cost:
    resource_id: Optional[int] = Factory(lambda: None)
    resource_type: Optional[Union[ResourceType, Unknown]] = Factory(lambda: None)
    resource_level: Optional[int] = Factory(lambda: None)
    quantity: Optional[int] = Factory(lambda: None)


@define
class SpecialTrainingCost:
    card_id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    cost: Optional[Cost] = Factory(lambda: None)


@define
class MasterLessonAchieveResource:
    release_condition_id: Optional[int] = Factory(lambda: None)
    card_id: Optional[int] = Factory(lambda: None)
    master_rank: Optional[int] = Factory(lambda: None)
    resources: Optional[List[Union[dict, str, int]]] = Factory(lambda: None)


@define
class Card:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    character_id: Optional[int] = Factory(lambda: None)
    card_rarity_type: Optional[Union[CardRarityType, Unknown]] = Factory(lambda: None)
    special_training_power1_bonus_fixed: Optional[int] = Factory(lambda: None)
    special_training_power2_bonus_fixed: Optional[int] = Factory(lambda: None)
    special_training_power3_bonus_fixed: Optional[int] = Factory(lambda: None)
    attr: Optional[Union[CardAttr, Unknown]] = Factory(lambda: None)
    support_unit: Optional[Union[Unit, Unknown]] = Factory(lambda: None)
    skill_id: Optional[int] = Factory(lambda: None)
    card_skill_name: Optional[str] = Factory(lambda: None)
    prefix: Optional[str] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    gacha_phrase: Optional[str] = Factory(lambda: None)
    flavor_text: Optional[str] = Factory(lambda: None)
    release_at: Optional[datetime] = Factory(lambda: None)
    archive_published_at: Optional[datetime] = Factory(lambda: None)
    card_parameters: Optional[List[CardParameter]] = Factory(lambda: None)
    special_training_costs: Optional[List[SpecialTrainingCost]] = Factory(lambda: None)
    master_lesson_achieve_resources: Optional[
        List[MasterLessonAchieveResource]
    ] = Factory(lambda: None)
    archive_display_type: Optional[Union[ArchiveDisplayType, Unknown]] = Factory(
        lambda: None
    )


@define
class SkillEffectDetail:
    id: Optional[int] = Factory(lambda: None)
    level: Optional[int] = Factory(lambda: None)
    activate_effect_duration: Optional[float] = Factory(lambda: None)
    activate_effect_value_type: Optional[
        Union[ActivateEffectValueType, Unknown]
    ] = Factory(lambda: None)
    activate_effect_value: Optional[int] = Factory(lambda: None)


@define
class SkillEnhanceCondition:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    unit: Optional[Union[Unit, Unknown]] = Factory(lambda: None)


@define
class SkillEnhance:
    id: Optional[int] = Factory(lambda: None)
    skill_enhance_type: Optional[Union[SkillEnhanceType, Unknown]] = Factory(
        lambda: None
    )
    activate_effect_value_type: Optional[
        Union[ActivateEffectValueType, Unknown]
    ] = Factory(lambda: None)
    activate_effect_value: Optional[int] = Factory(lambda: None)
    skill_enhance_condition: Optional[SkillEnhanceCondition] = Factory(lambda: None)


@define
class SkillEffect:
    id: Optional[int] = Factory(lambda: None)
    skill_effect_type: Optional[Union[SkillEffectType, Unknown]] = Factory(lambda: None)
    activate_notes_judgment_type: Optional[
        Union[IngameNoteJudgeType, Unknown]
    ] = Factory(lambda: None)
    skill_effect_details: Optional[List[SkillEffectDetail]] = Factory(lambda: None)
    activate_life: Optional[int] = Factory(lambda: None)
    condition_type: Optional[Union[SkillEffectConditionType, Unknown]] = Factory(
        lambda: None
    )
    skill_enhance: Optional[SkillEnhance] = Factory(lambda: None)


@define
class Skill:
    id: Optional[int] = Factory(lambda: None)
    short_description: Optional[str] = Factory(lambda: None)
    description: Optional[str] = Factory(lambda: None)
    description_sprite_name: Optional[str] = Factory(lambda: None)
    skill_filter_id: Optional[int] = Factory(lambda: None)
    skill_effects: Optional[List[SkillEffect]] = Factory(lambda: None)


@define
class CardEpisode:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    card_id: Optional[int] = Factory(lambda: None)
    title: Optional[str] = Factory(lambda: None)
    scenario_id: Optional[str] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    release_condition_id: Optional[int] = Factory(lambda: None)
    power1_bonus_fixed: Optional[int] = Factory(lambda: None)
    power2_bonus_fixed: Optional[int] = Factory(lambda: None)
    power3_bonus_fixed: Optional[int] = Factory(lambda: None)
    reward_resource_box_ids: Optional[List[int]] = Factory(lambda: None)
    costs: Optional[List[Cost]] = Factory(lambda: None)
    card_episode_part_type: Optional[Union[CardEpisodePartType, Unknown]] = Factory(
        lambda: None
    )


@define
class CardRarity:
    card_rarity_type: Optional[Union[CardRarityType, Unknown]] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    max_level: Optional[int] = Factory(lambda: None)
    max_skill_level: Optional[int] = Factory(lambda: None)
    training_max_level: Optional[int] = Factory(lambda: None)


@define
class CardSkillCost:
    id: Optional[int] = Factory(lambda: None)
    material_id: Optional[int] = Factory(lambda: None)
    exp: Optional[int] = Factory(lambda: None)


@define
class Music:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    release_condition_id: Optional[int] = Factory(lambda: None)
    categories: Optional[List[Union[MusicCategory, Unknown]]] = Factory(lambda: None)
    title: Optional[str] = Factory(lambda: None)
    pronunciation: Optional[str] = Factory(lambda: None)
    lyricist: Optional[str] = Factory(lambda: None)
    composer: Optional[str] = Factory(lambda: None)
    arranger: Optional[str] = Factory(lambda: None)
    dancer_count: Optional[int] = Factory(lambda: None)
    self_dancer_position: Optional[int] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    live_talk_background_asset_bundle_name: Optional[str] = Factory(lambda: None)
    published_at: Optional[datetime] = Factory(lambda: None)
    live_stage_id: Optional[int] = Factory(lambda: None)
    filler_sec: Optional[float] = Factory(lambda: None)
    music_collaboration_id: Optional[int] = Factory(lambda: None)


@define
class MusicTag:
    id: Optional[int] = Factory(lambda: None)
    music_id: Optional[int] = Factory(lambda: None)
    music_tag: Optional[str] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)


@define
class MusicDifficulty:
    id: Optional[int] = Factory(lambda: None)
    music_id: Optional[int] = Factory(lambda: None)
    music_difficulty: Optional[Union[MusicDifficultyType, Unknown]] = Factory(
        lambda: None
    )
    play_level: Optional[int] = Factory(lambda: None)
    release_condition_id: Optional[int] = Factory(lambda: None)
    total_note_count: Optional[int] = Factory(lambda: None)


@define
class Character:
    id: Optional[int] = Factory(lambda: None)
    music_id: Optional[int] = Factory(lambda: None)
    music_vocal_id: Optional[int] = Factory(lambda: None)
    character_type: Optional[Union[CharacterType, Unknown]] = Factory(lambda: None)
    character_id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)


@define
class MusicVocal:
    id: Optional[int] = Factory(lambda: None)
    music_id: Optional[int] = Factory(lambda: None)
    music_vocal_type: Optional[Union[MusicVocalType, Unknown]] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    release_condition_id: Optional[int] = Factory(lambda: None)
    caption: Optional[str] = Factory(lambda: None)
    characters: Optional[List[Character]] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    archive_published_at: Optional[datetime] = Factory(lambda: None)
    special_season_id: Optional[int] = Factory(lambda: None)
    archive_display_type: Optional[Union[ArchiveDisplayType, Unknown]] = Factory(
        lambda: None
    )


@define
class MusicDanceMember:
    id: Optional[int] = Factory(lambda: None)
    music_id: Optional[int] = Factory(lambda: None)
    default_music_type: Optional[Union[DefaultMusicType, Unknown]] = Factory(
        lambda: None
    )
    character_id1: Optional[int] = Factory(lambda: None)
    unit1: Optional[Union[Unit, Unknown]] = Factory(lambda: None)
    character_id2: Optional[int] = Factory(lambda: None)
    unit2: Optional[Union[Unit, Unknown]] = Factory(lambda: None)
    character_id3: Optional[int] = Factory(lambda: None)
    unit3: Optional[Union[Unit, Unknown]] = Factory(lambda: None)
    character_id4: Optional[int] = Factory(lambda: None)
    unit4: Optional[Union[Unit, Unknown]] = Factory(lambda: None)
    character_id5: Optional[int] = Factory(lambda: None)
    unit5: Optional[Union[Unit, Unknown]] = Factory(lambda: None)


@define
class MusicAchievement:
    id: Optional[int] = Factory(lambda: None)
    music_achievement_type: Optional[Union[MusicAchievementType, Unknown]] = Factory(
        lambda: None
    )
    music_achievement_type_value: Optional[str] = Factory(lambda: None)
    resource_box_id: Optional[int] = Factory(lambda: None)
    music_difficulty_type: Optional[Union[MusicDifficultyType, Unknown]] = Factory(
        lambda: None
    )


@define
class MusicVideoCharacter:
    id: Optional[int] = Factory(lambda: None)
    music_id: Optional[int] = Factory(lambda: None)
    default_music_type: Optional[Union[DefaultMusicType, Unknown]] = Factory(
        lambda: None
    )
    game_character_unit_id: Optional[int] = Factory(lambda: None)
    dance_priority: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    priority: Optional[int] = Factory(lambda: None)


@define
class MusicAssetVariant:
    id: Optional[int] = Factory(lambda: None)
    music_vocal_id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    music_asset_type: Optional[Union[MusicAssetType, Unknown]] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)


@define
class MusicCollaboration:
    id: Optional[int] = Factory(lambda: None)
    label: Optional[str] = Factory(lambda: None)


@define
class EpisodeMusicVideoCostume:
    id: Optional[int] = Factory(lambda: None)
    music_vocal_id: Optional[int] = Factory(lambda: None)
    character3d_id1: Optional[int] = Factory(lambda: None)
    character3d_id2: Optional[int] = Factory(lambda: None)
    character3d_id3: Optional[int] = Factory(lambda: None)
    character3d_id4: Optional[int] = Factory(lambda: None)
    character3d_id5: Optional[int] = Factory(lambda: None)


@define
class ReleaseCondition:
    id: Optional[int] = Factory(lambda: None)
    sentence: Optional[str] = Factory(lambda: None)
    release_condition_type: Optional[Union[ReleaseConditionType, Unknown]] = Factory(
        lambda: None
    )
    release_condition_type_level: Optional[int] = Factory(lambda: None)
    release_condition_type_id: Optional[int] = Factory(lambda: None)
    release_condition_type_quantity: Optional[int] = Factory(lambda: None)


@define
class PlayLevelScore:
    live_type: Optional[Union[LiveType, Unknown]] = Factory(lambda: None)
    play_level: Optional[int] = Factory(lambda: None)
    s: Optional[int] = Factory(lambda: None)
    a: Optional[int] = Factory(lambda: None)
    b: Optional[int] = Factory(lambda: None)
    c: Optional[int] = Factory(lambda: None)


@define
class IngameCombo:
    id: Optional[int] = Factory(lambda: None)
    from_count: Optional[int] = Factory(lambda: None)
    to_count: Optional[int] = Factory(lambda: None)
    score_coefficient: Optional[float] = Factory(lambda: None)


@define
class IngameNote:
    id: Optional[int] = Factory(lambda: None)
    ingame_note_type: Optional[Union[IngameNoteType, Unknown]] = Factory(lambda: None)
    score_coefficient: Optional[float] = Factory(lambda: None)
    damage_bad: Optional[int] = Factory(lambda: None)
    damage_miss: Optional[int] = Factory(lambda: None)


@define
class IngameNoteJudge:
    id: Optional[int] = Factory(lambda: None)
    ingame_note_jadge_type: Optional[Union[IngameNoteJudgeType, Unknown]] = Factory(
        lambda: None
    )
    score_coefficient: Optional[float] = Factory(lambda: None)
    damage: Optional[int] = Factory(lambda: None)


@define
class IngamePlayLevel:
    play_level: Optional[int] = Factory(lambda: None)
    score_coefficient: Optional[float] = Factory(lambda: None)


@define
class IngameCutin:
    id: Optional[int] = Factory(lambda: None)
    music_difficulty: Optional[Union[MusicDifficultyType, Unknown]] = Factory(
        lambda: None
    )
    combo: Optional[int] = Factory(lambda: None)


@define
class IngameCutinCharacter:
    id: Optional[int] = Factory(lambda: None)
    ingame_cutin_character_type: Optional[
        Union[IngameCutinCharacterType, Unknown]
    ] = Factory(lambda: None)
    priority: Optional[int] = Factory(lambda: None)
    game_character_unit_id1: Optional[int] = Factory(lambda: None)
    game_character_unit_id2: Optional[int] = Factory(lambda: None)
    asset_bundle_name1: Optional[str] = Factory(lambda: None)
    asset_bundle_name2: Optional[str] = Factory(lambda: None)
    release_condition_id: Optional[int] = Factory(lambda: None)


@define
class IngameJudgeFrame:
    id: Optional[int] = Factory(lambda: None)
    ingame_note_type: Optional[Union[IngameNoteType, Unknown]] = Factory(lambda: None)
    perfect: Optional[float] = Factory(lambda: None)
    great: Optional[float] = Factory(lambda: None)
    good: Optional[float] = Factory(lambda: None)
    bad: Optional[float] = Factory(lambda: None)
    perfect_before: Optional[float] = Factory(lambda: None)
    perfect_after: Optional[float] = Factory(lambda: None)
    great_before: Optional[float] = Factory(lambda: None)
    great_after: Optional[float] = Factory(lambda: None)
    good_before: Optional[float] = Factory(lambda: None)
    good_after: Optional[float] = Factory(lambda: None)
    bad_before: Optional[float] = Factory(lambda: None)
    bad_after: Optional[float] = Factory(lambda: None)


@define
class IngameNoteJudgeTechnicalScore:
    id: Optional[int] = Factory(lambda: None)
    live_type: Optional[Union[LiveType, Unknown]] = Factory(lambda: None)
    ingame_note_jadge_type: Optional[Union[IngameNoteJudgeType, Unknown]] = Factory(
        lambda: None
    )
    score: Optional[int] = Factory(lambda: None)


@define
class Shop:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    shop_type: Optional[Union[ShopType, Unknown]] = Factory(lambda: None)
    area_id: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    release_condition_id: Optional[int] = Factory(lambda: None)


@define
class ShopItemCost:
    shop_item_id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    cost: Optional[Cost] = Factory(lambda: None)


@define
class ShopItem:
    id: Optional[int] = Factory(lambda: None)
    shop_id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    release_condition_id: Optional[int] = Factory(lambda: None)
    resource_box_id: Optional[int] = Factory(lambda: None)
    costs: Optional[List[ShopItemCost]] = Factory(lambda: None)
    start_at: Optional[datetime] = Factory(lambda: None)


@define
class Costume3dShopItemCost(Cost):
    id: Optional[int] = Factory(lambda: None)
    costume3d_shop_item_id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)


@define
class Costume3dShopItem:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    group_id: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    body_costume3d_id: Optional[int] = Factory(lambda: None)
    release_condition_id: Optional[int] = Factory(lambda: None)
    costs: Optional[List[Costume3dShopItemCost]] = Factory(lambda: None)
    start_at: Optional[datetime] = Factory(lambda: None)
    head_costume3d_id: Optional[int] = Factory(lambda: None)


@define
class AreaItem:
    id: Optional[int] = Factory(lambda: None)
    area_id: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    flavor_text: Optional[str] = Factory(lambda: None)
    spawn_point: Optional[str] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)


@define
class AreaItemLevel:
    area_item_id: Optional[int] = Factory(lambda: None)
    level: Optional[int] = Factory(lambda: None)
    targetunit: Optional[Union[Unit, Unknown]] = Factory(lambda: None)
    target_card_attr: Optional[Union[CardAttr, Unknown]] = Factory(lambda: None)
    target_game_character_id: Optional[int] = Factory(lambda: None)
    power1_bonus_rate: Optional[float] = Factory(lambda: None)
    power1_all_match_bonus_rate: Optional[float] = Factory(lambda: None)
    power2_bonus_rate: Optional[float] = Factory(lambda: None)
    power2_all_match_bonus_rate: Optional[float] = Factory(lambda: None)
    power3_bonus_rate: Optional[float] = Factory(lambda: None)
    power3_all_match_bonus_rate: Optional[float] = Factory(lambda: None)
    sentence: Optional[str] = Factory(lambda: None)


@define
class Material:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    flavor_text: Optional[str] = Factory(lambda: None)
    material_type: Optional[Union[MaterialType, Unknown]] = Factory(lambda: None)


@define
class GachaCardRarityRate:
    id: Optional[int] = Factory(lambda: None)
    group_id: Optional[int] = Factory(lambda: None)
    card_rarity_type: Optional[Union[CardRarityType, Unknown]] = Factory(lambda: None)
    lottery_type: Optional[Union[LotteryType, Unknown]] = Factory(lambda: None)
    rate: Optional[float] = Factory(lambda: None)


@define
class GachaDetail:
    id: Optional[int] = Factory(lambda: None)
    gacha_id: Optional[int] = Factory(lambda: None)
    card_id: Optional[int] = Factory(lambda: None)
    weight: Optional[int] = Factory(lambda: None)
    is_wish: Optional[bool] = Factory(lambda: None)


@define
class GachaBehavior:
    id: Optional[int] = Factory(lambda: None)
    gacha_id: Optional[int] = Factory(lambda: None)
    group_id: Optional[int] = Factory(lambda: None)
    priority: Optional[int] = Factory(lambda: None)
    gacha_behavior_type: Optional[Union[GachaBehaviorType, Unknown]] = Factory(
        lambda: None
    )
    cost_resource_type: Optional[Union[ResourceType, Unknown]] = Factory(lambda: None)
    cost_resource_quantity: Optional[int] = Factory(lambda: None)
    spin_count: Optional[int] = Factory(lambda: None)
    execute_limit: Optional[int] = Factory(lambda: None)
    cost_resource_id: Optional[int] = Factory(lambda: None)
    gacha_extra_id: Optional[int] = Factory(lambda: None)


@define
class GachaPickup:
    id: Optional[int] = Factory(lambda: None)
    gacha_id: Optional[int] = Factory(lambda: None)
    card_id: Optional[int] = Factory(lambda: None)
    gacha_pickup_type: Optional[Union[GachaPickupType, Unknown]] = Factory(lambda: None)


@define
class GachaInformation:
    gacha_id: Optional[int] = Factory(lambda: None)
    summary: Optional[str] = Factory(lambda: None)
    description: Optional[str] = Factory(lambda: None)


@define
class Gacha:
    id: Optional[int] = Factory(lambda: None)
    gacha_type: Optional[Union[GachaType, Unknown]] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    gacha_card_rarity_rate_group_id: Optional[int] = Factory(lambda: None)
    start_at: Optional[datetime] = Factory(lambda: None)
    end_at: Optional[datetime] = Factory(lambda: None)
    is_show_period: Optional[bool] = Factory(lambda: None)
    gacha_ceil_item_id: Optional[int] = Factory(lambda: None)
    wish_select_count: Optional[int] = Factory(lambda: None)
    wish_fixed_select_count: Optional[int] = Factory(lambda: None)
    wish_limited_select_count: Optional[int] = Factory(lambda: None)
    gacha_card_rarity_rates: Optional[List[GachaCardRarityRate]] = Factory(lambda: None)
    gacha_details: Optional[List[GachaDetail]] = Factory(lambda: None)
    gacha_behaviors: Optional[List[GachaBehavior]] = Factory(lambda: None)
    gacha_pickups: Optional[List[GachaPickup]] = Factory(lambda: None)
    gacha_pickup_costumes: Optional[List[Union[dict, str, int]]] = Factory(lambda: None)
    gacha_information: Optional[GachaInformation] = Factory(lambda: None)
    drawable_gacha_hour: Optional[int] = Factory(lambda: None)
    gacha_bonus_id: Optional[int] = Factory(lambda: None)
    spin_limit: Optional[int] = Factory(lambda: None)


@define
class GachaBonus:
    id: Optional[int] = Factory(lambda: None)


@define
class GachaBonusPoint:
    id: Optional[int] = Factory(lambda: None)
    resource_type: Optional[Union[ResourceType, Unknown]] = Factory(lambda: None)
    point: Optional[float] = Factory(lambda: None)


@define
class GachaExtra:
    id: Optional[int] = Factory(lambda: None)
    resource_box_id: Optional[int] = Factory(lambda: None)


@define
class GiftGachaExchange:
    id: Optional[int] = Factory(lambda: None)
    gacha_id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    resource_box_id: Optional[int] = Factory(lambda: None)


@define
class PracticeTicket:
    id: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    exp: Optional[int] = Factory(lambda: None)
    flavor_text: Optional[str] = Factory(lambda: None)


@define
class SkillPracticeTicket(PracticeTicket):
    pass


@define
class Level:
    id: Optional[int] = Factory(lambda: None)
    level_type: Optional[Union[LevelType, Unknown]] = Factory(lambda: None)
    level: Optional[int] = Factory(lambda: None)
    total_exp: Optional[int] = Factory(lambda: None)


@define
class Episode:
    id: Optional[int] = Factory(lambda: None)
    episode_no: Optional[int] = Factory(lambda: None)
    title: Optional[str] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    scenario_id: Optional[str] = Factory(lambda: None)
    release_condition_id: Optional[int] = Factory(lambda: None)
    reward_resource_box_ids: Optional[List[int]] = Factory(lambda: None)


@define
class UnitStoryEpisode(Episode):
    unit: Optional[Union[Unit, Unknown]] = Factory(lambda: None)
    chapter_no: Optional[int] = Factory(lambda: None)
    unit_episode_category: Optional[Union[Unit, Unknown]] = Factory(lambda: None)
    episode_no_label: Optional[str] = Factory(lambda: None)
    limited_release_start_at: Optional[datetime] = Factory(lambda: None)
    limited_release_end_at: Optional[datetime] = Factory(lambda: None)
    and_release_condition_id: Optional[int] = Factory(lambda: None)


@define
class Chapter:
    id: Optional[int] = Factory(lambda: None)
    unit: Optional[Union[Unit, Unknown]] = Factory(lambda: None)
    chapter_no: Optional[int] = Factory(lambda: None)
    title: Optional[str] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    episodes: Optional[List[UnitStoryEpisode]] = Factory(lambda: None)


@define
class UnitStory:
    unit: Optional[Union[Unit, Unknown]] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    chapters: Optional[List[Chapter]] = Factory(lambda: None)


@define
class SpecialStoryEpisode(Episode):
    special_story_id: Optional[int] = Factory(lambda: None)
    special_story_episode_type: Optional[str] = Factory(lambda: None)
    is_able_skip: Optional[bool] = Factory(lambda: None)
    is_action_set_refresh: Optional[bool] = Factory(lambda: None)
    special_story_episode_type_id: Optional[int] = Factory(lambda: None)


@define
class SpecialStory:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    title: Optional[str] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    start_at: Optional[datetime] = Factory(lambda: None)
    end_at: Optional[datetime] = Factory(lambda: None)
    episodes: Optional[List[SpecialStoryEpisode]] = Factory(lambda: None)


@define
class Config:
    config_key: Optional[str] = Factory(lambda: None)
    value: Optional[str] = Factory(lambda: None)


@define
class ClientConfig:
    id: Optional[int] = Factory(lambda: None)
    value: Optional[str] = Factory(lambda: None)
    type: Optional[Union[ClientConfigType, Unknown]] = Factory(lambda: None)


@define
class Wording:
    wording_key: Optional[str] = Factory(lambda: None)
    value: Optional[str] = Factory(lambda: None)


@define
class Costume3d:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    costume3d_group_id: Optional[int] = Factory(lambda: None)
    costume3d_type: Optional[Union[Costume3dType, Unknown]] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    part_type: Optional[Union[PartType, Unknown]] = Factory(lambda: None)
    color_id: Optional[int] = Factory(lambda: None)
    color_name: Optional[str] = Factory(lambda: None)
    character_id: Optional[int] = Factory(lambda: None)
    costume3d_rarity: Optional[Union[Costume3dRarity, Unknown]] = Factory(lambda: None)
    how_to_obtain: Optional[str] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    designer: Optional[str] = Factory(lambda: None)
    archive_display_type: Optional[Union[ArchiveDisplayType, Unknown]] = Factory(
        lambda: None
    )
    archive_published_at: Optional[datetime] = Factory(lambda: None)
    published_at: Optional[datetime] = Factory(lambda: None)


@define
class Costume3dModel:
    id: Optional[int] = Factory(lambda: None)
    costume3d_id: Optional[int] = Factory(lambda: None)
    unit: Optional[Union[Unit, Unknown]] = Factory(lambda: None)
    head_costume3d_asset_bundle_type: Optional[
        Union[HeadCostume3dAssetBundleType, Unknown]
    ] = Factory(lambda: None)
    thumbnail_asset_bundle_name: Optional[str] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    color_asset_bundle_name: Optional[str] = Factory(lambda: None)
    part: Optional[str] = Factory(lambda: None)


@define
class Costume3dModelAvailablePattern:
    id: Optional[int] = Factory(lambda: None)
    head_costume3d_id: Optional[int] = Factory(lambda: None)
    hair_costume3d_id: Optional[int] = Factory(lambda: None)
    unit: Optional[Union[Unit, Unknown]] = Factory(lambda: None)
    is_default: Optional[bool] = Factory(lambda: None)


@define
class GameCharacterUnit3dMotion:
    id: Optional[int] = Factory(lambda: None)
    game_character_unit_id: Optional[int] = Factory(lambda: None)
    motion_type: Optional[Union[MotionType, Unknown]] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)


@define
class Costume2d:
    id: Optional[int] = Factory(lambda: None)
    costume2d_group_id: Optional[int] = Factory(lambda: None)
    character2d_id: Optional[int] = Factory(lambda: None)
    from_mmddhh: Optional[str] = Factory(lambda: None)
    to_mmddhh: Optional[str] = Factory(lambda: None)
    live2d_asset_bundle_name: Optional[str] = Factory(lambda: None)
    spine_asset_bundle_name: Optional[str] = Factory(lambda: None)


@define
class Costume2dGroup:
    id: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)


@define
class Topic:
    id: Optional[int] = Factory(lambda: None)
    topic_type: Optional[Union[TopicType, Unknown]] = Factory(lambda: None)
    topic_type_id: Optional[int] = Factory(lambda: None)
    release_condition_id: Optional[int] = Factory(lambda: None)


@define
class LiveStage:
    id: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)


@define
class Stamp:
    id: Optional[int] = Factory(lambda: None)
    stamp_type: Optional[Union[StampType, Unknown]] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    balloon_asset_bundle_name: Optional[str] = Factory(lambda: None)
    character_id1: Optional[int] = Factory(lambda: None)
    game_character_unit_id: Optional[int] = Factory(lambda: None)
    archive_published_at: Optional[datetime] = Factory(lambda: None)
    description: Optional[str] = Factory(lambda: None)
    archive_display_type: Optional[Union[ArchiveDisplayType, Unknown]] = Factory(
        lambda: None
    )


@define
class MultiLiveLobby:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    photon_lobby_name: Optional[str] = Factory(lambda: None)
    matching_logic: Optional[Union[MatchingLogic, Unknown]] = Factory(lambda: None)
    total_power: Optional[int] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    multi_live_lobby_type: Optional[Union[MultiLiveLobbyType, Unknown]] = Factory(
        lambda: None
    )


@define
class MasterLessonCost(Cost):
    id: Optional[int] = Factory(lambda: None)
    card_rarity_type: Optional[Union[CardRarityType, Unknown]] = Factory(lambda: None)
    master_rank: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)


@define
class MasterLesson:
    card_rarity_type: Optional[Union[CardRarityType, Unknown]] = Factory(lambda: None)
    master_rank: Optional[int] = Factory(lambda: None)
    power1_bonus_fixed: Optional[int] = Factory(lambda: None)
    power2_bonus_fixed: Optional[int] = Factory(lambda: None)
    power3_bonus_fixed: Optional[int] = Factory(lambda: None)
    character_rank_exp: Optional[int] = Factory(lambda: None)
    costs: Optional[List[MasterLessonCost]] = Factory(lambda: None)
    rewards: Optional[List[Union[dict, str, int]]] = Factory(lambda: None)


@define
class MasterLessonReward:
    id: Optional[int] = Factory(lambda: None)
    card_id: Optional[int] = Factory(lambda: None)
    master_rank: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    resource_box_id: Optional[int] = Factory(lambda: None)
    card_rarity: Optional[int] = Factory(lambda: None)


@define
class CardExchangeResource:
    card_rarity_type: Optional[Union[CardRarityType, Unknown]] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    resource_box_id: Optional[int] = Factory(lambda: None)


@define
class MaterialExchangeCost(Cost):
    material_exchange_id: Optional[int] = Factory(lambda: None)
    cost_group_id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)


@define
class MaterialExchange:
    id: Optional[int] = Factory(lambda: None)
    material_exchange_summary_id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    resource_box_id: Optional[int] = Factory(lambda: None)
    refresh_cycle: Optional[Union[RefreshCycle, Unknown]] = Factory(lambda: None)
    costs: Optional[List[MaterialExchangeCost]] = Factory(lambda: None)
    exchange_limit: Optional[int] = Factory(lambda: None)
    start_at: Optional[datetime] = Factory(lambda: None)


@define
class MaterialExchangeSummary:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    exchange_category: Optional[Union[ExchangeCategory, Unknown]] = Factory(
        lambda: None
    )
    material_exchange_type: Optional[Union[MaterialExchangeType, Unknown]] = Factory(
        lambda: None
    )
    name: Optional[str] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    start_at: Optional[datetime] = Factory(lambda: None)
    material_exchanges: Optional[List[MaterialExchange]] = Factory(lambda: None)
    end_at: Optional[datetime] = Factory(lambda: None)
    notification_remain_hour: Optional[int] = Factory(lambda: None)


@define
class BoostItem:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    recovery_value: Optional[int] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    flavor_text: Optional[str] = Factory(lambda: None)


@define
class BillingProduct:
    id: Optional[int] = Factory(lambda: None)
    group_id: Optional[int] = Factory(lambda: None)
    platform: Optional[Platform] = Factory(lambda: None)
    product_id: Optional[str] = Factory(lambda: None)
    price: Optional[int] = Factory(lambda: None)
    unit_price: Optional[float] = Factory(lambda: None)


@define
class BillingShopItem:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    billing_shop_item_type: Optional[Union[BillingShopItemType, Unknown]] = Factory(
        lambda: None
    )
    billing_product_group_id: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    description: Optional[str] = Factory(lambda: None)
    billable_limit_type: Optional[Union[BillableLimitType, Unknown]] = Factory(
        lambda: None
    )
    billable_limit_reset_interval_type: Optional[
        Union[BillableLimitResetIntervalType, Unknown]
    ] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    resource_box_id: Optional[int] = Factory(lambda: None)
    billable_limit_value: Optional[int] = Factory(lambda: None)
    bonus_resource_box_id: Optional[int] = Factory(lambda: None)
    label: Optional[str] = Factory(lambda: None)
    end_at: Optional[datetime] = Factory(lambda: None)
    start_at: Optional[datetime] = Factory(lambda: None)
    billable_limit_reset_interval_value: Optional[int] = Factory(lambda: None)
    purchase_option: Optional[Union[PurchaseOption, Unknown]] = Factory(lambda: None)


@define
class BillingShopItemExchangeCost(Cost):
    id: Optional[int] = Factory(lambda: None)
    billing_shop_item_id: Optional[int] = Factory(lambda: None)


@define
class ColorfulPass:
    id: Optional[int] = Factory(lambda: None)
    resource_box_id: Optional[int] = Factory(lambda: None)
    receivable_days: Optional[int] = Factory(lambda: None)
    present_sentence: Optional[str] = Factory(lambda: None)
    expire_days: Optional[int] = Factory(lambda: None)
    daily_paid_gacha_spin_limit: Optional[int] = Factory(lambda: None)
    challenge_live_point_multiple: Optional[int] = Factory(lambda: None)
    live_point_multiple: Optional[int] = Factory(lambda: None)


@define
class JewelBehavior:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    jewel_behavior_type: Optional[Union[JewelBehaviorType, Unknown]] = Factory(
        lambda: None
    )
    jewel_behavior_type_quantity: Optional[int] = Factory(lambda: None)
    amount: Optional[int] = Factory(lambda: None)


@define
class CharacterRankAchieveResource:
    release_condition_id: Optional[int] = Factory(lambda: None)
    character_id: Optional[int] = Factory(lambda: None)
    character_rank: Optional[int] = Factory(lambda: None)
    resources: Optional[List[Union[dict, str, int]]] = Factory(lambda: None)


@define
class CharacterRank:
    id: Optional[int] = Factory(lambda: None)
    character_id: Optional[int] = Factory(lambda: None)
    character_rank: Optional[int] = Factory(lambda: None)
    power1_bonus_rate: Optional[float] = Factory(lambda: None)
    power2_bonus_rate: Optional[float] = Factory(lambda: None)
    power3_bonus_rate: Optional[float] = Factory(lambda: None)
    reward_resource_box_ids: Optional[List[int]] = Factory(lambda: None)
    character_rank_achieve_resources: Optional[
        List[CharacterRankAchieveResource]
    ] = Factory(lambda: None)


@define
class CharacterMissionV2:
    id: Optional[int] = Factory(lambda: None)
    character_mission_type: Optional[Union[CharacterMissionType, Unknown]] = Factory(
        lambda: None
    )
    character_id: Optional[int] = Factory(lambda: None)
    parameter_group_id: Optional[int] = Factory(lambda: None)
    sentence: Optional[str] = Factory(lambda: None)
    progress_sentence: Optional[str] = Factory(lambda: None)
    is_achievement_mission: Optional[bool] = Factory(lambda: None)


@define
class CharacterMissionV2ParameterGroup:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    requirement: Optional[int] = Factory(lambda: None)
    exp: Optional[int] = Factory(lambda: None)


@define
class CharacterMissionV2AreaItem:
    id: Optional[int] = Factory(lambda: None)
    character_mission_type: Optional[Union[CharacterMissionType, Unknown]] = Factory(
        lambda: None
    )
    area_item_id: Optional[int] = Factory(lambda: None)
    character_id: Optional[int] = Factory(lambda: None)
    unit: Optional[Union[Unit, Unknown]] = Factory(lambda: None)


@define
class SystemLive2d(Live2d):
    serif: Optional[str] = Factory(lambda: None)
    voice: Optional[str] = Factory(lambda: None)
    published_at: Optional[datetime] = Factory(lambda: None)
    closed_at: Optional[datetime] = Factory(lambda: None)
    special_season_id: Optional[int] = Factory(lambda: None)


@define
class Reward:
    id: Optional[int] = Factory(lambda: None)
    mission_type: Optional[Union[MissionType, Unknown]] = Factory(lambda: None)
    mission_id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    resource_box_id: Optional[int] = Factory(lambda: None)


@define
class NormalMission:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    normal_mission_type: Optional[Union[NormalMissionType, Unknown]] = Factory(
        lambda: None
    )
    requirement: Optional[int] = Factory(lambda: None)
    sentence: Optional[str] = Factory(lambda: None)
    rewards: Optional[List[Reward]] = Factory(lambda: None)


@define
class BeginnerMission:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    beginner_mission_type: Optional[Union[BeginnerMissionType, Unknown]] = Factory(
        lambda: None
    )
    beginner_mission_category: Optional[
        Union[BeginnerMissionCategory, Unknown]
    ] = Factory(lambda: None)
    requirement: Optional[int] = Factory(lambda: None)
    sentence: Optional[str] = Factory(lambda: None)
    rewards: Optional[List[Reward]] = Factory(lambda: None)


@define
class Detail:
    resource_box_purpose: Optional[Union[ResourceBoxPurpose, Unknown]] = Factory(
        lambda: None
    )
    resource_box_id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    resource_type: Optional[Union[ResourceType, Unknown]] = Factory(lambda: None)
    resource_quantity: Optional[int] = Factory(lambda: None)
    resource_id: Optional[int] = Factory(lambda: None)
    resource_level: Optional[int] = Factory(lambda: None)


@define
class ResourceBox:
    resource_box_purpose: Optional[Union[ResourceBoxPurpose, Unknown]] = Factory(
        lambda: None
    )
    id: Optional[int] = Factory(lambda: None)
    resource_box_type: Optional[Union[ResourceBoxType, Unknown]] = Factory(lambda: None)
    details: Optional[List[Detail]] = Factory(lambda: None)
    description: Optional[str] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)


@define
class LiveMissionPeriod:
    id: Optional[int] = Factory(lambda: None)
    start_at: Optional[datetime] = Factory(lambda: None)
    end_at: Optional[datetime] = Factory(lambda: None)
    sentence: Optional[str] = Factory(lambda: None)


@define
class LiveMission:
    id: Optional[int] = Factory(lambda: None)
    live_mission_period_id: Optional[int] = Factory(lambda: None)
    live_mission_type: Optional[Union[LiveMissionType, Unknown]] = Factory(lambda: None)
    requirement: Optional[int] = Factory(lambda: None)
    rewards: Optional[List[Reward]] = Factory(lambda: None)


@define
class LiveMissionPass:
    id: Optional[int] = Factory(lambda: None)
    live_mission_period_id: Optional[int] = Factory(lambda: None)
    costume_name: Optional[str] = Factory(lambda: None)
    character3d_id1: Optional[int] = Factory(lambda: None)
    character3d_id2: Optional[int] = Factory(lambda: None)
    male_asset_bundle_name: Optional[str] = Factory(lambda: None)
    female_asset_bundle_name: Optional[str] = Factory(lambda: None)


@define
class PenlightColor:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    description: Optional[str] = Factory(lambda: None)
    color_code: Optional[str] = Factory(lambda: None)
    character_id: Optional[int] = Factory(lambda: None)
    unit: Optional[Union[Unit, Unknown]] = Factory(lambda: None)


@define
class Penlight:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    default_penlight_color_id: Optional[int] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)


@define
class LiveTalk:
    id: Optional[int] = Factory(lambda: None)
    live_talk_type: Optional[Union[LiveTalkType, Unknown]] = Factory(lambda: None)
    scenario_id: Optional[str] = Factory(lambda: None)
    character_id1: Optional[int] = Factory(lambda: None)
    character_id2: Optional[int] = Factory(lambda: None)


@define
class Tip:
    id: Optional[int] = Factory(lambda: None)
    title: Optional[str] = Factory(lambda: None)
    description: Optional[str] = Factory(lambda: None)
    from_user_rank: Optional[int] = Factory(lambda: None)
    to_user_rank: Optional[int] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)


@define
class GachaCeilItem:
    id: Optional[int] = Factory(lambda: None)
    gacha_id: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    convert_start_at: Optional[datetime] = Factory(lambda: None)
    convert_resource_box_id: Optional[int] = Factory(lambda: None)


@define
class GachaCeilExchangeCost(Cost):
    gacha_ceil_exchange_id: Optional[int] = Factory(lambda: None)
    gacha_ceil_item_id: Optional[int] = Factory(lambda: None)


@define
class GachaCeilExchangeSubstituteCost(Cost):
    id: Optional[int] = Factory(lambda: None)
    substitute_quantity: Optional[int] = Factory(lambda: None)


@define
class GachaCeilExchange:
    id: Optional[int] = Factory(lambda: None)
    gacha_ceil_exchange_summary_id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    resource_box_id: Optional[int] = Factory(lambda: None)
    start_at: Optional[datetime] = Factory(lambda: None)
    end_at: Optional[datetime] = Factory(lambda: None)
    gacha_ceil_exchange_cost: Optional[GachaCeilExchangeCost] = Factory(lambda: None)
    gacha_ceil_exchange_substitute_costs: Optional[
        List[GachaCeilExchangeSubstituteCost]
    ] = Factory(lambda: None)
    exchange_limit: Optional[int] = Factory(lambda: None)
    gacha_ceil_exchange_label_type: Optional[
        Union[GachaCeilExchangeLabelType, Unknown]
    ] = Factory(lambda: None)
    substitute_limit: Optional[int] = Factory(lambda: None)


@define
class GachaCeilExchangeSummary:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    gacha_id: Optional[int] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    start_at: Optional[datetime] = Factory(lambda: None)
    end_at: Optional[datetime] = Factory(lambda: None)
    gacha_ceil_exchanges: Optional[List[GachaCeilExchange]] = Factory(lambda: None)
    gacha_ceil_item_id: Optional[int] = Factory(lambda: None)


@define
class PlayerRankReward:
    id: Optional[int] = Factory(lambda: None)
    player_rank: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    resource_box_id: Optional[int] = Factory(lambda: None)


@define
class GachaTicket:
    id: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)


@define
class HonorGroup:
    id: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    honor_type: Optional[Union[HonorType, Unknown]] = Factory(lambda: None)
    archive_published_at: Optional[datetime] = Factory(lambda: None)
    background_asset_bundle_name: Optional[str] = Factory(lambda: None)


@define
class HonorLevel:
    honor_id: Optional[int] = Factory(lambda: None)
    level: Optional[int] = Factory(lambda: None)
    bonus: Optional[int] = Factory(lambda: None)
    description: Optional[str] = Factory(lambda: None)


@define
class Honor:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    group_id: Optional[int] = Factory(lambda: None)
    honor_rarity: Optional[Union[HonorRarity, Unknown]] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    levels: Optional[List[HonorLevel]] = Factory(lambda: None)
    honor_type_id: Optional[int] = Factory(lambda: None)


@define
class HonorMission:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    honor_mission_type: Optional[Union[HonorMissionType, Unknown]] = Factory(
        lambda: None
    )
    requirement: Optional[int] = Factory(lambda: None)
    sentence: Optional[str] = Factory(lambda: None)
    rewards: Optional[List[Reward]] = Factory(lambda: None)


@define
class BondsHonorLevel:
    id: Optional[int] = Factory(lambda: None)
    bonds_honor_id: Optional[int] = Factory(lambda: None)
    level: Optional[int] = Factory(lambda: None)
    description: Optional[str] = Factory(lambda: None)


@define
class BondsHonor:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    bonds_group_id: Optional[int] = Factory(lambda: None)
    game_character_unit_id1: Optional[int] = Factory(lambda: None)
    game_character_unit_id2: Optional[int] = Factory(lambda: None)
    honor_rarity: Optional[Union[HonorRarity, Unknown]] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    description: Optional[str] = Factory(lambda: None)
    levels: Optional[List[BondsHonorLevel]] = Factory(lambda: None)
    configurable_unit_virtual_singer: Optional[bool] = Factory(lambda: None)


@define
class BondsHonorWord:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    bonds_group_id: Optional[int] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    description: Optional[str] = Factory(lambda: None)


@define
class BondsReward:
    id: Optional[int] = Factory(lambda: None)
    bonds_group_id: Optional[int] = Factory(lambda: None)
    rank: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    bonds_reward_type: Optional[Union[BondsRewardType, Unknown]] = Factory(lambda: None)
    resource_box_id: Optional[int] = Factory(lambda: None)
    description: Optional[str] = Factory(lambda: None)


@define
class ChallengeLiveDetail:
    id: Optional[int] = Factory(lambda: None)
    challenge_live_id: Optional[int] = Factory(lambda: None)
    challenge_live_type: Optional[Union[LiveType, Unknown]] = Factory(lambda: None)


@define
class ChallengeLive:
    id: Optional[int] = Factory(lambda: None)
    playable_count: Optional[int] = Factory(lambda: None)
    challenge_live_details: Optional[List[ChallengeLiveDetail]] = Factory(lambda: None)


@define
class ChallengeLiveDeck:
    id: Optional[int] = Factory(lambda: None)
    character_id: Optional[int] = Factory(lambda: None)
    release_condition_id: Optional[int] = Factory(lambda: None)
    card_limit: Optional[int] = Factory(lambda: None)


@define
class ChallengeLiveStage:
    id: Optional[int] = Factory(lambda: None)
    character_id: Optional[int] = Factory(lambda: None)
    rank: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    next_stage_challenge_point: Optional[int] = Factory(lambda: None)
    complete_stage_resource_box_id: Optional[int] = Factory(lambda: None)
    complete_stage_character_exp: Optional[int] = Factory(lambda: None)


@define
class ChallengeLiveStageEx:
    id: Optional[int] = Factory(lambda: None)
    character_id: Optional[int] = Factory(lambda: None)
    from_rank: Optional[int] = Factory(lambda: None)
    to_rank: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    next_stage_challenge_point: Optional[int] = Factory(lambda: None)
    complete_stage_resource_box_id: Optional[int] = Factory(lambda: None)
    complete_stage_character_exp: Optional[int] = Factory(lambda: None)


@define
class ChallengeLiveHighScoreReward:
    id: Optional[int] = Factory(lambda: None)
    character_id: Optional[int] = Factory(lambda: None)
    high_score: Optional[int] = Factory(lambda: None)
    resource_box_id: Optional[int] = Factory(lambda: None)


@define
class ChallengeLiveCharacter:
    id: Optional[int] = Factory(lambda: None)
    character_id: Optional[int] = Factory(lambda: None)
    release_condition_id: Optional[int] = Factory(lambda: None)
    or_release_condition_id: Optional[int] = Factory(lambda: None)


@define
class ChallengeLivePlayDayReward:
    id: Optional[int] = Factory(lambda: None)
    challenge_live_play_day_reward_period_id: Optional[int] = Factory(lambda: None)
    play_days: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    resource_box_id: Optional[int] = Factory(lambda: None)


@define
class ChallengeLivePlayDayRewardPeriod:
    id: Optional[int] = Factory(lambda: None)
    start_at: Optional[datetime] = Factory(lambda: None)
    end_at: Optional[datetime] = Factory(lambda: None)
    priority: Optional[int] = Factory(lambda: None)
    challenge_live_play_day_rewards: Optional[
        List[ChallengeLivePlayDayReward]
    ] = Factory(lambda: None)


@define
class VirtualLiveSetlist:
    id: Optional[int] = Factory(lambda: None)
    virtual_live_id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    virtual_live_setlist_type: Optional[
        Union[VirtualLiveSetlistType, Unknown]
    ] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    virtual_live_stage_id: Optional[int] = Factory(lambda: None)
    music_id: Optional[int] = Factory(lambda: None)
    music_vocal_id: Optional[int] = Factory(lambda: None)
    character3d_id1: Optional[int] = Factory(lambda: None)
    character3d_id2: Optional[int] = Factory(lambda: None)
    character3d_id3: Optional[int] = Factory(lambda: None)
    character3d_id4: Optional[int] = Factory(lambda: None)
    character3d_id5: Optional[int] = Factory(lambda: None)
    character3d_id6: Optional[int] = Factory(lambda: None)


@define
class VirtualLiveBeginnerSchedule:
    id: Optional[int] = Factory(lambda: None)
    virtual_live_id: Optional[int] = Factory(lambda: None)
    day_of_week: Optional[Union[DayOfWeek, Unknown]] = Factory(lambda: None)
    start_time: Optional[str] = Factory(lambda: None)
    end_time: Optional[str] = Factory(lambda: None)


@define
class VirtualLiveSchedule:
    id: Optional[int] = Factory(lambda: None)
    virtual_live_id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    start_at: Optional[datetime] = Factory(lambda: None)
    end_at: Optional[datetime] = Factory(lambda: None)
    notice_group_id: Optional[str] = Factory(lambda: None)


@define
class VirtualLiveCharacter:
    id: Optional[int] = Factory(lambda: None)
    virtual_live_id: Optional[int] = Factory(lambda: None)
    game_character_unit_id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)


@define
class VirtualLiveReward:
    id: Optional[int] = Factory(lambda: None)
    virtual_live_type: Optional[Union[VirtualLiveType, Unknown]] = Factory(lambda: None)
    virtual_live_id: Optional[int] = Factory(lambda: None)
    resource_box_id: Optional[int] = Factory(lambda: None)


@define
class VirtualLiveWaitingRoom:
    id: Optional[int] = Factory(lambda: None)
    virtual_live_id: Optional[int] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    start_at: Optional[datetime] = Factory(lambda: None)
    end_at: Optional[datetime] = Factory(lambda: None)
    lobby_asset_bundle_name: Optional[str] = Factory(lambda: None)


@define
class VirtualItem:
    id: Optional[int] = Factory(lambda: None)
    virtual_item_category: Optional[Union[VirtualItemCategory, Unknown]] = Factory(
        lambda: None
    )
    seq: Optional[int] = Factory(lambda: None)
    priority: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    cost_virtual_coin: Optional[int] = Factory(lambda: None)
    cost_jewel: Optional[int] = Factory(lambda: None)
    cheer_point: Optional[int] = Factory(lambda: None)
    effect_asset_bundle_name: Optional[str] = Factory(lambda: None)
    effect_expression_type: Optional[Union[EffectExpressionType, Unknown]] = Factory(
        lambda: None
    )
    unit: Optional[Union[Unit, Unknown]] = Factory(lambda: None)
    game_character_unit_id: Optional[int] = Factory(lambda: None)
    virtual_item_label_type: Optional[Union[VirtualItemLabelType, Unknown]] = Factory(
        lambda: None
    )


@define
class VirtualLiveAppeal:
    id: Optional[int] = Factory(lambda: None)
    virtual_live_id: Optional[int] = Factory(lambda: None)
    virtual_live_stage_status: Optional[
        Union[VirtualLiveStageStatus, Unknown]
    ] = Factory(lambda: None)
    appeal_text: Optional[str] = Factory(lambda: None)


@define
class VirtualLiveInformation:
    virtual_live_id: Optional[int] = Factory(lambda: None)
    summary: Optional[str] = Factory(lambda: None)
    description: Optional[str] = Factory(lambda: None)


@define
class VirtualLive:
    id: Optional[int] = Factory(lambda: None)
    virtual_live_type: Optional[Union[VirtualLiveType, Unknown]] = Factory(lambda: None)
    virtual_live_platform: Optional[str] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    screen_mv_music_vocal_id: Optional[int] = Factory(lambda: None)
    start_at: Optional[datetime] = Factory(lambda: None)
    end_at: Optional[datetime] = Factory(lambda: None)
    ranking_announce_at: Optional[datetime] = Factory(lambda: None)
    virtual_live_setlists: Optional[List[VirtualLiveSetlist]] = Factory(lambda: None)
    virtual_live_beginner_schedules: Optional[
        List[VirtualLiveBeginnerSchedule]
    ] = Factory(lambda: None)
    virtual_live_schedules: Optional[List[VirtualLiveSchedule]] = Factory(lambda: None)
    virtual_live_characters: Optional[List[VirtualLiveCharacter]] = Factory(
        lambda: None
    )
    virtual_live_reward: Optional[VirtualLiveReward] = Factory(lambda: None)
    virtual_live_rewards: Optional[List[VirtualLiveReward]] = Factory(lambda: None)
    virtual_live_cheer_point_rewards: Optional[List[Union[dict, str, int]]] = Factory(
        lambda: None
    )
    virtual_live_waiting_room: Optional[VirtualLiveWaitingRoom] = Factory(lambda: None)
    virtual_items: Optional[List[VirtualItem]] = Factory(lambda: None)
    virtual_live_appeals: Optional[List[VirtualLiveAppeal]] = Factory(lambda: None)
    virtual_live_information: Optional[VirtualLiveInformation] = Factory(lambda: None)
    archive_release_condition_id: Optional[int] = Factory(lambda: None)
    virtual_live_ticket_id: Optional[int] = Factory(lambda: None)


@define
class VirtualShopItem:
    id: Optional[int] = Factory(lambda: None)
    virtual_shop_id: Optional[int] = Factory(lambda: None)
    virtual_shop_item_type: Optional[Union[VirtualShopItemType, Unknown]] = Factory(
        lambda: None
    )
    seq: Optional[int] = Factory(lambda: None)
    resource_box_id: Optional[int] = Factory(lambda: None)
    cost_virtual_coin: Optional[int] = Factory(lambda: None)
    cost_jewel: Optional[int] = Factory(lambda: None)
    start_at: Optional[datetime] = Factory(lambda: None)
    cost_paid_jewel: Optional[int] = Factory(lambda: None)
    end_at: Optional[datetime] = Factory(lambda: None)
    limit_value: Optional[int] = Factory(lambda: None)


@define
class VirtualShop:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    virtual_shop_items: Optional[List[VirtualShopItem]] = Factory(lambda: None)
    virtual_shop_type: Optional[Union[VirtualShopType, Unknown]] = Factory(lambda: None)
    virtual_live_id: Optional[int] = Factory(lambda: None)


@define
class VirtualLiveCheerMessage:
    id: Optional[int] = Factory(lambda: None)
    virtual_live_type: Optional[Union[VirtualLiveType, Unknown]] = Factory(lambda: None)
    resource_type: Optional[Union[ResourceType, Unknown]] = Factory(lambda: None)
    from_cost_virtual_coin: Optional[int] = Factory(lambda: None)
    to_cost_virtual_coin: Optional[int] = Factory(lambda: None)
    from_cost: Optional[int] = Factory(lambda: None)
    to_cost: Optional[int] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    message_length_limit: Optional[int] = Factory(lambda: None)
    display_sec: Optional[float] = Factory(lambda: None)
    message_size: Optional[str] = Factory(lambda: None)
    color_code: Optional[str] = Factory(lambda: None)
    virtual_live_cheer_message_display_limit_id: Optional[int] = Factory(lambda: None)


@define
class VirtualLiveCheerMessageDisplayLimit:
    id: Optional[int] = Factory(lambda: None)
    display_limit: Optional[int] = Factory(lambda: None)


@define
class VirtualLiveTicket:
    id: Optional[int] = Factory(lambda: None)
    virtual_live_id: Optional[int] = Factory(lambda: None)
    virtual_live_ticket_type: Optional[Union[VirtualLiveTicketType, Unknown]] = Factory(
        lambda: None
    )
    name: Optional[str] = Factory(lambda: None)
    flavor_text: Optional[str] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)


@define
class VirtualLivePamphlet:
    id: Optional[int] = Factory(lambda: None)
    virtual_live_id: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    flavor_text: Optional[str] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)


@define
class AvatarAccessory:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    part: Optional[Union[AccessoryPart, Unknown]] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)


@define
class AvatarCostume:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)


@define
class AvatarMotion:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    sync_music_flg: Optional[bool] = Factory(lambda: None)
    repeat_count: Optional[int] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)


@define
class AvatarSkinColor:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    color_code: Optional[str] = Factory(lambda: None)


@define
class AvatarCoordinate:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    skin_color_code: Optional[str] = Factory(lambda: None)
    costume_asset_bundle_name: Optional[str] = Factory(lambda: None)
    accessory_part: Optional[Union[AccessoryPart, Unknown]] = Factory(lambda: None)
    accessory_asset_bundle_name: Optional[str] = Factory(lambda: None)


@define
class NgWord:
    id: Optional[int] = Factory(lambda: None)
    word: Optional[str] = Factory(lambda: None)


@define
class RuleSlide:
    id: Optional[int] = Factory(lambda: None)
    rule_slide_type: Optional[Union[RuleSlideType, Unknown]] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)


@define
class Facility:
    id: Optional[int] = Factory(lambda: None)
    facility_type: Optional[Union[FacilityType, Unknown]] = Factory(lambda: None)
    release_condition_id: Optional[int] = Factory(lambda: None)
    and_release_condition_id: Optional[int] = Factory(lambda: None)


@define
class OneTimeBehavior:
    id: Optional[int] = Factory(lambda: None)
    one_time_behavior_type: Optional[Union[OneTimeBehaviorType, Unknown]] = Factory(
        lambda: None
    )
    release_condition_id: Optional[int] = Factory(lambda: None)


@define
class LoginBonus:
    id: Optional[int] = Factory(lambda: None)
    day: Optional[int] = Factory(lambda: None)
    resource_box_id: Optional[int] = Factory(lambda: None)


@define
class BeginnerLoginBonus:
    id: Optional[int] = Factory(lambda: None)
    day: Optional[int] = Factory(lambda: None)
    resource_box_id: Optional[int] = Factory(lambda: None)
    login_bonus_id: Optional[int] = Factory(lambda: None)


@define
class BeginnerLoginBonusSummary:
    id: Optional[int] = Factory(lambda: None)
    login_bonus_id: Optional[int] = Factory(lambda: None)
    start_at: Optional[datetime] = Factory(lambda: None)
    end_at: Optional[datetime] = Factory(lambda: None)


@define
class LimitedLoginBonusDetail:
    id: Optional[int] = Factory(lambda: None)
    limited_login_bonus_id: Optional[int] = Factory(lambda: None)
    day: Optional[int] = Factory(lambda: None)
    resource_box_id: Optional[int] = Factory(lambda: None)


@define
class LimitedLoginBonus:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    start_at: Optional[datetime] = Factory(lambda: None)
    end_at: Optional[datetime] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    close_at: Optional[datetime] = Factory(lambda: None)
    limited_login_bonus_details: Optional[List[LimitedLoginBonusDetail]] = Factory(
        lambda: None
    )


@define
class LoginBonusLive2d(Live2d):
    serif: Optional[str] = Factory(lambda: None)
    voice: Optional[str] = Factory(lambda: None)
    published_at: Optional[datetime] = Factory(lambda: None)
    closed_at: Optional[datetime] = Factory(lambda: None)


@define
class EventRankingReward:
    id: Optional[int] = Factory(lambda: None)
    event_ranking_reward_range_id: Optional[int] = Factory(lambda: None)
    resource_box_id: Optional[int] = Factory(lambda: None)


@define
class EventRankingRewardRange:
    id: Optional[int] = Factory(lambda: None)
    event_id: Optional[int] = Factory(lambda: None)
    from_rank: Optional[int] = Factory(lambda: None)
    to_rank: Optional[int] = Factory(lambda: None)
    event_ranking_rewards: Optional[List[EventRankingReward]] = Factory(lambda: None)


@define
class Event:
    id: Optional[int] = Factory(lambda: None)
    event_type: Optional[Union[EventType, Unknown]] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    bgm_asset_bundle_name: Optional[str] = Factory(lambda: None)
    start_at: Optional[datetime] = Factory(lambda: None)
    aggregate_at: Optional[datetime] = Factory(lambda: None)
    ranking_announce_at: Optional[datetime] = Factory(lambda: None)
    distribution_start_at: Optional[datetime] = Factory(lambda: None)
    closed_at: Optional[datetime] = Factory(lambda: None)
    distribution_end_at: Optional[datetime] = Factory(lambda: None)
    virtual_live_id: Optional[int] = Factory(lambda: None)
    unit: Optional[Union[Unit, Unknown]] = Factory(lambda: None)
    event_ranking_reward_ranges: Optional[List[EventRankingRewardRange]] = Factory(
        lambda: None
    )
    event_point_asset_bundle_name: Optional[str] = Factory(lambda: None)


@define
class EventMusic:
    event_id: Optional[int] = Factory(lambda: None)
    music_id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    release_condition_id: Optional[int] = Factory(lambda: None)


@define
class EventDeckBonus:
    id: Optional[int] = Factory(lambda: None)
    event_id: Optional[int] = Factory(lambda: None)
    game_character_unit_id: Optional[int] = Factory(lambda: None)
    card_attr: Optional[Union[CardAttr, Unknown]] = Factory(lambda: None)
    bonus_rate: Optional[float] = Factory(lambda: None)


@define
class EventRarityBonusRate:
    id: Optional[int] = Factory(lambda: None)
    card_rarity_type: Optional[Union[CardRarityType, Unknown]] = Factory(lambda: None)
    master_rank: Optional[int] = Factory(lambda: None)
    bonus_rate: Optional[float] = Factory(lambda: None)


@define
class EventItem:
    id: Optional[int] = Factory(lambda: None)
    event_id: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    flavor_text: Optional[str] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)


@define
class EpisodeReward:
    story_type: Optional[Union[StoryType, Unknown]] = Factory(lambda: None)
    resource_box_id: Optional[int] = Factory(lambda: None)


@define
class EventStoryEpisode:
    id: Optional[int] = Factory(lambda: None)
    event_story_id: Optional[int] = Factory(lambda: None)
    episode_no: Optional[int] = Factory(lambda: None)
    title: Optional[str] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    scenario_id: Optional[str] = Factory(lambda: None)
    release_condition_id: Optional[int] = Factory(lambda: None)
    episode_rewards: Optional[List[EpisodeReward]] = Factory(lambda: None)


@define
class EventStory:
    id: Optional[int] = Factory(lambda: None)
    event_id: Optional[int] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    event_story_episodes: Optional[List[EventStoryEpisode]] = Factory(lambda: None)


@define
class EventExchangeCost(Cost):
    id: Optional[int] = Factory(lambda: None)
    event_exchange_id: Optional[int] = Factory(lambda: None)


@define
class EventExchange:
    id: Optional[int] = Factory(lambda: None)
    event_exchange_summary_id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    resource_box_id: Optional[int] = Factory(lambda: None)
    exchange_limit: Optional[int] = Factory(lambda: None)
    event_exchange_cost: Optional[EventExchangeCost] = Factory(lambda: None)


@define
class EventExchangeSummary:
    id: Optional[int] = Factory(lambda: None)
    event_id: Optional[int] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    start_at: Optional[datetime] = Factory(lambda: None)
    end_at: Optional[datetime] = Factory(lambda: None)
    event_exchanges: Optional[List[EventExchange]] = Factory(lambda: None)


@define
class EventStoryUnit:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    event_story_id: Optional[int] = Factory(lambda: None)
    unit: Optional[Union[Unit, Unknown]] = Factory(lambda: None)
    event_story_unit_relation: Optional[
        Union[EventStoryUnitRelation, Unknown]
    ] = Factory(lambda: None)


@define
class EventCard:
    id: Optional[int] = Factory(lambda: None)
    card_id: Optional[int] = Factory(lambda: None)
    event_id: Optional[int] = Factory(lambda: None)
    bonus_rate: Optional[float] = Factory(lambda: None)


@define
class PreliminaryTournamentCard:
    id: Optional[int] = Factory(lambda: None)
    preliminary_tournament_id: Optional[int] = Factory(lambda: None)
    card_id: Optional[int] = Factory(lambda: None)


@define
class PreliminaryTournamentMusic:
    id: Optional[int] = Factory(lambda: None)
    preliminary_tournament_id: Optional[int] = Factory(lambda: None)
    music_difficulty_id: Optional[int] = Factory(lambda: None)
    music_id: Optional[int] = Factory(lambda: None)


@define
class PreliminaryTournament:
    id: Optional[int] = Factory(lambda: None)
    preliminary_tournament_type: Optional[
        Union[PreliminaryTournamentType, Unknown]
    ] = Factory(lambda: None)
    start_at: Optional[datetime] = Factory(lambda: None)
    end_at: Optional[datetime] = Factory(lambda: None)
    release_condition_id: Optional[int] = Factory(lambda: None)
    preliminary_tournament_cards: Optional[List[PreliminaryTournamentCard]] = Factory(
        lambda: None
    )
    preliminary_tournament_musics: Optional[List[PreliminaryTournamentMusic]] = Factory(
        lambda: None
    )


@define
class CheerfulCarnivalSummary:
    id: Optional[int] = Factory(lambda: None)
    event_id: Optional[int] = Factory(lambda: None)
    theme: Optional[str] = Factory(lambda: None)
    midterm_announce1_at: Optional[datetime] = Factory(lambda: None)
    midterm_announce2_at: Optional[datetime] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)


@define
class CheerfulCarnivalTeam:
    id: Optional[int] = Factory(lambda: None)
    event_id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    team_name: Optional[str] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)


@define
class CheerfulCarnivalPartyName:
    id: Optional[int] = Factory(lambda: None)
    party_name: Optional[str] = Factory(lambda: None)
    game_character_unit_id1: Optional[int] = Factory(lambda: None)
    game_character_unit_id2: Optional[int] = Factory(lambda: None)
    game_character_unit_id3: Optional[int] = Factory(lambda: None)
    game_character_unit_id4: Optional[int] = Factory(lambda: None)
    game_character_unit_id5: Optional[int] = Factory(lambda: None)


@define
class CheerfulCarnivalCharacterPartyName:
    id: Optional[int] = Factory(lambda: None)
    character_party_name: Optional[str] = Factory(lambda: None)
    game_character_unit_id: Optional[int] = Factory(lambda: None)


@define
class CheerfulCarnivalLiveTeamPointBonus:
    id: Optional[int] = Factory(lambda: None)
    team_point_bonus_rate: Optional[int] = Factory(lambda: None)


@define
class CheerfulCarnivalReward:
    id: Optional[int] = Factory(lambda: None)
    event_id: Optional[int] = Factory(lambda: None)
    cheerful_carnival_team_id: Optional[int] = Factory(lambda: None)
    resource_box_id: Optional[int] = Factory(lambda: None)


@define
class CheerfulCarnivalResultReward:
    id: Optional[int] = Factory(lambda: None)
    event_id: Optional[int] = Factory(lambda: None)
    cheerful_carnival_team_point_term_type: Optional[
        Union[CheerfulCarnivalTeamPointTermType, Unknown]
    ] = Factory(lambda: None)
    cheerful_carnival_result_type: Optional[
        Union[CheerfulCarnivalResultType, Unknown]
    ] = Factory(lambda: None)
    resource_box_id: Optional[int] = Factory(lambda: None)


@define
class Appeal:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    appeal_target_type: Optional[Union[AppealTargetType, Unknown]] = Factory(
        lambda: None
    )
    appeal_type: Optional[Union[AppealType, Unknown]] = Factory(lambda: None)
    start_at: Optional[datetime] = Factory(lambda: None)
    end_at: Optional[datetime] = Factory(lambda: None)
    appeal_read_condition_type: Optional[
        Union[AppealReadConditionType, Unknown]
    ] = Factory(lambda: None)
    text: Optional[str] = Factory(lambda: None)


@define
class Boost:
    id: Optional[int] = Factory(lambda: None)
    cost_boost: Optional[int] = Factory(lambda: None)
    is_event_only: Optional[bool] = Factory(lambda: None)
    exp_rate: Optional[int] = Factory(lambda: None)
    reward_rate: Optional[int] = Factory(lambda: None)
    live_point_rate: Optional[int] = Factory(lambda: None)
    event_point_rate: Optional[int] = Factory(lambda: None)
    bonds_exp_rate: Optional[int] = Factory(lambda: None)


@define
class BoostPresent:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    recovery_value: Optional[int] = Factory(lambda: None)
    present_limit: Optional[int] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    is_unlimited_receive: Optional[bool] = Factory(lambda: None)
    boost_present_cost_id: Optional[int] = Factory(lambda: None)


@define
class BoostPresentCost(Cost):
    id: Optional[int] = Factory(lambda: None)


@define
class EpisodeCharacter:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    character2d_id: Optional[int] = Factory(lambda: None)
    story_type: Optional[Union[StoryType, Unknown]] = Factory(lambda: None)
    episode_id: Optional[int] = Factory(lambda: None)


@define
class CustomProfileTextColor:
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    color_code: Optional[str] = Factory(lambda: None)


@define
class CustomProfileTextFont:
    id: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    font_name: Optional[str] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)


@define
class CustomProfileResource:
    custom_profile_resource_type: Optional[
        Union[CustomProfileResourceType, Unknown]
    ] = Factory(lambda: None)
    id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    resource_load_type: Optional[Union[ResourceLoadType, Unknown]] = Factory(
        lambda: None
    )
    resource_load_val: Optional[str] = Factory(lambda: None)
    file_name: Optional[str] = Factory(lambda: None)


@define
class CustomProfilePlayerInfoResource(CustomProfileResource):
    pass


@define
class CustomProfileGeneralBackgroundResource(CustomProfileResource):
    pass


@define
class CustomProfileStoryBackgroundResource(CustomProfileResource):
    pass


@define
class CustomProfileCollectionResource(CustomProfileResource):
    custom_profile_resource_collection_type: Optional[
        Union[CustomProfileResourceCollectionType, Unknown]
    ] = Factory(lambda: None)
    group_id: Optional[int] = Factory(lambda: None)


@define
class CustomProfileMemberStandingPictureResource(CustomProfileResource):
    character_id: Optional[int] = Factory(lambda: None)


@define
class CustomProfileShapeResource(CustomProfileResource):
    pass


@define
class CustomProfileEtcResource(CustomProfileResource):
    pass


@define
class CustomProfileGachaBehavior:
    id: Optional[int] = Factory(lambda: None)
    custom_profile_gacha_id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    cost_resource_type: Optional[Union[ResourceType, Unknown]] = Factory(lambda: None)
    cost_resource_quantity: Optional[int] = Factory(lambda: None)
    spin_count: Optional[int] = Factory(lambda: None)


@define
class CustomProfileGachaDetail:
    id: Optional[int] = Factory(lambda: None)
    custom_profile_gacha_id: Optional[int] = Factory(lambda: None)
    custom_profile_resource_type: Optional[
        Union[CustomProfileResourceType, Unknown]
    ] = Factory(lambda: None)
    custom_profile_resource_id: Optional[int] = Factory(lambda: None)
    custom_profile_resource_quantity: Optional[int] = Factory(lambda: None)
    weight: Optional[int] = Factory(lambda: None)


@define
class CustomProfileGacha:
    id: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    start_at: Optional[datetime] = Factory(lambda: None)
    end_at: Optional[datetime] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    description: Optional[str] = Factory(lambda: None)
    notice: Optional[str] = Factory(lambda: None)
    custom_profile_gacha_behaviors: Optional[
        List[CustomProfileGachaBehavior]
    ] = Factory(lambda: None)
    custom_profile_gacha_details: Optional[List[CustomProfileGachaDetail]] = Factory(
        lambda: None
    )


@define
class StreamingLiveBgm:
    id: Optional[int] = Factory(lambda: None)
    virtual_live_id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    music_vocal_id: Optional[int] = Factory(lambda: None)


@define
class Omikuji:
    id: Optional[int] = Factory(lambda: None)
    omikuji_group_id: Optional[int] = Factory(lambda: None)
    unit: Optional[Union[Unit, Unknown]] = Factory(lambda: None)
    fortune_type: Optional[Union[FortuneType, Unknown]] = Factory(lambda: None)
    summary: Optional[str] = Factory(lambda: None)
    title1: Optional[str] = Factory(lambda: None)
    description1: Optional[str] = Factory(lambda: None)
    title2: Optional[str] = Factory(lambda: None)
    description2: Optional[str] = Factory(lambda: None)
    title3: Optional[str] = Factory(lambda: None)
    description3: Optional[str] = Factory(lambda: None)
    unit_asset_bundle_name: Optional[str] = Factory(lambda: None)
    fortune_asset_bundle_name: Optional[str] = Factory(lambda: None)
    omikuji_cover_asset_bundle_name: Optional[str] = Factory(lambda: None)
    unit_file_path: Optional[str] = Factory(lambda: None)
    fortune_file_path: Optional[str] = Factory(lambda: None)
    omikuji_cover_file_path: Optional[str] = Factory(lambda: None)


@define
class OmikujiGroup:
    id: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    summary: Optional[str] = Factory(lambda: None)
    description: Optional[str] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    appeal_asset_bundle_name: Optional[str] = Factory(lambda: None)
    sound_asset_bundle_name: Optional[str] = Factory(lambda: None)


@define
class OmikujiRate:
    id: Optional[int] = Factory(lambda: None)
    omikuji_group_id: Optional[int] = Factory(lambda: None)
    fortune_type: Optional[Union[FortuneType, Unknown]] = Factory(lambda: None)
    rate: Optional[float] = Factory(lambda: None)


@define
class OmikujiCost(Cost):
    id: Optional[int] = Factory(lambda: None)
    omikuji_group_id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)


@define
class OmikujiReward:
    id: Optional[int] = Factory(lambda: None)
    omikuji_group_id: Optional[int] = Factory(lambda: None)
    seq: Optional[int] = Factory(lambda: None)
    resource_type: Optional[Union[ResourceType, Unknown]] = Factory(lambda: None)
    resource_id: Optional[int] = Factory(lambda: None)
    resource_quantity: Optional[int] = Factory(lambda: None)


@define
class VirtualBoothShop:
    id: Optional[int] = Factory(lambda: None)
    virtual_live_id: Optional[int] = Factory(lambda: None)
    virtual_booth_shop_type: Optional[Union[VirtualBoothShopType, Unknown]] = Factory(
        lambda: None
    )
    target_id: Optional[int] = Factory(lambda: None)


@define
class SpecialSeason:
    id: Optional[int] = Factory(lambda: None)
    special_season_type: Optional[Union[SpecialSeasonType, Unknown]] = Factory(
        lambda: None
    )
    start_at: Optional[datetime] = Factory(lambda: None)
    end_at: Optional[datetime] = Factory(lambda: None)
    priority: Optional[int] = Factory(lambda: None)


@define
class SpecialSeasonArea:
    id: Optional[int] = Factory(lambda: None)
    special_season_id: Optional[int] = Factory(lambda: None)
    area_id: Optional[int] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    file_name: Optional[str] = Factory(lambda: None)
    special_season_area_use_type: Optional[
        Union[SpecialSeasonAreaUseType, Unknown]
    ] = Factory(lambda: None)


@define
class RankMatchPenalty:
    id: Optional[int] = Factory(lambda: None)
    count: Optional[int] = Factory(lambda: None)
    rank_match_penalty_type: Optional[Union[RankMatchPenaltyType, Unknown]] = Factory(
        lambda: None
    )
    rank_match_penalty_type_value: Optional[int] = Factory(lambda: None)


@define
class RankMatchPlacement:
    id: Optional[int] = Factory(lambda: None)
    rank_match_placement_condition_type: Optional[str] = Factory(lambda: None)
    tier_behavior_type: Optional[Union[TierBehaviorType, Unknown]] = Factory(
        lambda: None
    )
    tier_behavior_type_value: Optional[int] = Factory(lambda: None)
    rank_match_placement_condition_type_value: Optional[int] = Factory(lambda: None)


@define
class RankMatchBonusPointCondition:
    id: Optional[int] = Factory(lambda: None)
    rank_match_bonus_point_condition_type: Optional[
        Union[RankMatchBonusPointConditionType, Unknown]
    ] = Factory(lambda: None)
    group_id: Optional[int] = Factory(lambda: None)
    priority: Optional[int] = Factory(lambda: None)
    calc_type: Optional[Union[CalcType, Unknown]] = Factory(lambda: None)
    bonus_point: Optional[int] = Factory(lambda: None)


@define
class RankMatchSeasonPlayableTime:
    id: Optional[int] = Factory(lambda: None)
    rank_match_season_id: Optional[int] = Factory(lambda: None)
    start_time: Optional[str] = Factory(lambda: None)
    end_time: Optional[str] = Factory(lambda: None)


@define
class RankMatchSeasonTierMusicPlayLevel:
    id: Optional[int] = Factory(lambda: None)
    rank_match_season_id: Optional[int] = Factory(lambda: None)
    rank_match_tier_id: Optional[int] = Factory(lambda: None)
    from_play_level: Optional[int] = Factory(lambda: None)
    to_play_level: Optional[int] = Factory(lambda: None)


@define
class RankMatchSeasonTierReward:
    id: Optional[int] = Factory(lambda: None)
    rank_match_season_id: Optional[int] = Factory(lambda: None)
    rank_match_tier_id: Optional[int] = Factory(lambda: None)
    resource_box_id: Optional[int] = Factory(lambda: None)


@define
class RankMatchSeason:
    id: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)
    start_at: Optional[datetime] = Factory(lambda: None)
    aggregated_at: Optional[datetime] = Factory(lambda: None)
    ranking_published_at: Optional[datetime] = Factory(lambda: None)
    batch_execution_at: Optional[datetime] = Factory(lambda: None)
    distribution_start_at: Optional[datetime] = Factory(lambda: None)
    distribution_end_at: Optional[datetime] = Factory(lambda: None)
    closed_at: Optional[datetime] = Factory(lambda: None)
    asset_bundle_name: Optional[str] = Factory(lambda: None)
    is_display_result: Optional[bool] = Factory(lambda: None)
    rank_match_season_playable_times: Optional[
        List[RankMatchSeasonPlayableTime]
    ] = Factory(lambda: None)
    rank_match_season_tier_music_play_levels: Optional[
        List[RankMatchSeasonTierMusicPlayLevel]
    ] = Factory(lambda: None)
    rank_match_season_tier_rewards: Optional[List[RankMatchSeasonTierReward]] = Factory(
        lambda: None
    )


@define
class RankMatchTier:
    id: Optional[int] = Factory(lambda: None)
    rank_match_grade_id: Optional[int] = Factory(lambda: None)
    rank_match_class_id: Optional[int] = Factory(lambda: None)
    tier: Optional[int] = Factory(lambda: None)
    total_music_difficulty: Optional[int] = Factory(lambda: None)
    point: Optional[int] = Factory(lambda: None)
    grade_asset_bundle_name: Optional[str] = Factory(lambda: None)
    tier_asset_bundle_name: Optional[str] = Factory(lambda: None)


@define
class RankMatchTierBonusPoint:
    id: Optional[int] = Factory(lambda: None)
    rank_match_tier_id: Optional[int] = Factory(lambda: None)
    max_bonus_point: Optional[int] = Factory(lambda: None)
    reward_point: Optional[int] = Factory(lambda: None)


@define
class RankMatchGrade(Costume2dGroup):
    id: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)


@define
class RankMatchClass(Costume2dGroup):
    id: Optional[int] = Factory(lambda: None)
    name: Optional[str] = Factory(lambda: None)


@define
class LimitedTitleScreen:
    id: Optional[int] = Factory(lambda: None)
    priority: Optional[int] = Factory(lambda: None)
    download_start_at: Optional[datetime] = Factory(lambda: None)
    download_end_at: Optional[datetime] = Factory(lambda: None)
    display_start_at: Optional[datetime] = Factory(lambda: None)
    display_end_at: Optional[datetime] = Factory(lambda: None)
    bg_asset_bundle_name: Optional[str] = Factory(lambda: None)
    logo_asset_bundle_name: Optional[str] = Factory(lambda: None)
    bgm_asset_bundle_name: Optional[str] = Factory(lambda: None)
    start_effect_asset_bundle_name: Optional[str] = Factory(lambda: None)


@define
class MasterData:
    game_characters: Optional[List[GameCharacter]] = Factory(lambda: None)
    game_character_units: Optional[List[GameCharacterUnit]] = Factory(lambda: None)
    outside_characters: Optional[List[OutsideCharacter]] = Factory(lambda: None)
    character3ds: Optional[List[Character3d]] = Factory(lambda: None)
    character2ds: Optional[List[Character2d]] = Factory(lambda: None)
    character_profiles: Optional[List[CharacterProfile]] = Factory(lambda: None)
    bonds: Optional[List[Bond]] = Factory(lambda: None)
    bonds_live2ds: Optional[List[BondsLive2d]] = Factory(lambda: None)
    bonds_rank_up_live2ds: Optional[List[BondsRankUpLive2d]] = Factory(lambda: None)
    unit_profiles: Optional[List[UnitProfile]] = Factory(lambda: None)
    action_sets: Optional[List[ActionSet]] = Factory(lambda: None)
    areas: Optional[List[Area]] = Factory(lambda: None)
    area_playlists: Optional[List[AreaPlaylist]] = Factory(lambda: None)
    mob_characters: Optional[List[MobCharacter]] = Factory(lambda: None)
    character_costumes: Optional[List[CharacterCostume]] = Factory(lambda: None)
    card_costume3ds: Optional[List[CardCostume3d]] = Factory(lambda: None)
    cards: Optional[List[Card]] = Factory(lambda: None)
    skills: Optional[List[Skill]] = Factory(lambda: None)
    card_episodes: Optional[List[CardEpisode]] = Factory(lambda: None)
    card_rarities: Optional[List[CardRarity]] = Factory(lambda: None)
    card_skill_costs: Optional[List[CardSkillCost]] = Factory(lambda: None)
    musics: Optional[List[Music]] = Factory(lambda: None)
    music_tags: Optional[List[MusicTag]] = Factory(lambda: None)
    music_difficulties: Optional[List[MusicDifficulty]] = Factory(lambda: None)
    music_vocals: Optional[List[MusicVocal]] = Factory(lambda: None)
    music_dance_members: Optional[List[MusicDanceMember]] = Factory(lambda: None)
    music_achievements: Optional[List[MusicAchievement]] = Factory(lambda: None)
    music_video_characters: Optional[List[MusicVideoCharacter]] = Factory(lambda: None)
    music_asset_variants: Optional[List[MusicAssetVariant]] = Factory(lambda: None)
    music_collaborations: Optional[List[MusicCollaboration]] = Factory(lambda: None)
    episode_music_video_costumes: Optional[List[EpisodeMusicVideoCostume]] = Factory(
        lambda: None
    )
    release_conditions: Optional[List[ReleaseCondition]] = Factory(lambda: None)
    play_level_scores: Optional[List[PlayLevelScore]] = Factory(lambda: None)
    ingame_combos: Optional[List[IngameCombo]] = Factory(lambda: None)
    ingame_notes: Optional[List[IngameNote]] = Factory(lambda: None)
    ingame_note_judges: Optional[List[IngameNoteJudge]] = Factory(lambda: None)
    ingame_play_levels: Optional[List[IngamePlayLevel]] = Factory(lambda: None)
    ingame_cutins: Optional[List[IngameCutin]] = Factory(lambda: None)
    ingame_cutin_characters: Optional[List[IngameCutinCharacter]] = Factory(
        lambda: None
    )
    ingame_judge_frames: Optional[List[IngameJudgeFrame]] = Factory(lambda: None)
    ingame_note_judge_technical_scores: Optional[
        List[IngameNoteJudgeTechnicalScore]
    ] = Factory(lambda: None)
    shops: Optional[List[Shop]] = Factory(lambda: None)
    shop_items: Optional[List[ShopItem]] = Factory(lambda: None)
    costume3d_shop_items: Optional[List[Costume3dShopItem]] = Factory(lambda: None)
    area_items: Optional[List[AreaItem]] = Factory(lambda: None)
    area_item_levels: Optional[List[AreaItemLevel]] = Factory(lambda: None)
    materials: Optional[List[Material]] = Factory(lambda: None)
    gachas: Optional[List[Gacha]] = Factory(lambda: None)
    gacha_bonuses: Optional[List[GachaBonus]] = Factory(lambda: None)
    gacha_bonus_points: Optional[List[GachaBonusPoint]] = Factory(lambda: None)
    gacha_extras: Optional[List[GachaExtra]] = Factory(lambda: None)
    gift_gacha_exchanges: Optional[List[GiftGachaExchange]] = Factory(lambda: None)
    gacha_tabs: Optional[List[Union[dict, str, int]]] = Factory(lambda: None)
    practice_tickets: Optional[List[PracticeTicket]] = Factory(lambda: None)
    skill_practice_tickets: Optional[List[SkillPracticeTicket]] = Factory(lambda: None)
    levels: Optional[List[Level]] = Factory(lambda: None)
    unit_stories: Optional[List[UnitStory]] = Factory(lambda: None)
    special_stories: Optional[List[SpecialStory]] = Factory(lambda: None)
    configs: Optional[List[Config]] = Factory(lambda: None)
    client_configs: Optional[List[ClientConfig]] = Factory(lambda: None)
    wordings: Optional[List[Wording]] = Factory(lambda: None)
    costume3ds: Optional[List[Costume3d]] = Factory(lambda: None)
    costume3d_models: Optional[List[Costume3dModel]] = Factory(lambda: None)
    costume3d_model_available_patterns: Optional[
        List[Costume3dModelAvailablePattern]
    ] = Factory(lambda: None)
    game_character_unit3d_motions: Optional[List[GameCharacterUnit3dMotion]] = Factory(
        lambda: None
    )
    costume2ds: Optional[List[Costume2d]] = Factory(lambda: None)
    costume2d_groups: Optional[List[Costume2dGroup]] = Factory(lambda: None)
    topics: Optional[List[Topic]] = Factory(lambda: None)
    live_stages: Optional[List[LiveStage]] = Factory(lambda: None)
    stamps: Optional[List[Stamp]] = Factory(lambda: None)
    multi_live_lobbies: Optional[List[MultiLiveLobby]] = Factory(lambda: None)
    master_lessons: Optional[List[MasterLesson]] = Factory(lambda: None)
    master_lesson_rewards: Optional[List[MasterLessonReward]] = Factory(lambda: None)
    card_exchange_resources: Optional[List[CardExchangeResource]] = Factory(
        lambda: None
    )
    material_exchanges: Optional[List[MaterialExchange]] = Factory(lambda: None)
    material_exchange_summaries: Optional[List[MaterialExchangeSummary]] = Factory(
        lambda: None
    )
    boost_items: Optional[List[BoostItem]] = Factory(lambda: None)
    billing_products: Optional[List[BillingProduct]] = Factory(lambda: None)
    billing_shop_items: Optional[List[BillingShopItem]] = Factory(lambda: None)
    billing_shop_item_exchange_costs: Optional[
        List[BillingShopItemExchangeCost]
    ] = Factory(lambda: None)
    colorful_passes: Optional[List[ColorfulPass]] = Factory(lambda: None)
    jewel_behaviors: Optional[List[JewelBehavior]] = Factory(lambda: None)
    character_ranks: Optional[List[CharacterRank]] = Factory(lambda: None)
    character_mission_v2s: Optional[List[CharacterMissionV2]] = Factory(lambda: None)
    character_mission_v2_parameter_groups: Optional[
        List[CharacterMissionV2ParameterGroup]
    ] = Factory(lambda: None)
    character_mission_v2_area_items: Optional[
        List[CharacterMissionV2AreaItem]
    ] = Factory(lambda: None)
    system_live2ds: Optional[List[SystemLive2d]] = Factory(lambda: None)
    normal_missions: Optional[List[NormalMission]] = Factory(lambda: None)
    beginner_missions: Optional[List[BeginnerMission]] = Factory(lambda: None)
    resource_boxes: Optional[List[ResourceBox]] = Factory(lambda: None)
    live_mission_periods: Optional[List[LiveMissionPeriod]] = Factory(lambda: None)
    live_missions: Optional[List[LiveMission]] = Factory(lambda: None)
    live_mission_passes: Optional[List[LiveMissionPass]] = Factory(lambda: None)
    penlight_colors: Optional[List[PenlightColor]] = Factory(lambda: None)
    penlights: Optional[List[Penlight]] = Factory(lambda: None)
    live_talks: Optional[List[LiveTalk]] = Factory(lambda: None)
    tips: Optional[List[Tip]] = Factory(lambda: None)
    gacha_ceil_items: Optional[List[GachaCeilItem]] = Factory(lambda: None)
    gacha_ceil_exchange_summaries: Optional[List[GachaCeilExchangeSummary]] = Factory(
        lambda: None
    )
    player_rank_rewards: Optional[List[PlayerRankReward]] = Factory(lambda: None)
    gacha_tickets: Optional[List[GachaTicket]] = Factory(lambda: None)
    honor_groups: Optional[List[HonorGroup]] = Factory(lambda: None)
    honors: Optional[List[Honor]] = Factory(lambda: None)
    honor_missions: Optional[List[HonorMission]] = Factory(lambda: None)
    bonds_honors: Optional[List[BondsHonor]] = Factory(lambda: None)
    bonds_honor_words: Optional[List[BondsHonorWord]] = Factory(lambda: None)
    bonds_rewards: Optional[List[BondsReward]] = Factory(lambda: None)
    challenge_lives: Optional[List[ChallengeLive]] = Factory(lambda: None)
    challenge_live_decks: Optional[List[ChallengeLiveDeck]] = Factory(lambda: None)
    challenge_live_stages: Optional[List[ChallengeLiveStage]] = Factory(lambda: None)
    challenge_live_stage_exs: Optional[List[ChallengeLiveStageEx]] = Factory(
        lambda: None
    )
    challenge_live_high_score_rewards: Optional[
        List[ChallengeLiveHighScoreReward]
    ] = Factory(lambda: None)
    challenge_live_characters: Optional[List[ChallengeLiveCharacter]] = Factory(
        lambda: None
    )
    challenge_live_play_day_reward_periods: Optional[
        List[ChallengeLivePlayDayRewardPeriod]
    ] = Factory(lambda: None)
    virtual_lives: Optional[List[VirtualLive]] = Factory(lambda: None)
    virtual_shops: Optional[List[VirtualShop]] = Factory(lambda: None)
    virtual_items: Optional[List[VirtualItem]] = Factory(lambda: None)
    virtual_live_cheer_messages: Optional[List[VirtualLiveCheerMessage]] = Factory(
        lambda: None
    )
    virtual_live_cheer_message_display_limits: Optional[
        List[VirtualLiveCheerMessageDisplayLimit]
    ] = Factory(lambda: None)
    virtual_live_tickets: Optional[List[VirtualLiveTicket]] = Factory(lambda: None)
    virtual_live_pamphlets: Optional[List[VirtualLivePamphlet]] = Factory(lambda: None)
    avatar_accessories: Optional[List[AvatarAccessory]] = Factory(lambda: None)
    avatar_costumes: Optional[List[AvatarCostume]] = Factory(lambda: None)
    avatar_motions: Optional[List[AvatarMotion]] = Factory(lambda: None)
    avatar_skin_colors: Optional[List[AvatarSkinColor]] = Factory(lambda: None)
    avatar_coordinates: Optional[List[AvatarCoordinate]] = Factory(lambda: None)
    ng_words: Optional[List[NgWord]] = Factory(lambda: None)
    rule_slides: Optional[List[RuleSlide]] = Factory(lambda: None)
    facilities: Optional[List[Facility]] = Factory(lambda: None)
    one_time_behaviors: Optional[List[OneTimeBehavior]] = Factory(lambda: None)
    login_bonuses: Optional[List[LoginBonus]] = Factory(lambda: None)
    beginner_login_bonuses: Optional[List[BeginnerLoginBonus]] = Factory(lambda: None)
    beginner_login_bonus_summaries: Optional[List[BeginnerLoginBonusSummary]] = Factory(
        lambda: None
    )
    limited_login_bonuses: Optional[List[LimitedLoginBonus]] = Factory(lambda: None)
    login_bonus_live2ds: Optional[List[LoginBonusLive2d]] = Factory(lambda: None)
    events: Optional[List[Event]] = Factory(lambda: None)
    event_musics: Optional[List[EventMusic]] = Factory(lambda: None)
    event_deck_bonuses: Optional[List[EventDeckBonus]] = Factory(lambda: None)
    event_rarity_bonus_rates: Optional[List[EventRarityBonusRate]] = Factory(
        lambda: None
    )
    event_items: Optional[List[EventItem]] = Factory(lambda: None)
    event_stories: Optional[List[EventStory]] = Factory(lambda: None)
    event_exchange_summaries: Optional[List[EventExchangeSummary]] = Factory(
        lambda: None
    )
    event_story_units: Optional[List[EventStoryUnit]] = Factory(lambda: None)
    event_cards: Optional[List[EventCard]] = Factory(lambda: None)
    preliminary_tournaments: Optional[List[PreliminaryTournament]] = Factory(
        lambda: None
    )
    cheerful_carnival_summaries: Optional[List[CheerfulCarnivalSummary]] = Factory(
        lambda: None
    )
    cheerful_carnival_teams: Optional[List[CheerfulCarnivalTeam]] = Factory(
        lambda: None
    )
    cheerful_carnival_party_names: Optional[List[CheerfulCarnivalPartyName]] = Factory(
        lambda: None
    )
    cheerful_carnival_character_party_names: Optional[
        List[CheerfulCarnivalCharacterPartyName]
    ] = Factory(lambda: None)
    cheerful_carnival_live_team_point_bonuses: Optional[
        List[CheerfulCarnivalLiveTeamPointBonus]
    ] = Factory(lambda: None)
    cheerful_carnival_rewards: Optional[List[CheerfulCarnivalReward]] = Factory(
        lambda: None
    )
    cheerful_carnival_result_rewards: Optional[
        List[CheerfulCarnivalResultReward]
    ] = Factory(lambda: None)
    appeals: Optional[List[Appeal]] = Factory(lambda: None)
    boosts: Optional[List[Boost]] = Factory(lambda: None)
    boost_presents: Optional[List[BoostPresent]] = Factory(lambda: None)
    boost_present_costs: Optional[List[BoostPresentCost]] = Factory(lambda: None)
    episode_characters: Optional[List[EpisodeCharacter]] = Factory(lambda: None)
    custom_profile_text_colors: Optional[List[CustomProfileTextColor]] = Factory(
        lambda: None
    )
    custom_profile_text_fonts: Optional[List[CustomProfileTextFont]] = Factory(
        lambda: None
    )
    custom_profile_player_info_resources: Optional[
        List[CustomProfilePlayerInfoResource]
    ] = Factory(lambda: None)
    custom_profile_general_background_resources: Optional[
        List[CustomProfileGeneralBackgroundResource]
    ] = Factory(lambda: None)
    custom_profile_story_background_resources: Optional[
        List[CustomProfileStoryBackgroundResource]
    ] = Factory(lambda: None)
    custom_profile_collection_resources: Optional[
        List[CustomProfileCollectionResource]
    ] = Factory(lambda: None)
    custom_profile_member_standing_picture_resources: Optional[
        List[CustomProfileMemberStandingPictureResource]
    ] = Factory(lambda: None)
    custom_profile_shape_resources: Optional[
        List[CustomProfileShapeResource]
    ] = Factory(lambda: None)
    custom_profile_etc_resources: Optional[List[CustomProfileEtcResource]] = Factory(
        lambda: None
    )
    custom_profile_member_resource_exclude_cards: Optional[
        List[Union[dict, str, int]]
    ] = Factory(lambda: None)
    custom_profile_gachas: Optional[List[CustomProfileGacha]] = Factory(lambda: None)
    custom_profile_gacha_tabs: Optional[List[Union[dict, str, int]]] = Factory(
        lambda: None
    )
    streaming_live_bgms: Optional[List[StreamingLiveBgm]] = Factory(lambda: None)
    omikujis: Optional[List[Omikuji]] = Factory(lambda: None)
    omikuji_groups: Optional[List[OmikujiGroup]] = Factory(lambda: None)
    omikuji_rates: Optional[List[OmikujiRate]] = Factory(lambda: None)
    omikuji_costs: Optional[List[OmikujiCost]] = Factory(lambda: None)
    omikuji_rewards: Optional[List[OmikujiReward]] = Factory(lambda: None)
    virtual_booth_shops: Optional[List[VirtualBoothShop]] = Factory(lambda: None)
    special_seasons: Optional[List[SpecialSeason]] = Factory(lambda: None)
    special_season_areas: Optional[List[SpecialSeasonArea]] = Factory(lambda: None)
    rank_match_penalties: Optional[List[RankMatchPenalty]] = Factory(lambda: None)
    rank_match_placements: Optional[List[RankMatchPlacement]] = Factory(lambda: None)
    rank_match_bonus_point_conditions: Optional[
        List[RankMatchBonusPointCondition]
    ] = Factory(lambda: None)
    rank_match_seasons: Optional[List[RankMatchSeason]] = Factory(lambda: None)
    rank_match_tiers: Optional[List[RankMatchTier]] = Factory(lambda: None)
    rank_match_tier_bonus_points: Optional[List[RankMatchTierBonusPoint]] = Factory(
        lambda: None
    )
    rank_match_grades: Optional[List[RankMatchGrade]] = Factory(lambda: None)
    rank_match_classes: Optional[List[RankMatchClass]] = Factory(lambda: None)
    limited_title_screens: Optional[List[LimitedTitleScreen]] = Factory(lambda: None)
    panel_mission_campaigns: Optional[List[Union[dict, str, int]]] = Factory(
        lambda: None
    )

    @classmethod
    def create(cls):
        return cls(**{field.name: None for field in fields(cls)})
