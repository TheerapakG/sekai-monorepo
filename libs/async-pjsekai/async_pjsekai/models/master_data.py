# SPDX-FileCopyrightText: 2022-2023 Erik Chan <erikchan002@gmail.com>
# SPDX-FileCopyrightText: 2023-present TheerapakG <theerapakg@gmail.com>
#
# SPDX-License-Identifier: MIT


from dataclasses import dataclass, field, fields
from datetime import datetime
from typing import Optional, Type, TypeVar, Union

from pjsekai.enums import *


@dataclass(slots=True)
class GameCharacter:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    resource_id: Optional[int] = field(default=None)
    first_name: Optional[str] = field(default=None)
    given_name: Optional[str] = field(default=None)
    first_name_ruby: Optional[str] = field(default=None)
    given_name_ruby: Optional[str] = field(default=None)
    gender: Optional[Union[Gender, Unknown]] = field(default=None)
    height: Optional[float] = field(default=None)
    live2d_height_adjustment: Optional[float] = field(default=None)
    figure: Optional[Union[Figure, Unknown]] = field(default=None)
    breast_size: Optional[Union[BreastSize, Unknown]] = field(default=None)
    model_name: Optional[str] = field(default=None)
    unit: Optional[Union[Unit, Unknown]] = field(default=None)
    support_unit_type: Optional[Union[SupportUnitType, Unknown]] = field(default=None)


@dataclass(slots=True)
class GameCharacterUnit:
    id: Optional[int] = field(default=None)
    game_character_id: Optional[int] = field(default=None)
    unit: Optional[Union[Unit, Unknown]] = field(default=None)
    color_code: Optional[str] = field(default=None)
    skin_color_code: Optional[str] = field(default=None)
    skin_shadow_color_code1: Optional[str] = field(default=None)
    skin_shadow_color_code2: Optional[str] = field(default=None)


@dataclass(slots=True)
class OutsideCharacter:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)


@dataclass(slots=True)
class Character3d:
    id: Optional[int] = field(default=None)
    character_type: Optional[Union[CharacterType, Unknown]] = field(default=None)
    character_id: Optional[int] = field(default=None)
    unit: Optional[Union[Unit, Unknown]] = field(default=None)
    name: Optional[str] = field(default=None)
    head_costume3d_id: Optional[int] = field(default=None)
    hair_costume3d_id: Optional[int] = field(default=None)
    body_costume3d_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class Character2d:
    id: Optional[int] = field(default=None)
    character_type: Optional[Union[CharacterType, Unknown]] = field(default=None)
    character_id: Optional[int] = field(default=None)
    unit: Optional[Union[Unit, Unknown]] = field(default=None)
    asset_name: Optional[str] = field(default=None)


@dataclass(slots=True)
class CharacterProfile:
    character_id: Optional[int] = field(default=None)
    character_voice: Optional[str] = field(default=None)
    birthday: Optional[str] = field(default=None)
    height: Optional[str] = field(default=None)
    school: Optional[str] = field(default=None)
    school_year: Optional[str] = field(default=None)
    hobby: Optional[str] = field(default=None)
    special_skill: Optional[str] = field(default=None)
    favorite_food: Optional[str] = field(default=None)
    hated_food: Optional[str] = field(default=None)
    weak: Optional[str] = field(default=None)
    introduction: Optional[str] = field(default=None)
    scenario_id: Optional[str] = field(default=None)


@dataclass(slots=True)
class Bond:
    id: Optional[int] = field(default=None)
    group_id: Optional[int] = field(default=None)
    character_id1: Optional[int] = field(default=None)
    character_id2: Optional[int] = field(default=None)


@dataclass(slots=True)
class Live2d:
    id: Optional[int] = field(default=None)
    character_id: Optional[int] = field(default=None)
    unit: Optional[Union[Unit, Unknown]] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    motion: Optional[str] = field(default=None)
    expression: Optional[str] = field(default=None)
    weight: Optional[int] = field(default=None)


@dataclass(slots=True)
class BondsLive2d(Live2d):
    default_flg: Optional[bool] = field(default=None)


@dataclass(slots=True)
class BondsRankUpLive2d(Live2d):
    default_flg: Optional[bool] = field(default=None)


@dataclass(slots=True)
class UnitProfile:
    unit: Optional[Union[Unit, Unknown]] = field(default=None)
    unit_name: Optional[str] = field(default=None)
    seq: Optional[int] = field(default=None)
    profile_sentence: Optional[str] = field(default=None)
    color_code: Optional[str] = field(default=None)


@dataclass(slots=True)
class ActionSet:
    id: Optional[int] = field(default=None)
    area_id: Optional[int] = field(default=None)
    script_id: Optional[str] = field(default=None)
    character_ids: Optional[list[int]] = field(default=None)
    archive_display_type: Optional[Union[ArchiveDisplayType, Unknown]] = field(
        default=None
    )
    archive_published_at: Optional[datetime] = field(default=None)
    release_condition_id: Optional[datetime] = field(default=None)
    scenario_id: Optional[str] = field(default=None)
    action_set_type: Optional[Union[ActionSetType, Unknown]] = field(default=None)
    special_season_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class Area:
    id: Optional[int] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    area_type: Optional[Union[AreaType, Unknown]] = field(default=None)
    view_type: Optional[Union[ViewType, Unknown]] = field(default=None)
    name: Optional[str] = field(default=None)
    release_condition_id: Optional[int] = field(default=None)
    label: Optional[str] = field(default=None)
    start_at: Optional[datetime] = field(default=None)
    end_at: Optional[datetime] = field(default=None)


@dataclass(slots=True)
class AreaPlaylist:
    id: Optional[int] = field(default=None)
    area_id: Optional[int] = field(default=None)
    music_id: Optional[int] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    bgm_name: Optional[str] = field(default=None)
    release_condition_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class MobCharacter:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    gender: Optional[Union[Gender, Unknown]] = field(default=None)


@dataclass(slots=True)
class CharacterCostume:
    id: Optional[int] = field(default=None)
    character_id: Optional[int] = field(default=None)
    costume_id: Optional[int] = field(default=None)
    sd_asset_bundle_name: Optional[str] = field(default=None)
    live2d_asset_bundle_name: Optional[str] = field(default=None)


@dataclass(slots=True)
class CardCostume3d:
    card_id: Optional[int] = field(default=None)
    costume3d_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class CardParameter:
    id: Optional[int] = field(default=None)
    card_id: Optional[int] = field(default=None)
    card_level: Optional[int] = field(default=None)
    card_parameter_type: Optional[Union[CardParameterType, Unknown]] = field(
        default=None
    )
    power: Optional[int] = field(default=None)


@dataclass(slots=True)
class Cost:
    resource_id: Optional[int] = field(default=None)
    resource_type: Optional[Union[ResourceType, Unknown]] = field(default=None)
    resource_level: Optional[int] = field(default=None)
    quantity: Optional[int] = field(default=None)


@dataclass(slots=True)
class SpecialTrainingCost:
    card_id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    cost: Optional[Cost] = field(default=None)


@dataclass(slots=True)
class MasterLessonAchieveResource:
    release_condition_id: Optional[int] = field(default=None)
    card_id: Optional[int] = field(default=None)
    master_rank: Optional[int] = field(default=None)
    resources: Optional[list[Union[dict, str, int]]] = field(default=None)


@dataclass(slots=True)
class Card:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    character_id: Optional[int] = field(default=None)
    card_rarity_type: Optional[Union[CardRarityType, Unknown]] = field(default=None)
    special_training_power1_bonus_fixed: Optional[int] = field(default=None)
    special_training_power2_bonus_fixed: Optional[int] = field(default=None)
    special_training_power3_bonus_fixed: Optional[int] = field(default=None)
    attr: Optional[Union[CardAttr, Unknown]] = field(default=None)
    support_unit: Optional[Union[Unit, Unknown]] = field(default=None)
    skill_id: Optional[int] = field(default=None)
    card_skill_name: Optional[str] = field(default=None)
    prefix: Optional[str] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    gacha_phrase: Optional[str] = field(default=None)
    flavor_text: Optional[str] = field(default=None)
    release_at: Optional[datetime] = field(default=None)
    archive_published_at: Optional[datetime] = field(default=None)
    card_parameters: Optional[list[CardParameter]] = field(default=None)
    special_training_costs: Optional[list[SpecialTrainingCost]] = field(default=None)
    master_lesson_achieve_resources: Optional[
        list[MasterLessonAchieveResource]
    ] = field(default=None)
    archive_display_type: Optional[Union[ArchiveDisplayType, Unknown]] = field(
        default=None
    )


@dataclass(slots=True)
class SkillEffectDetail:
    id: Optional[int] = field(default=None)
    level: Optional[int] = field(default=None)
    activate_effect_duration: Optional[float] = field(default=None)
    activate_effect_value_type: Optional[
        Union[ActivateEffectValueType, Unknown]
    ] = field(default=None)
    activate_effect_value: Optional[int] = field(default=None)


@dataclass(slots=True)
class SkillEnhanceCondition:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    unit: Optional[Union[Unit, Unknown]] = field(default=None)


@dataclass(slots=True)
class SkillEnhance:
    id: Optional[int] = field(default=None)
    skill_enhance_type: Optional[Union[SkillEnhanceType, Unknown]] = field(default=None)
    activate_effect_value_type: Optional[
        Union[ActivateEffectValueType, Unknown]
    ] = field(default=None)
    activate_effect_value: Optional[int] = field(default=None)
    skill_enhance_condition: Optional[SkillEnhanceCondition] = field(default=None)


@dataclass(slots=True)
class SkillEffect:
    id: Optional[int] = field(default=None)
    skill_effect_type: Optional[Union[SkillEffectType, Unknown]] = field(default=None)
    activate_notes_judgment_type: Optional[Union[IngameNoteJudgeType, Unknown]] = field(
        default=None
    )
    skill_effect_details: Optional[list[SkillEffectDetail]] = field(default=None)
    activate_life: Optional[int] = field(default=None)
    condition_type: Optional[Union[SkillEffectConditionType, Unknown]] = field(
        default=None
    )
    skill_enhance: Optional[SkillEnhance] = field(default=None)


@dataclass(slots=True)
class Skill:
    id: Optional[int] = field(default=None)
    short_description: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)
    description_sprite_name: Optional[str] = field(default=None)
    skill_filter_id: Optional[int] = field(default=None)
    skill_effects: Optional[list[SkillEffect]] = field(default=None)


@dataclass(slots=True)
class CardEpisode:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    card_id: Optional[int] = field(default=None)
    title: Optional[str] = field(default=None)
    scenario_id: Optional[str] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    release_condition_id: Optional[int] = field(default=None)
    power1_bonus_fixed: Optional[int] = field(default=None)
    power2_bonus_fixed: Optional[int] = field(default=None)
    power3_bonus_fixed: Optional[int] = field(default=None)
    reward_resource_box_ids: Optional[list[int]] = field(default=None)
    costs: Optional[list[Cost]] = field(default=None)
    card_episode_part_type: Optional[Union[CardEpisodePartType, Unknown]] = field(
        default=None
    )


@dataclass(slots=True)
class CardRarity:
    card_rarity_type: Optional[Union[CardRarityType, Unknown]] = field(default=None)
    seq: Optional[int] = field(default=None)
    max_level: Optional[int] = field(default=None)
    max_skill_level: Optional[int] = field(default=None)
    training_max_level: Optional[int] = field(default=None)


@dataclass(slots=True)
class CardSkillCost:
    id: Optional[int] = field(default=None)
    material_id: Optional[int] = field(default=None)
    exp: Optional[int] = field(default=None)


@dataclass(slots=True)
class Music:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    release_condition_id: Optional[int] = field(default=None)
    categories: Optional[list[Union[MusicCategory, Unknown]]] = field(default=None)
    title: Optional[str] = field(default=None)
    pronunciation: Optional[str] = field(default=None)
    lyricist: Optional[str] = field(default=None)
    composer: Optional[str] = field(default=None)
    arranger: Optional[str] = field(default=None)
    dancer_count: Optional[int] = field(default=None)
    self_dancer_position: Optional[int] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    live_talk_background_asset_bundle_name: Optional[str] = field(default=None)
    published_at: Optional[datetime] = field(default=None)
    live_stage_id: Optional[int] = field(default=None)
    filler_sec: Optional[float] = field(default=None)
    music_collaboration_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class MusicTag:
    id: Optional[int] = field(default=None)
    music_id: Optional[int] = field(default=None)
    music_tag: Optional[str] = field(default=None)
    seq: Optional[int] = field(default=None)


@dataclass(slots=True)
class MusicDifficulty:
    id: Optional[int] = field(default=None)
    music_id: Optional[int] = field(default=None)
    music_difficulty: Optional[Union[MusicDifficultyType, Unknown]] = field(
        default=None
    )
    play_level: Optional[int] = field(default=None)
    release_condition_id: Optional[int] = field(default=None)
    total_note_count: Optional[int] = field(default=None)


@dataclass(slots=True)
class Character:
    id: Optional[int] = field(default=None)
    music_id: Optional[int] = field(default=None)
    music_vocal_id: Optional[int] = field(default=None)
    character_type: Optional[Union[CharacterType, Unknown]] = field(default=None)
    character_id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)


@dataclass(slots=True)
class MusicVocal:
    id: Optional[int] = field(default=None)
    music_id: Optional[int] = field(default=None)
    music_vocal_type: Optional[Union[MusicVocalType, Unknown]] = field(default=None)
    seq: Optional[int] = field(default=None)
    release_condition_id: Optional[int] = field(default=None)
    caption: Optional[str] = field(default=None)
    characters: Optional[list[Character]] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    archive_published_at: Optional[datetime] = field(default=None)
    special_season_id: Optional[int] = field(default=None)
    archive_display_type: Optional[Union[ArchiveDisplayType, Unknown]] = field(
        default=None
    )


@dataclass(slots=True)
class MusicDanceMember:
    id: Optional[int] = field(default=None)
    music_id: Optional[int] = field(default=None)
    default_music_type: Optional[Union[DefaultMusicType, Unknown]] = field(default=None)
    character_id1: Optional[int] = field(default=None)
    unit1: Optional[Union[Unit, Unknown]] = field(default=None)
    character_id2: Optional[int] = field(default=None)
    unit2: Optional[Union[Unit, Unknown]] = field(default=None)
    character_id3: Optional[int] = field(default=None)
    unit3: Optional[Union[Unit, Unknown]] = field(default=None)
    character_id4: Optional[int] = field(default=None)
    unit4: Optional[Union[Unit, Unknown]] = field(default=None)
    character_id5: Optional[int] = field(default=None)
    unit5: Optional[Union[Unit, Unknown]] = field(default=None)


@dataclass(slots=True)
class MusicAchievement:
    id: Optional[int] = field(default=None)
    music_achievement_type: Optional[Union[MusicAchievementType, Unknown]] = field(
        default=None
    )
    music_achievement_type_value: Optional[str] = field(default=None)
    resource_box_id: Optional[int] = field(default=None)
    music_difficulty_type: Optional[Union[MusicDifficultyType, Unknown]] = field(
        default=None
    )


@dataclass(slots=True)
class MusicVideoCharacter:
    id: Optional[int] = field(default=None)
    music_id: Optional[int] = field(default=None)
    default_music_type: Optional[Union[DefaultMusicType, Unknown]] = field(default=None)
    game_character_unit_id: Optional[int] = field(default=None)
    dance_priority: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    priority: Optional[int] = field(default=None)


@dataclass(slots=True)
class MusicAssetVariant:
    id: Optional[int] = field(default=None)
    music_vocal_id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    music_asset_type: Optional[Union[MusicAssetType, Unknown]] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)


@dataclass(slots=True)
class MusicCollaboration:
    id: Optional[int] = field(default=None)
    label: Optional[str] = field(default=None)


@dataclass(slots=True)
class EpisodeMusicVideoCostume:
    id: Optional[int] = field(default=None)
    music_vocal_id: Optional[int] = field(default=None)
    character3d_id1: Optional[int] = field(default=None)
    character3d_id2: Optional[int] = field(default=None)
    character3d_id3: Optional[int] = field(default=None)
    character3d_id4: Optional[int] = field(default=None)
    character3d_id5: Optional[int] = field(default=None)


@dataclass(slots=True)
class ReleaseCondition:
    id: Optional[int] = field(default=None)
    sentence: Optional[str] = field(default=None)
    release_condition_type: Optional[Union[ReleaseConditionType, Unknown]] = field(
        default=None
    )
    release_condition_type_level: Optional[int] = field(default=None)
    release_condition_type_id: Optional[int] = field(default=None)
    release_condition_type_quantity: Optional[int] = field(default=None)


@dataclass(slots=True)
class PlayLevelScore:
    live_type: Optional[Union[LiveType, Unknown]] = field(default=None)
    play_level: Optional[int] = field(default=None)
    s: Optional[int] = field(default=None)
    a: Optional[int] = field(default=None)
    b: Optional[int] = field(default=None)
    c: Optional[int] = field(default=None)


@dataclass(slots=True)
class IngameCombo:
    id: Optional[int] = field(default=None)
    from_count: Optional[int] = field(default=None)
    to_count: Optional[int] = field(default=None)
    score_coefficient: Optional[float] = field(default=None)


@dataclass(slots=True)
class IngameNote:
    id: Optional[int] = field(default=None)
    ingame_note_type: Optional[Union[IngameNoteType, Unknown]] = field(default=None)
    score_coefficient: Optional[float] = field(default=None)
    damage_bad: Optional[int] = field(default=None)
    damage_miss: Optional[int] = field(default=None)


@dataclass(slots=True)
class IngameNoteJudge:
    id: Optional[int] = field(default=None)
    ingame_note_jadge_type: Optional[Union[IngameNoteJudgeType, Unknown]] = field(
        default=None
    )
    score_coefficient: Optional[float] = field(default=None)
    damage: Optional[int] = field(default=None)


@dataclass(slots=True)
class IngamePlayLevel:
    play_level: Optional[int] = field(default=None)
    score_coefficient: Optional[float] = field(default=None)


@dataclass(slots=True)
class IngameCutin:
    id: Optional[int] = field(default=None)
    music_difficulty: Optional[Union[MusicDifficultyType, Unknown]] = field(
        default=None
    )
    combo: Optional[int] = field(default=None)


@dataclass(slots=True)
class IngameCutinCharacter:
    id: Optional[int] = field(default=None)
    ingame_cutin_character_type: Optional[
        Union[IngameCutinCharacterType, Unknown]
    ] = field(default=None)
    priority: Optional[int] = field(default=None)
    game_character_unit_id1: Optional[int] = field(default=None)
    game_character_unit_id2: Optional[int] = field(default=None)
    asset_bundle_name1: Optional[str] = field(default=None)
    asset_bundle_name2: Optional[str] = field(default=None)
    release_condition_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class IngameJudgeFrame:
    id: Optional[int] = field(default=None)
    ingame_note_type: Optional[Union[IngameNoteType, Unknown]] = field(default=None)
    perfect: Optional[float] = field(default=None)
    great: Optional[float] = field(default=None)
    good: Optional[float] = field(default=None)
    bad: Optional[float] = field(default=None)
    perfect_before: Optional[float] = field(default=None)
    perfect_after: Optional[float] = field(default=None)
    great_before: Optional[float] = field(default=None)
    great_after: Optional[float] = field(default=None)
    good_before: Optional[float] = field(default=None)
    good_after: Optional[float] = field(default=None)
    bad_before: Optional[float] = field(default=None)
    bad_after: Optional[float] = field(default=None)


@dataclass(slots=True)
class IngameNoteJudgeTechnicalScore:
    id: Optional[int] = field(default=None)
    live_type: Optional[Union[LiveType, Unknown]] = field(default=None)
    ingame_note_jadge_type: Optional[Union[IngameNoteJudgeType, Unknown]] = field(
        default=None
    )
    score: Optional[int] = field(default=None)


@dataclass(slots=True)
class Shop:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    shop_type: Optional[Union[ShopType, Unknown]] = field(default=None)
    area_id: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    release_condition_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class ShopItemCost:
    shop_item_id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    cost: Optional[Cost] = field(default=None)


@dataclass(slots=True)
class ShopItem:
    id: Optional[int] = field(default=None)
    shop_id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    release_condition_id: Optional[int] = field(default=None)
    resource_box_id: Optional[int] = field(default=None)
    costs: Optional[list[ShopItemCost]] = field(default=None)
    start_at: Optional[datetime] = field(default=None)


@dataclass(slots=True)
class Costume3dShopItemCost(Cost):
    id: Optional[int] = field(default=None)
    costume3d_shop_item_id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)


@dataclass(slots=True)
class Costume3dShopItem:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    group_id: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    body_costume3d_id: Optional[int] = field(default=None)
    release_condition_id: Optional[int] = field(default=None)
    costs: Optional[list[Costume3dShopItemCost]] = field(default=None)
    start_at: Optional[datetime] = field(default=None)
    head_costume3d_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class AreaItem:
    id: Optional[int] = field(default=None)
    area_id: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    flavor_text: Optional[str] = field(default=None)
    spawn_point: Optional[str] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)


@dataclass(slots=True)
class AreaItemLevel:
    area_item_id: Optional[int] = field(default=None)
    level: Optional[int] = field(default=None)
    targetunit: Optional[Union[Unit, Unknown]] = field(default=None)
    target_card_attr: Optional[Union[CardAttr, Unknown]] = field(default=None)
    target_game_character_id: Optional[int] = field(default=None)
    power1_bonus_rate: Optional[float] = field(default=None)
    power1_all_match_bonus_rate: Optional[float] = field(default=None)
    power2_bonus_rate: Optional[float] = field(default=None)
    power2_all_match_bonus_rate: Optional[float] = field(default=None)
    power3_bonus_rate: Optional[float] = field(default=None)
    power3_all_match_bonus_rate: Optional[float] = field(default=None)
    sentence: Optional[str] = field(default=None)


@dataclass(slots=True)
class Material:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    flavor_text: Optional[str] = field(default=None)
    material_type: Optional[Union[MaterialType, Unknown]] = field(default=None)


@dataclass(slots=True)
class GachaCardRarityRate:
    id: Optional[int] = field(default=None)
    group_id: Optional[int] = field(default=None)
    card_rarity_type: Optional[Union[CardRarityType, Unknown]] = field(default=None)
    lottery_type: Optional[Union[LotteryType, Unknown]] = field(default=None)
    rate: Optional[float] = field(default=None)


@dataclass(slots=True)
class GachaDetail:
    id: Optional[int] = field(default=None)
    gacha_id: Optional[int] = field(default=None)
    card_id: Optional[int] = field(default=None)
    weight: Optional[int] = field(default=None)
    is_wish: Optional[bool] = field(default=None)


@dataclass(slots=True)
class GachaBehavior:
    id: Optional[int] = field(default=None)
    gacha_id: Optional[int] = field(default=None)
    group_id: Optional[int] = field(default=None)
    priority: Optional[int] = field(default=None)
    gacha_behavior_type: Optional[Union[GachaBehaviorType, Unknown]] = field(
        default=None
    )
    cost_resource_type: Optional[Union[ResourceType, Unknown]] = field(default=None)
    cost_resource_quantity: Optional[int] = field(default=None)
    spin_count: Optional[int] = field(default=None)
    execute_limit: Optional[int] = field(default=None)
    cost_resource_id: Optional[int] = field(default=None)
    gacha_extra_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class GachaPickup:
    id: Optional[int] = field(default=None)
    gacha_id: Optional[int] = field(default=None)
    card_id: Optional[int] = field(default=None)
    gacha_pickup_type: Optional[Union[GachaPickupType, Unknown]] = field(default=None)


@dataclass(slots=True)
class GachaInformation:
    gacha_id: Optional[int] = field(default=None)
    summary: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)


@dataclass(slots=True)
class Gacha:
    id: Optional[int] = field(default=None)
    gacha_type: Optional[Union[GachaType, Unknown]] = field(default=None)
    name: Optional[str] = field(default=None)
    seq: Optional[int] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    gacha_card_rarity_rate_group_id: Optional[int] = field(default=None)
    start_at: Optional[datetime] = field(default=None)
    end_at: Optional[datetime] = field(default=None)
    is_show_period: Optional[bool] = field(default=None)
    gacha_ceil_item_id: Optional[int] = field(default=None)
    wish_select_count: Optional[int] = field(default=None)
    wish_fixed_select_count: Optional[int] = field(default=None)
    wish_limited_select_count: Optional[int] = field(default=None)
    gacha_card_rarity_rates: Optional[list[GachaCardRarityRate]] = field(default=None)
    gacha_details: Optional[list[GachaDetail]] = field(default=None)
    gacha_behaviors: Optional[list[GachaBehavior]] = field(default=None)
    gacha_pickups: Optional[list[GachaPickup]] = field(default=None)
    gacha_pickup_costumes: Optional[list[Union[dict, str, int]]] = field(default=None)
    gacha_information: Optional[GachaInformation] = field(default=None)
    drawable_gacha_hour: Optional[int] = field(default=None)
    gacha_bonus_id: Optional[int] = field(default=None)
    spin_limit: Optional[int] = field(default=None)


@dataclass(slots=True)
class GachaBonus:
    id: Optional[int] = field(default=None)


@dataclass(slots=True)
class GachaBonusPoint:
    id: Optional[int] = field(default=None)
    resource_type: Optional[Union[ResourceType, Unknown]] = field(default=None)
    point: Optional[float] = field(default=None)


@dataclass(slots=True)
class GachaExtra:
    id: Optional[int] = field(default=None)
    resource_box_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class GiftGachaExchange:
    id: Optional[int] = field(default=None)
    gacha_id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    resource_box_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class PracticeTicket:
    id: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    exp: Optional[int] = field(default=None)
    flavor_text: Optional[str] = field(default=None)


@dataclass(slots=True)
class SkillPracticeTicket(PracticeTicket):
    pass


@dataclass(slots=True)
class Level:
    id: Optional[int] = field(default=None)
    level_type: Optional[Union[LevelType, Unknown]] = field(default=None)
    level: Optional[int] = field(default=None)
    total_exp: Optional[int] = field(default=None)


@dataclass(slots=True)
class Episode:
    id: Optional[int] = field(default=None)
    episode_no: Optional[int] = field(default=None)
    title: Optional[str] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    scenario_id: Optional[str] = field(default=None)
    release_condition_id: Optional[int] = field(default=None)
    reward_resource_box_ids: Optional[list[int]] = field(default=None)


@dataclass(slots=True)
class UnitStoryEpisode(Episode):
    unit: Optional[Union[Unit, Unknown]] = field(default=None)
    chapter_no: Optional[int] = field(default=None)
    unit_episode_category: Optional[Union[Unit, Unknown]] = field(default=None)
    episode_no_label: Optional[str] = field(default=None)
    limited_release_start_at: Optional[datetime] = field(default=None)
    limited_release_end_at: Optional[datetime] = field(default=None)
    and_release_condition_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class Chapter:
    id: Optional[int] = field(default=None)
    unit: Optional[Union[Unit, Unknown]] = field(default=None)
    chapter_no: Optional[int] = field(default=None)
    title: Optional[str] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    episodes: Optional[list[UnitStoryEpisode]] = field(default=None)


@dataclass(slots=True)
class UnitStory:
    unit: Optional[Union[Unit, Unknown]] = field(default=None)
    seq: Optional[int] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    chapters: Optional[list[Chapter]] = field(default=None)


@dataclass(slots=True)
class SpecialStoryEpisode(Episode):
    special_story_id: Optional[int] = field(default=None)
    special_story_episode_type: Optional[str] = field(default=None)
    is_able_skip: Optional[bool] = field(default=None)
    is_action_set_refresh: Optional[bool] = field(default=None)
    special_story_episode_type_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class SpecialStory:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    title: Optional[str] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    start_at: Optional[datetime] = field(default=None)
    end_at: Optional[datetime] = field(default=None)
    episodes: Optional[list[SpecialStoryEpisode]] = field(default=None)


@dataclass(slots=True)
class Config:
    config_key: Optional[str] = field(default=None)
    value: Optional[str] = field(default=None)


@dataclass(slots=True)
class ClientConfig:
    id: Optional[int] = field(default=None)
    value: Optional[str] = field(default=None)
    type: Optional[Union[ClientConfigType, Unknown]] = field(default=None)


@dataclass(slots=True)
class Wording:
    wording_key: Optional[str] = field(default=None)
    value: Optional[str] = field(default=None)


@dataclass(slots=True)
class Costume3d:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    costume3d_group_id: Optional[int] = field(default=None)
    costume3d_type: Optional[Union[Costume3dType, Unknown]] = field(default=None)
    name: Optional[str] = field(default=None)
    part_type: Optional[Union[PartType, Unknown]] = field(default=None)
    color_id: Optional[int] = field(default=None)
    color_name: Optional[str] = field(default=None)
    character_id: Optional[int] = field(default=None)
    costume3d_rarity: Optional[Union[Costume3dRarity, Unknown]] = field(default=None)
    how_to_obtain: Optional[str] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    designer: Optional[str] = field(default=None)
    archive_display_type: Optional[Union[ArchiveDisplayType, Unknown]] = field(
        default=None
    )
    archive_published_at: Optional[datetime] = field(default=None)
    published_at: Optional[datetime] = field(default=None)


@dataclass(slots=True)
class Costume3dModel:
    id: Optional[int] = field(default=None)
    costume3d_id: Optional[int] = field(default=None)
    unit: Optional[Union[Unit, Unknown]] = field(default=None)
    head_costume3d_asset_bundle_type: Optional[
        Union[HeadCostume3dAssetBundleType, Unknown]
    ] = field(default=None)
    thumbnail_asset_bundle_name: Optional[str] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    color_asset_bundle_name: Optional[str] = field(default=None)
    part: Optional[str] = field(default=None)


@dataclass(slots=True)
class Costume3dModelAvailablePattern:
    id: Optional[int] = field(default=None)
    head_costume3d_id: Optional[int] = field(default=None)
    hair_costume3d_id: Optional[int] = field(default=None)
    unit: Optional[Union[Unit, Unknown]] = field(default=None)
    is_default: Optional[bool] = field(default=None)


@dataclass(slots=True)
class GameCharacterUnit3dMotion:
    id: Optional[int] = field(default=None)
    game_character_unit_id: Optional[int] = field(default=None)
    motion_type: Optional[Union[MotionType, Unknown]] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)


@dataclass(slots=True)
class Costume2d:
    id: Optional[int] = field(default=None)
    costume2d_group_id: Optional[int] = field(default=None)
    character2d_id: Optional[int] = field(default=None)
    from_mmddhh: Optional[str] = field(default=None)
    to_mmddhh: Optional[str] = field(default=None)
    live2d_asset_bundle_name: Optional[str] = field(default=None)
    spine_asset_bundle_name: Optional[str] = field(default=None)


@dataclass(slots=True)
class Costume2dGroup:
    id: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)


@dataclass(slots=True)
class Topic:
    id: Optional[int] = field(default=None)
    topic_type: Optional[Union[TopicType, Unknown]] = field(default=None)
    topic_type_id: Optional[int] = field(default=None)
    release_condition_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class LiveStage:
    id: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)


@dataclass(slots=True)
class Stamp:
    id: Optional[int] = field(default=None)
    stamp_type: Optional[Union[StampType, Unknown]] = field(default=None)
    seq: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    balloon_asset_bundle_name: Optional[str] = field(default=None)
    character_id1: Optional[int] = field(default=None)
    game_character_unit_id: Optional[int] = field(default=None)
    archive_published_at: Optional[datetime] = field(default=None)
    description: Optional[str] = field(default=None)
    archive_display_type: Optional[Union[ArchiveDisplayType, Unknown]] = field(
        default=None
    )


@dataclass(slots=True)
class MultiLiveLobby:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    photon_lobby_name: Optional[str] = field(default=None)
    matching_logic: Optional[Union[MatchingLogic, Unknown]] = field(default=None)
    total_power: Optional[int] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    multi_live_lobby_type: Optional[Union[MultiLiveLobbyType, Unknown]] = field(
        default=None
    )


@dataclass(slots=True)
class MasterLessonCost(Cost):
    id: Optional[int] = field(default=None)
    card_rarity_type: Optional[Union[CardRarityType, Unknown]] = field(default=None)
    master_rank: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)


@dataclass(slots=True)
class MasterLesson:
    card_rarity_type: Optional[Union[CardRarityType, Unknown]] = field(default=None)
    master_rank: Optional[int] = field(default=None)
    power1_bonus_fixed: Optional[int] = field(default=None)
    power2_bonus_fixed: Optional[int] = field(default=None)
    power3_bonus_fixed: Optional[int] = field(default=None)
    character_rank_exp: Optional[int] = field(default=None)
    costs: Optional[list[MasterLessonCost]] = field(default=None)
    rewards: Optional[list[Union[dict, str, int]]] = field(default=None)


@dataclass(slots=True)
class MasterLessonReward:
    id: Optional[int] = field(default=None)
    card_id: Optional[int] = field(default=None)
    master_rank: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    resource_box_id: Optional[int] = field(default=None)
    card_rarity: Optional[int] = field(default=None)


@dataclass(slots=True)
class CardExchangeResource:
    card_rarity_type: Optional[Union[CardRarityType, Unknown]] = field(default=None)
    seq: Optional[int] = field(default=None)
    resource_box_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class MaterialExchangeCost(Cost):
    material_exchange_id: Optional[int] = field(default=None)
    cost_group_id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)


@dataclass(slots=True)
class MaterialExchange:
    id: Optional[int] = field(default=None)
    material_exchange_summary_id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    resource_box_id: Optional[int] = field(default=None)
    refresh_cycle: Optional[Union[RefreshCycle, Unknown]] = field(default=None)
    costs: Optional[list[MaterialExchangeCost]] = field(default=None)
    exchange_limit: Optional[int] = field(default=None)
    start_at: Optional[datetime] = field(default=None)


@dataclass(slots=True)
class MaterialExchangeSummary:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    exchange_category: Optional[Union[ExchangeCategory, Unknown]] = field(default=None)
    material_exchange_type: Optional[Union[MaterialExchangeType, Unknown]] = field(
        default=None
    )
    name: Optional[str] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    start_at: Optional[datetime] = field(default=None)
    material_exchanges: Optional[list[MaterialExchange]] = field(default=None)
    end_at: Optional[datetime] = field(default=None)
    notification_remain_hour: Optional[int] = field(default=None)


@dataclass(slots=True)
class BoostItem:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    recovery_value: Optional[int] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    flavor_text: Optional[str] = field(default=None)


@dataclass(slots=True)
class BillingProduct:
    id: Optional[int] = field(default=None)
    group_id: Optional[int] = field(default=None)
    platform: Optional[Platform] = field(default=None)
    product_id: Optional[str] = field(default=None)
    price: Optional[int] = field(default=None)
    unit_price: Optional[float] = field(default=None)


@dataclass(slots=True)
class BillingShopItem:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    billing_shop_item_type: Optional[Union[BillingShopItemType, Unknown]] = field(
        default=None
    )
    billing_product_group_id: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)
    billable_limit_type: Optional[Union[BillableLimitType, Unknown]] = field(
        default=None
    )
    billable_limit_reset_interval_type: Optional[
        Union[BillableLimitResetIntervalType, Unknown]
    ] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    resource_box_id: Optional[int] = field(default=None)
    billable_limit_value: Optional[int] = field(default=None)
    bonus_resource_box_id: Optional[int] = field(default=None)
    label: Optional[str] = field(default=None)
    end_at: Optional[datetime] = field(default=None)
    start_at: Optional[datetime] = field(default=None)
    billable_limit_reset_interval_value: Optional[int] = field(default=None)
    purchase_option: Optional[Union[PurchaseOption, Unknown]] = field(default=None)


@dataclass(slots=True)
class BillingShopItemExchangeCost(Cost):
    id: Optional[int] = field(default=None)
    billing_shop_item_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class ColorfulPass:
    id: Optional[int] = field(default=None)
    resource_box_id: Optional[int] = field(default=None)
    receivable_days: Optional[int] = field(default=None)
    present_sentence: Optional[str] = field(default=None)
    expire_days: Optional[int] = field(default=None)
    daily_paid_gacha_spin_limit: Optional[int] = field(default=None)
    challenge_live_point_multiple: Optional[int] = field(default=None)
    live_point_multiple: Optional[int] = field(default=None)


@dataclass(slots=True)
class JewelBehavior:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    jewel_behavior_type: Optional[Union[JewelBehaviorType, Unknown]] = field(
        default=None
    )
    jewel_behavior_type_quantity: Optional[int] = field(default=None)
    amount: Optional[int] = field(default=None)


@dataclass(slots=True)
class CharacterRankAchieveResource:
    release_condition_id: Optional[int] = field(default=None)
    character_id: Optional[int] = field(default=None)
    character_rank: Optional[int] = field(default=None)
    resources: Optional[list[Union[dict, str, int]]] = field(default=None)


@dataclass(slots=True)
class CharacterRank:
    id: Optional[int] = field(default=None)
    character_id: Optional[int] = field(default=None)
    character_rank: Optional[int] = field(default=None)
    power1_bonus_rate: Optional[float] = field(default=None)
    power2_bonus_rate: Optional[float] = field(default=None)
    power3_bonus_rate: Optional[float] = field(default=None)
    reward_resource_box_ids: Optional[list[int]] = field(default=None)
    character_rank_achieve_resources: Optional[
        list[CharacterRankAchieveResource]
    ] = field(default=None)


@dataclass(slots=True)
class CharacterMissionV2:
    id: Optional[int] = field(default=None)
    character_mission_type: Optional[Union[CharacterMissionType, Unknown]] = field(
        default=None
    )
    character_id: Optional[int] = field(default=None)
    parameter_group_id: Optional[int] = field(default=None)
    sentence: Optional[str] = field(default=None)
    progress_sentence: Optional[str] = field(default=None)
    is_achievement_mission: Optional[bool] = field(default=None)


@dataclass(slots=True)
class CharacterMissionV2ParameterGroup:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    requirement: Optional[int] = field(default=None)
    exp: Optional[int] = field(default=None)


@dataclass(slots=True)
class CharacterMissionV2AreaItem:
    id: Optional[int] = field(default=None)
    character_mission_type: Optional[Union[CharacterMissionType, Unknown]] = field(
        default=None
    )
    area_item_id: Optional[int] = field(default=None)
    character_id: Optional[int] = field(default=None)
    unit: Optional[Union[Unit, Unknown]] = field(default=None)


@dataclass(slots=True)
class SystemLive2d(Live2d):
    serif: Optional[str] = field(default=None)
    voice: Optional[str] = field(default=None)
    published_at: Optional[datetime] = field(default=None)
    closed_at: Optional[datetime] = field(default=None)
    special_season_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class Reward:
    id: Optional[int] = field(default=None)
    mission_type: Optional[Union[MissionType, Unknown]] = field(default=None)
    mission_id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    resource_box_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class NormalMission:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    normal_mission_type: Optional[Union[NormalMissionType, Unknown]] = field(
        default=None
    )
    requirement: Optional[int] = field(default=None)
    sentence: Optional[str] = field(default=None)
    rewards: Optional[list[Reward]] = field(default=None)


@dataclass(slots=True)
class BeginnerMission:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    beginner_mission_type: Optional[Union[BeginnerMissionType, Unknown]] = field(
        default=None
    )
    beginner_mission_category: Optional[
        Union[BeginnerMissionCategory, Unknown]
    ] = field(default=None)
    requirement: Optional[int] = field(default=None)
    sentence: Optional[str] = field(default=None)
    rewards: Optional[list[Reward]] = field(default=None)


@dataclass(slots=True)
class Detail:
    resource_box_purpose: Optional[Union[ResourceBoxPurpose, Unknown]] = field(
        default=None
    )
    resource_box_id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    resource_type: Optional[Union[ResourceType, Unknown]] = field(default=None)
    resource_quantity: Optional[int] = field(default=None)
    resource_id: Optional[int] = field(default=None)
    resource_level: Optional[int] = field(default=None)


@dataclass(slots=True)
class ResourceBox:
    resource_box_purpose: Optional[Union[ResourceBoxPurpose, Unknown]] = field(
        default=None
    )
    id: Optional[int] = field(default=None)
    resource_box_type: Optional[Union[ResourceBoxType, Unknown]] = field(default=None)
    details: Optional[list[Detail]] = field(default=None)
    description: Optional[str] = field(default=None)
    name: Optional[str] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)


@dataclass(slots=True)
class LiveMissionPeriod:
    id: Optional[int] = field(default=None)
    start_at: Optional[datetime] = field(default=None)
    end_at: Optional[datetime] = field(default=None)
    sentence: Optional[str] = field(default=None)


@dataclass(slots=True)
class LiveMission:
    id: Optional[int] = field(default=None)
    live_mission_period_id: Optional[int] = field(default=None)
    live_mission_type: Optional[Union[LiveMissionType, Unknown]] = field(default=None)
    requirement: Optional[int] = field(default=None)
    rewards: Optional[list[Reward]] = field(default=None)


@dataclass(slots=True)
class LiveMissionPass:
    id: Optional[int] = field(default=None)
    live_mission_period_id: Optional[int] = field(default=None)
    costume_name: Optional[str] = field(default=None)
    character3d_id1: Optional[int] = field(default=None)
    character3d_id2: Optional[int] = field(default=None)
    male_asset_bundle_name: Optional[str] = field(default=None)
    female_asset_bundle_name: Optional[str] = field(default=None)


@dataclass(slots=True)
class PenlightColor:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)
    color_code: Optional[str] = field(default=None)
    character_id: Optional[int] = field(default=None)
    unit: Optional[Union[Unit, Unknown]] = field(default=None)


@dataclass(slots=True)
class Penlight:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    default_penlight_color_id: Optional[int] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)


@dataclass(slots=True)
class LiveTalk:
    id: Optional[int] = field(default=None)
    live_talk_type: Optional[Union[LiveTalkType, Unknown]] = field(default=None)
    scenario_id: Optional[str] = field(default=None)
    character_id1: Optional[int] = field(default=None)
    character_id2: Optional[int] = field(default=None)


@dataclass(slots=True)
class Tip:
    id: Optional[int] = field(default=None)
    title: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)
    from_user_rank: Optional[int] = field(default=None)
    to_user_rank: Optional[int] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)


@dataclass(slots=True)
class GachaCeilItem:
    id: Optional[int] = field(default=None)
    gacha_id: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    convert_start_at: Optional[datetime] = field(default=None)
    convert_resource_box_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class GachaCeilExchangeCost(Cost):
    gacha_ceil_exchange_id: Optional[int] = field(default=None)
    gacha_ceil_item_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class GachaCeilExchangeSubstituteCost(Cost):
    id: Optional[int] = field(default=None)
    substitute_quantity: Optional[int] = field(default=None)


@dataclass(slots=True)
class GachaCeilExchange:
    id: Optional[int] = field(default=None)
    gacha_ceil_exchange_summary_id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    resource_box_id: Optional[int] = field(default=None)
    start_at: Optional[datetime] = field(default=None)
    end_at: Optional[datetime] = field(default=None)
    gacha_ceil_exchange_cost: Optional[GachaCeilExchangeCost] = field(default=None)
    gacha_ceil_exchange_substitute_costs: Optional[
        list[GachaCeilExchangeSubstituteCost]
    ] = field(default=None)
    exchange_limit: Optional[int] = field(default=None)
    gacha_ceil_exchange_label_type: Optional[
        Union[GachaCeilExchangeLabelType, Unknown]
    ] = field(default=None)
    substitute_limit: Optional[int] = field(default=None)


@dataclass(slots=True)
class GachaCeilExchangeSummary:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    gacha_id: Optional[int] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    start_at: Optional[datetime] = field(default=None)
    end_at: Optional[datetime] = field(default=None)
    gacha_ceil_exchanges: Optional[list[GachaCeilExchange]] = field(default=None)
    gacha_ceil_item_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class PlayerRankReward:
    id: Optional[int] = field(default=None)
    player_rank: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    resource_box_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class GachaTicket:
    id: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)


@dataclass(slots=True)
class HonorGroup:
    id: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    honor_type: Optional[Union[HonorType, Unknown]] = field(default=None)
    archive_published_at: Optional[datetime] = field(default=None)
    background_asset_bundle_name: Optional[str] = field(default=None)


@dataclass(slots=True)
class HonorLevel:
    honor_id: Optional[int] = field(default=None)
    level: Optional[int] = field(default=None)
    bonus: Optional[int] = field(default=None)
    description: Optional[str] = field(default=None)


@dataclass(slots=True)
class Honor:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    group_id: Optional[int] = field(default=None)
    honor_rarity: Optional[Union[HonorRarity, Unknown]] = field(default=None)
    name: Optional[str] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    levels: Optional[list[HonorLevel]] = field(default=None)
    honor_type_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class HonorMission:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    honor_mission_type: Optional[Union[HonorMissionType, Unknown]] = field(default=None)
    requirement: Optional[int] = field(default=None)
    sentence: Optional[str] = field(default=None)
    rewards: Optional[list[Reward]] = field(default=None)


@dataclass(slots=True)
class BondsHonorLevel:
    id: Optional[int] = field(default=None)
    bonds_honor_id: Optional[int] = field(default=None)
    level: Optional[int] = field(default=None)
    description: Optional[str] = field(default=None)


@dataclass(slots=True)
class BondsHonor:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    bonds_group_id: Optional[int] = field(default=None)
    game_character_unit_id1: Optional[int] = field(default=None)
    game_character_unit_id2: Optional[int] = field(default=None)
    honor_rarity: Optional[Union[HonorRarity, Unknown]] = field(default=None)
    name: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)
    levels: Optional[list[BondsHonorLevel]] = field(default=None)
    configurable_unit_virtual_singer: Optional[bool] = field(default=None)


@dataclass(slots=True)
class BondsHonorWord:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    bonds_group_id: Optional[int] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    name: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)


@dataclass(slots=True)
class BondsReward:
    id: Optional[int] = field(default=None)
    bonds_group_id: Optional[int] = field(default=None)
    rank: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    bonds_reward_type: Optional[Union[BondsRewardType, Unknown]] = field(default=None)
    resource_box_id: Optional[int] = field(default=None)
    description: Optional[str] = field(default=None)


@dataclass(slots=True)
class ChallengeLiveDetail:
    id: Optional[int] = field(default=None)
    challenge_live_id: Optional[int] = field(default=None)
    challenge_live_type: Optional[Union[LiveType, Unknown]] = field(default=None)


@dataclass(slots=True)
class ChallengeLive:
    id: Optional[int] = field(default=None)
    playable_count: Optional[int] = field(default=None)
    challenge_live_details: Optional[list[ChallengeLiveDetail]] = field(default=None)


@dataclass(slots=True)
class ChallengeLiveDeck:
    id: Optional[int] = field(default=None)
    character_id: Optional[int] = field(default=None)
    release_condition_id: Optional[int] = field(default=None)
    card_limit: Optional[int] = field(default=None)


@dataclass(slots=True)
class ChallengeLiveStage:
    id: Optional[int] = field(default=None)
    character_id: Optional[int] = field(default=None)
    rank: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    next_stage_challenge_point: Optional[int] = field(default=None)
    complete_stage_resource_box_id: Optional[int] = field(default=None)
    complete_stage_character_exp: Optional[int] = field(default=None)


@dataclass(slots=True)
class ChallengeLiveStageEx:
    id: Optional[int] = field(default=None)
    character_id: Optional[int] = field(default=None)
    from_rank: Optional[int] = field(default=None)
    to_rank: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    next_stage_challenge_point: Optional[int] = field(default=None)
    complete_stage_resource_box_id: Optional[int] = field(default=None)
    complete_stage_character_exp: Optional[int] = field(default=None)


@dataclass(slots=True)
class ChallengeLiveHighScoreReward:
    id: Optional[int] = field(default=None)
    character_id: Optional[int] = field(default=None)
    high_score: Optional[int] = field(default=None)
    resource_box_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class ChallengeLiveCharacter:
    id: Optional[int] = field(default=None)
    character_id: Optional[int] = field(default=None)
    release_condition_id: Optional[int] = field(default=None)
    or_release_condition_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class ChallengeLivePlayDayReward:
    id: Optional[int] = field(default=None)
    challenge_live_play_day_reward_period_id: Optional[int] = field(default=None)
    play_days: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    resource_box_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class ChallengeLivePlayDayRewardPeriod:
    id: Optional[int] = field(default=None)
    start_at: Optional[datetime] = field(default=None)
    end_at: Optional[datetime] = field(default=None)
    priority: Optional[int] = field(default=None)
    challenge_live_play_day_rewards: Optional[list[ChallengeLivePlayDayReward]] = field(
        default=None
    )


@dataclass(slots=True)
class VirtualLiveSetlist:
    id: Optional[int] = field(default=None)
    virtual_live_id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    virtual_live_setlist_type: Optional[Union[VirtualLiveSetlistType, Unknown]] = field(
        default=None
    )
    asset_bundle_name: Optional[str] = field(default=None)
    virtual_live_stage_id: Optional[int] = field(default=None)
    music_id: Optional[int] = field(default=None)
    music_vocal_id: Optional[int] = field(default=None)
    character3d_id1: Optional[int] = field(default=None)
    character3d_id2: Optional[int] = field(default=None)
    character3d_id3: Optional[int] = field(default=None)
    character3d_id4: Optional[int] = field(default=None)
    character3d_id5: Optional[int] = field(default=None)
    character3d_id6: Optional[int] = field(default=None)


@dataclass(slots=True)
class VirtualLiveBeginnerSchedule:
    id: Optional[int] = field(default=None)
    virtual_live_id: Optional[int] = field(default=None)
    day_of_week: Optional[Union[DayOfWeek, Unknown]] = field(default=None)
    start_time: Optional[str] = field(default=None)
    end_time: Optional[str] = field(default=None)


@dataclass(slots=True)
class VirtualLiveSchedule:
    id: Optional[int] = field(default=None)
    virtual_live_id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    start_at: Optional[datetime] = field(default=None)
    end_at: Optional[datetime] = field(default=None)
    notice_group_id: Optional[str] = field(default=None)


@dataclass(slots=True)
class VirtualLiveCharacter:
    id: Optional[int] = field(default=None)
    virtual_live_id: Optional[int] = field(default=None)
    game_character_unit_id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)


@dataclass(slots=True)
class VirtualLiveReward:
    id: Optional[int] = field(default=None)
    virtual_live_type: Optional[Union[VirtualLiveType, Unknown]] = field(default=None)
    virtual_live_id: Optional[int] = field(default=None)
    resource_box_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class VirtualLiveWaitingRoom:
    id: Optional[int] = field(default=None)
    virtual_live_id: Optional[int] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    start_at: Optional[datetime] = field(default=None)
    end_at: Optional[datetime] = field(default=None)
    lobby_asset_bundle_name: Optional[str] = field(default=None)


@dataclass(slots=True)
class VirtualItem:
    id: Optional[int] = field(default=None)
    virtual_item_category: Optional[Union[VirtualItemCategory, Unknown]] = field(
        default=None
    )
    seq: Optional[int] = field(default=None)
    priority: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    cost_virtual_coin: Optional[int] = field(default=None)
    cost_jewel: Optional[int] = field(default=None)
    cheer_point: Optional[int] = field(default=None)
    effect_asset_bundle_name: Optional[str] = field(default=None)
    effect_expression_type: Optional[Union[EffectExpressionType, Unknown]] = field(
        default=None
    )
    unit: Optional[Union[Unit, Unknown]] = field(default=None)
    game_character_unit_id: Optional[int] = field(default=None)
    virtual_item_label_type: Optional[Union[VirtualItemLabelType, Unknown]] = field(
        default=None
    )


@dataclass(slots=True)
class VirtualLiveAppeal:
    id: Optional[int] = field(default=None)
    virtual_live_id: Optional[int] = field(default=None)
    virtual_live_stage_status: Optional[Union[VirtualLiveStageStatus, Unknown]] = field(
        default=None
    )
    appeal_text: Optional[str] = field(default=None)


@dataclass(slots=True)
class VirtualLiveInformation:
    virtual_live_id: Optional[int] = field(default=None)
    summary: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)


@dataclass(slots=True)
class VirtualLive:
    id: Optional[int] = field(default=None)
    virtual_live_type: Optional[Union[VirtualLiveType, Unknown]] = field(default=None)
    virtual_live_platform: Optional[str] = field(default=None)
    seq: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    screen_mv_music_vocal_id: Optional[int] = field(default=None)
    start_at: Optional[datetime] = field(default=None)
    end_at: Optional[datetime] = field(default=None)
    ranking_announce_at: Optional[datetime] = field(default=None)
    virtual_live_setlists: Optional[list[VirtualLiveSetlist]] = field(default=None)
    virtual_live_beginner_schedules: Optional[
        list[VirtualLiveBeginnerSchedule]
    ] = field(default=None)
    virtual_live_schedules: Optional[list[VirtualLiveSchedule]] = field(default=None)
    virtual_live_characters: Optional[list[VirtualLiveCharacter]] = field(default=None)
    virtual_live_reward: Optional[VirtualLiveReward] = field(default=None)
    virtual_live_rewards: Optional[list[VirtualLiveReward]] = field(default=None)
    virtual_live_cheer_point_rewards: Optional[list[Union[dict, str, int]]] = field(
        default=None
    )
    virtual_live_waiting_room: Optional[VirtualLiveWaitingRoom] = field(default=None)
    virtual_items: Optional[list[VirtualItem]] = field(default=None)
    virtual_live_appeals: Optional[list[VirtualLiveAppeal]] = field(default=None)
    virtual_live_information: Optional[VirtualLiveInformation] = field(default=None)
    archive_release_condition_id: Optional[int] = field(default=None)
    virtual_live_ticket_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class VirtualShopItem:
    id: Optional[int] = field(default=None)
    virtual_shop_id: Optional[int] = field(default=None)
    virtual_shop_item_type: Optional[Union[VirtualShopItemType, Unknown]] = field(
        default=None
    )
    seq: Optional[int] = field(default=None)
    resource_box_id: Optional[int] = field(default=None)
    cost_virtual_coin: Optional[int] = field(default=None)
    cost_jewel: Optional[int] = field(default=None)
    start_at: Optional[datetime] = field(default=None)
    cost_paid_jewel: Optional[int] = field(default=None)
    end_at: Optional[datetime] = field(default=None)
    limit_value: Optional[int] = field(default=None)


@dataclass(slots=True)
class VirtualShop:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    virtual_shop_items: Optional[list[VirtualShopItem]] = field(default=None)
    virtual_shop_type: Optional[Union[VirtualShopType, Unknown]] = field(default=None)
    virtual_live_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class VirtualLiveCheerMessage:
    id: Optional[int] = field(default=None)
    virtual_live_type: Optional[Union[VirtualLiveType, Unknown]] = field(default=None)
    resource_type: Optional[Union[ResourceType, Unknown]] = field(default=None)
    from_cost_virtual_coin: Optional[int] = field(default=None)
    to_cost_virtual_coin: Optional[int] = field(default=None)
    from_cost: Optional[int] = field(default=None)
    to_cost: Optional[int] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    message_length_limit: Optional[int] = field(default=None)
    display_sec: Optional[float] = field(default=None)
    message_size: Optional[str] = field(default=None)
    color_code: Optional[str] = field(default=None)
    virtual_live_cheer_message_display_limit_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class VirtualLiveCheerMessageDisplayLimit:
    id: Optional[int] = field(default=None)
    display_limit: Optional[int] = field(default=None)


@dataclass(slots=True)
class VirtualLiveTicket:
    id: Optional[int] = field(default=None)
    virtual_live_id: Optional[int] = field(default=None)
    virtual_live_ticket_type: Optional[Union[VirtualLiveTicketType, Unknown]] = field(
        default=None
    )
    name: Optional[str] = field(default=None)
    flavor_text: Optional[str] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)


@dataclass(slots=True)
class VirtualLivePamphlet:
    id: Optional[int] = field(default=None)
    virtual_live_id: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    flavor_text: Optional[str] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)


@dataclass(slots=True)
class AvatarAccessory:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    part: Optional[Union[AccessoryPart, Unknown]] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)


@dataclass(slots=True)
class AvatarCostume:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)


@dataclass(slots=True)
class AvatarMotion:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    sync_music_flg: Optional[bool] = field(default=None)
    repeat_count: Optional[int] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)


@dataclass(slots=True)
class AvatarSkinColor:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    color_code: Optional[str] = field(default=None)


@dataclass(slots=True)
class AvatarCoordinate:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    skin_color_code: Optional[str] = field(default=None)
    costume_asset_bundle_name: Optional[str] = field(default=None)
    accessory_part: Optional[Union[AccessoryPart, Unknown]] = field(default=None)
    accessory_asset_bundle_name: Optional[str] = field(default=None)


@dataclass(slots=True)
class NgWord:
    id: Optional[int] = field(default=None)
    word: Optional[str] = field(default=None)


@dataclass(slots=True)
class RuleSlide:
    id: Optional[int] = field(default=None)
    rule_slide_type: Optional[Union[RuleSlideType, Unknown]] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)


@dataclass(slots=True)
class Facility:
    id: Optional[int] = field(default=None)
    facility_type: Optional[Union[FacilityType, Unknown]] = field(default=None)
    release_condition_id: Optional[int] = field(default=None)
    and_release_condition_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class OneTimeBehavior:
    id: Optional[int] = field(default=None)
    one_time_behavior_type: Optional[Union[OneTimeBehaviorType, Unknown]] = field(
        default=None
    )
    release_condition_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class LoginBonus:
    id: Optional[int] = field(default=None)
    day: Optional[int] = field(default=None)
    resource_box_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class BeginnerLoginBonus:
    id: Optional[int] = field(default=None)
    day: Optional[int] = field(default=None)
    resource_box_id: Optional[int] = field(default=None)
    login_bonus_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class BeginnerLoginBonusSummary:
    id: Optional[int] = field(default=None)
    login_bonus_id: Optional[int] = field(default=None)
    start_at: Optional[datetime] = field(default=None)
    end_at: Optional[datetime] = field(default=None)


@dataclass(slots=True)
class LimitedLoginBonusDetail:
    id: Optional[int] = field(default=None)
    limited_login_bonus_id: Optional[int] = field(default=None)
    day: Optional[int] = field(default=None)
    resource_box_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class LimitedLoginBonus:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    start_at: Optional[datetime] = field(default=None)
    end_at: Optional[datetime] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    close_at: Optional[datetime] = field(default=None)
    limited_login_bonus_details: Optional[list[LimitedLoginBonusDetail]] = field(
        default=None
    )


@dataclass(slots=True)
class LoginBonusLive2d(Live2d):
    serif: Optional[str] = field(default=None)
    voice: Optional[str] = field(default=None)
    published_at: Optional[datetime] = field(default=None)
    closed_at: Optional[datetime] = field(default=None)


@dataclass(slots=True)
class EventRankingReward:
    id: Optional[int] = field(default=None)
    event_ranking_reward_range_id: Optional[int] = field(default=None)
    resource_box_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class EventRankingRewardRange:
    id: Optional[int] = field(default=None)
    event_id: Optional[int] = field(default=None)
    from_rank: Optional[int] = field(default=None)
    to_rank: Optional[int] = field(default=None)
    event_ranking_rewards: Optional[list[EventRankingReward]] = field(default=None)


@dataclass(slots=True)
class Event:
    id: Optional[int] = field(default=None)
    event_type: Optional[Union[EventType, Unknown]] = field(default=None)
    name: Optional[str] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    bgm_asset_bundle_name: Optional[str] = field(default=None)
    start_at: Optional[datetime] = field(default=None)
    aggregate_at: Optional[datetime] = field(default=None)
    ranking_announce_at: Optional[datetime] = field(default=None)
    distribution_start_at: Optional[datetime] = field(default=None)
    closed_at: Optional[datetime] = field(default=None)
    distribution_end_at: Optional[datetime] = field(default=None)
    virtual_live_id: Optional[int] = field(default=None)
    unit: Optional[Union[Unit, Unknown]] = field(default=None)
    event_ranking_reward_ranges: Optional[list[EventRankingRewardRange]] = field(
        default=None
    )
    event_point_asset_bundle_name: Optional[str] = field(default=None)


@dataclass(slots=True)
class EventMusic:
    event_id: Optional[int] = field(default=None)
    music_id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    release_condition_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class EventDeckBonus:
    id: Optional[int] = field(default=None)
    event_id: Optional[int] = field(default=None)
    game_character_unit_id: Optional[int] = field(default=None)
    card_attr: Optional[Union[CardAttr, Unknown]] = field(default=None)
    bonus_rate: Optional[float] = field(default=None)


@dataclass(slots=True)
class EventRarityBonusRate:
    id: Optional[int] = field(default=None)
    card_rarity_type: Optional[Union[CardRarityType, Unknown]] = field(default=None)
    master_rank: Optional[int] = field(default=None)
    bonus_rate: Optional[float] = field(default=None)


@dataclass(slots=True)
class EventItem:
    id: Optional[int] = field(default=None)
    event_id: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    flavor_text: Optional[str] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)


@dataclass(slots=True)
class EpisodeReward:
    story_type: Optional[Union[StoryType, Unknown]] = field(default=None)
    resource_box_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class EventStoryEpisode:
    id: Optional[int] = field(default=None)
    event_story_id: Optional[int] = field(default=None)
    episode_no: Optional[int] = field(default=None)
    title: Optional[str] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    scenario_id: Optional[str] = field(default=None)
    release_condition_id: Optional[int] = field(default=None)
    episode_rewards: Optional[list[EpisodeReward]] = field(default=None)


@dataclass(slots=True)
class EventStory:
    id: Optional[int] = field(default=None)
    event_id: Optional[int] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    event_story_episodes: Optional[list[EventStoryEpisode]] = field(default=None)


@dataclass(slots=True)
class EventExchangeCost(Cost):
    id: Optional[int] = field(default=None)
    event_exchange_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class EventExchange:
    id: Optional[int] = field(default=None)
    event_exchange_summary_id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    resource_box_id: Optional[int] = field(default=None)
    exchange_limit: Optional[int] = field(default=None)
    event_exchange_cost: Optional[EventExchangeCost] = field(default=None)


@dataclass(slots=True)
class EventExchangeSummary:
    id: Optional[int] = field(default=None)
    event_id: Optional[int] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    start_at: Optional[datetime] = field(default=None)
    end_at: Optional[datetime] = field(default=None)
    event_exchanges: Optional[list[EventExchange]] = field(default=None)


@dataclass(slots=True)
class EventStoryUnit:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    event_story_id: Optional[int] = field(default=None)
    unit: Optional[Union[Unit, Unknown]] = field(default=None)
    event_story_unit_relation: Optional[Union[EventStoryUnitRelation, Unknown]] = field(
        default=None
    )


@dataclass(slots=True)
class EventCard:
    id: Optional[int] = field(default=None)
    card_id: Optional[int] = field(default=None)
    event_id: Optional[int] = field(default=None)
    bonus_rate: Optional[float] = field(default=None)


@dataclass(slots=True)
class PreliminaryTournamentCard:
    id: Optional[int] = field(default=None)
    preliminary_tournament_id: Optional[int] = field(default=None)
    card_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class PreliminaryTournamentMusic:
    id: Optional[int] = field(default=None)
    preliminary_tournament_id: Optional[int] = field(default=None)
    music_difficulty_id: Optional[int] = field(default=None)
    music_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class PreliminaryTournament:
    id: Optional[int] = field(default=None)
    preliminary_tournament_type: Optional[
        Union[PreliminaryTournamentType, Unknown]
    ] = field(default=None)
    start_at: Optional[datetime] = field(default=None)
    end_at: Optional[datetime] = field(default=None)
    release_condition_id: Optional[int] = field(default=None)
    preliminary_tournament_cards: Optional[list[PreliminaryTournamentCard]] = field(
        default=None
    )
    preliminary_tournament_musics: Optional[list[PreliminaryTournamentMusic]] = field(
        default=None
    )


@dataclass(slots=True)
class CheerfulCarnivalSummary:
    id: Optional[int] = field(default=None)
    event_id: Optional[int] = field(default=None)
    theme: Optional[str] = field(default=None)
    midterm_announce1_at: Optional[datetime] = field(default=None)
    midterm_announce2_at: Optional[datetime] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)


@dataclass(slots=True)
class CheerfulCarnivalTeam:
    id: Optional[int] = field(default=None)
    event_id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    team_name: Optional[str] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)


@dataclass(slots=True)
class CheerfulCarnivalPartyName:
    id: Optional[int] = field(default=None)
    party_name: Optional[str] = field(default=None)
    game_character_unit_id1: Optional[int] = field(default=None)
    game_character_unit_id2: Optional[int] = field(default=None)
    game_character_unit_id3: Optional[int] = field(default=None)
    game_character_unit_id4: Optional[int] = field(default=None)
    game_character_unit_id5: Optional[int] = field(default=None)


@dataclass(slots=True)
class CheerfulCarnivalCharacterPartyName:
    id: Optional[int] = field(default=None)
    character_party_name: Optional[str] = field(default=None)
    game_character_unit_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class CheerfulCarnivalLiveTeamPointBonus:
    id: Optional[int] = field(default=None)
    team_point_bonus_rate: Optional[int] = field(default=None)


@dataclass(slots=True)
class CheerfulCarnivalReward:
    id: Optional[int] = field(default=None)
    event_id: Optional[int] = field(default=None)
    cheerful_carnival_team_id: Optional[int] = field(default=None)
    resource_box_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class CheerfulCarnivalResultReward:
    id: Optional[int] = field(default=None)
    event_id: Optional[int] = field(default=None)
    cheerful_carnival_team_point_term_type: Optional[
        Union[CheerfulCarnivalTeamPointTermType, Unknown]
    ] = field(default=None)
    cheerful_carnival_result_type: Optional[
        Union[CheerfulCarnivalResultType, Unknown]
    ] = field(default=None)
    resource_box_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class Appeal:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    appeal_target_type: Optional[Union[AppealTargetType, Unknown]] = field(default=None)
    appeal_type: Optional[Union[AppealType, Unknown]] = field(default=None)
    start_at: Optional[datetime] = field(default=None)
    end_at: Optional[datetime] = field(default=None)
    appeal_read_condition_type: Optional[
        Union[AppealReadConditionType, Unknown]
    ] = field(default=None)
    text: Optional[str] = field(default=None)


@dataclass(slots=True)
class Boost:
    id: Optional[int] = field(default=None)
    cost_boost: Optional[int] = field(default=None)
    is_event_only: Optional[bool] = field(default=None)
    exp_rate: Optional[int] = field(default=None)
    reward_rate: Optional[int] = field(default=None)
    live_point_rate: Optional[int] = field(default=None)
    event_point_rate: Optional[int] = field(default=None)
    bonds_exp_rate: Optional[int] = field(default=None)


@dataclass(slots=True)
class BoostPresent:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    recovery_value: Optional[int] = field(default=None)
    present_limit: Optional[int] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    is_unlimited_receive: Optional[bool] = field(default=None)
    boost_present_cost_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class BoostPresentCost(Cost):
    id: Optional[int] = field(default=None)


@dataclass(slots=True)
class EpisodeCharacter:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    character2d_id: Optional[int] = field(default=None)
    story_type: Optional[Union[StoryType, Unknown]] = field(default=None)
    episode_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class CustomProfileTextColor:
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    color_code: Optional[str] = field(default=None)


@dataclass(slots=True)
class CustomProfileTextFont:
    id: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    font_name: Optional[str] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)


@dataclass(slots=True)
class CustomProfileResource:
    custom_profile_resource_type: Optional[
        Union[CustomProfileResourceType, Unknown]
    ] = field(default=None)
    id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    resource_load_type: Optional[Union[ResourceLoadType, Unknown]] = field(default=None)
    resource_load_val: Optional[str] = field(default=None)
    file_name: Optional[str] = field(default=None)


@dataclass(slots=True)
class CustomProfilePlayerInfoResource(CustomProfileResource):
    pass


@dataclass(slots=True)
class CustomProfileGeneralBackgroundResource(CustomProfileResource):
    pass


@dataclass(slots=True)
class CustomProfileStoryBackgroundResource(CustomProfileResource):
    pass


@dataclass(slots=True)
class CustomProfileCollectionResource(CustomProfileResource):
    custom_profile_resource_collection_type: Optional[
        Union[CustomProfileResourceCollectionType, Unknown]
    ] = field(default=None)
    group_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class CustomProfileMemberStandingPictureResource(CustomProfileResource):
    character_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class CustomProfileShapeResource(CustomProfileResource):
    pass


@dataclass(slots=True)
class CustomProfileEtcResource(CustomProfileResource):
    pass


@dataclass(slots=True)
class CustomProfileGachaBehavior:
    id: Optional[int] = field(default=None)
    custom_profile_gacha_id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    cost_resource_type: Optional[Union[ResourceType, Unknown]] = field(default=None)
    cost_resource_quantity: Optional[int] = field(default=None)
    spin_count: Optional[int] = field(default=None)


@dataclass(slots=True)
class CustomProfileGachaDetail:
    id: Optional[int] = field(default=None)
    custom_profile_gacha_id: Optional[int] = field(default=None)
    custom_profile_resource_type: Optional[
        Union[CustomProfileResourceType, Unknown]
    ] = field(default=None)
    custom_profile_resource_id: Optional[int] = field(default=None)
    custom_profile_resource_quantity: Optional[int] = field(default=None)
    weight: Optional[int] = field(default=None)


@dataclass(slots=True)
class CustomProfileGacha:
    id: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    start_at: Optional[datetime] = field(default=None)
    end_at: Optional[datetime] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)
    notice: Optional[str] = field(default=None)
    custom_profile_gacha_behaviors: Optional[list[CustomProfileGachaBehavior]] = field(
        default=None
    )
    custom_profile_gacha_details: Optional[list[CustomProfileGachaDetail]] = field(
        default=None
    )


@dataclass(slots=True)
class StreamingLiveBgm:
    id: Optional[int] = field(default=None)
    virtual_live_id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    music_vocal_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class Omikuji:
    id: Optional[int] = field(default=None)
    omikuji_group_id: Optional[int] = field(default=None)
    unit: Optional[Union[Unit, Unknown]] = field(default=None)
    fortune_type: Optional[Union[FortuneType, Unknown]] = field(default=None)
    summary: Optional[str] = field(default=None)
    title1: Optional[str] = field(default=None)
    description1: Optional[str] = field(default=None)
    title2: Optional[str] = field(default=None)
    description2: Optional[str] = field(default=None)
    title3: Optional[str] = field(default=None)
    description3: Optional[str] = field(default=None)
    unit_asset_bundle_name: Optional[str] = field(default=None)
    fortune_asset_bundle_name: Optional[str] = field(default=None)
    omikuji_cover_asset_bundle_name: Optional[str] = field(default=None)
    unit_file_path: Optional[str] = field(default=None)
    fortune_file_path: Optional[str] = field(default=None)
    omikuji_cover_file_path: Optional[str] = field(default=None)


@dataclass(slots=True)
class OmikujiGroup:
    id: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    summary: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    appeal_asset_bundle_name: Optional[str] = field(default=None)
    sound_asset_bundle_name: Optional[str] = field(default=None)


@dataclass(slots=True)
class OmikujiRate:
    id: Optional[int] = field(default=None)
    omikuji_group_id: Optional[int] = field(default=None)
    fortune_type: Optional[Union[FortuneType, Unknown]] = field(default=None)
    rate: Optional[float] = field(default=None)


@dataclass(slots=True)
class OmikujiCost(Cost):
    id: Optional[int] = field(default=None)
    omikuji_group_id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)


@dataclass(slots=True)
class OmikujiReward:
    id: Optional[int] = field(default=None)
    omikuji_group_id: Optional[int] = field(default=None)
    seq: Optional[int] = field(default=None)
    resource_type: Optional[Union[ResourceType, Unknown]] = field(default=None)
    resource_id: Optional[int] = field(default=None)
    resource_quantity: Optional[int] = field(default=None)


@dataclass(slots=True)
class VirtualBoothShop:
    id: Optional[int] = field(default=None)
    virtual_live_id: Optional[int] = field(default=None)
    virtual_booth_shop_type: Optional[Union[VirtualBoothShopType, Unknown]] = field(
        default=None
    )
    target_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class SpecialSeason:
    id: Optional[int] = field(default=None)
    special_season_type: Optional[Union[SpecialSeasonType, Unknown]] = field(
        default=None
    )
    start_at: Optional[datetime] = field(default=None)
    end_at: Optional[datetime] = field(default=None)
    priority: Optional[int] = field(default=None)


@dataclass(slots=True)
class SpecialSeasonArea:
    id: Optional[int] = field(default=None)
    special_season_id: Optional[int] = field(default=None)
    area_id: Optional[int] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    file_name: Optional[str] = field(default=None)
    special_season_area_use_type: Optional[
        Union[SpecialSeasonAreaUseType, Unknown]
    ] = field(default=None)


@dataclass(slots=True)
class RankMatchPenalty:
    id: Optional[int] = field(default=None)
    count: Optional[int] = field(default=None)
    rank_match_penalty_type: Optional[Union[RankMatchPenaltyType, Unknown]] = field(
        default=None
    )
    rank_match_penalty_type_value: Optional[int] = field(default=None)


@dataclass(slots=True)
class RankMatchPlacement:
    id: Optional[int] = field(default=None)
    rank_match_placement_condition_type: Optional[str] = field(default=None)
    tier_behavior_type: Optional[Union[TierBehaviorType, Unknown]] = field(default=None)
    tier_behavior_type_value: Optional[int] = field(default=None)
    rank_match_placement_condition_type_value: Optional[int] = field(default=None)


@dataclass(slots=True)
class RankMatchBonusPointCondition:
    id: Optional[int] = field(default=None)
    rank_match_bonus_point_condition_type: Optional[
        Union[RankMatchBonusPointConditionType, Unknown]
    ] = field(default=None)
    group_id: Optional[int] = field(default=None)
    priority: Optional[int] = field(default=None)
    calc_type: Optional[Union[CalcType, Unknown]] = field(default=None)
    bonus_point: Optional[int] = field(default=None)


@dataclass(slots=True)
class RankMatchSeasonPlayableTime:
    id: Optional[int] = field(default=None)
    rank_match_season_id: Optional[int] = field(default=None)
    start_time: Optional[str] = field(default=None)
    end_time: Optional[str] = field(default=None)


@dataclass(slots=True)
class RankMatchSeasonTierMusicPlayLevel:
    id: Optional[int] = field(default=None)
    rank_match_season_id: Optional[int] = field(default=None)
    rank_match_tier_id: Optional[int] = field(default=None)
    from_play_level: Optional[int] = field(default=None)
    to_play_level: Optional[int] = field(default=None)


@dataclass(slots=True)
class RankMatchSeasonTierReward:
    id: Optional[int] = field(default=None)
    rank_match_season_id: Optional[int] = field(default=None)
    rank_match_tier_id: Optional[int] = field(default=None)
    resource_box_id: Optional[int] = field(default=None)


@dataclass(slots=True)
class RankMatchSeason:
    id: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    start_at: Optional[datetime] = field(default=None)
    aggregated_at: Optional[datetime] = field(default=None)
    ranking_published_at: Optional[datetime] = field(default=None)
    batch_execution_at: Optional[datetime] = field(default=None)
    distribution_start_at: Optional[datetime] = field(default=None)
    distribution_end_at: Optional[datetime] = field(default=None)
    closed_at: Optional[datetime] = field(default=None)
    asset_bundle_name: Optional[str] = field(default=None)
    is_display_result: Optional[bool] = field(default=None)
    rank_match_season_playable_times: Optional[
        list[RankMatchSeasonPlayableTime]
    ] = field(default=None)
    rank_match_season_tier_music_play_levels: Optional[
        list[RankMatchSeasonTierMusicPlayLevel]
    ] = field(default=None)
    rank_match_season_tier_rewards: Optional[list[RankMatchSeasonTierReward]] = field(
        default=None
    )


@dataclass(slots=True)
class RankMatchTier:
    id: Optional[int] = field(default=None)
    rank_match_grade_id: Optional[int] = field(default=None)
    rank_match_class_id: Optional[int] = field(default=None)
    tier: Optional[int] = field(default=None)
    total_music_difficulty: Optional[int] = field(default=None)
    point: Optional[int] = field(default=None)
    grade_asset_bundle_name: Optional[str] = field(default=None)
    tier_asset_bundle_name: Optional[str] = field(default=None)


@dataclass(slots=True)
class RankMatchTierBonusPoint:
    id: Optional[int] = field(default=None)
    rank_match_tier_id: Optional[int] = field(default=None)
    max_bonus_point: Optional[int] = field(default=None)
    reward_point: Optional[int] = field(default=None)


@dataclass(slots=True)
class RankMatchGrade(Costume2dGroup):
    id: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)


@dataclass(slots=True)
class RankMatchClass(Costume2dGroup):
    id: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)


@dataclass(slots=True)
class LimitedTitleScreen:
    id: Optional[int] = field(default=None)
    priority: Optional[int] = field(default=None)
    download_start_at: Optional[datetime] = field(default=None)
    download_end_at: Optional[datetime] = field(default=None)
    display_start_at: Optional[datetime] = field(default=None)
    display_end_at: Optional[datetime] = field(default=None)
    bg_asset_bundle_name: Optional[str] = field(default=None)
    logo_asset_bundle_name: Optional[str] = field(default=None)
    bgm_asset_bundle_name: Optional[str] = field(default=None)
    start_effect_asset_bundle_name: Optional[str] = field(default=None)


T_MasterData = TypeVar("T_MasterData", bound="MasterData")


@dataclass(slots=True)
class MasterData:
    game_characters: Optional[list[GameCharacter]] = field(default=None)
    game_character_units: Optional[list[GameCharacterUnit]] = field(default=None)
    outside_characters: Optional[list[OutsideCharacter]] = field(default=None)
    character3ds: Optional[list[Character3d]] = field(default=None)
    character2ds: Optional[list[Character2d]] = field(default=None)
    character_profiles: Optional[list[CharacterProfile]] = field(default=None)
    bonds: Optional[list[Bond]] = field(default=None)
    bonds_live2ds: Optional[list[BondsLive2d]] = field(default=None)
    bonds_rank_up_live2ds: Optional[list[BondsRankUpLive2d]] = field(default=None)
    unit_profiles: Optional[list[UnitProfile]] = field(default=None)
    action_sets: Optional[list[ActionSet]] = field(default=None)
    areas: Optional[list[Area]] = field(default=None)
    area_playlists: Optional[list[AreaPlaylist]] = field(default=None)
    mob_characters: Optional[list[MobCharacter]] = field(default=None)
    character_costumes: Optional[list[CharacterCostume]] = field(default=None)
    card_costume3ds: Optional[list[CardCostume3d]] = field(default=None)
    cards: Optional[list[Card]] = field(default=None)
    skills: Optional[list[Skill]] = field(default=None)
    card_episodes: Optional[list[CardEpisode]] = field(default=None)
    card_rarities: Optional[list[CardRarity]] = field(default=None)
    card_skill_costs: Optional[list[CardSkillCost]] = field(default=None)
    musics: Optional[list[Music]] = field(default=None)
    music_tags: Optional[list[MusicTag]] = field(default=None)
    music_difficulties: Optional[list[MusicDifficulty]] = field(default=None)
    music_vocals: Optional[list[MusicVocal]] = field(default=None)
    music_dance_members: Optional[list[MusicDanceMember]] = field(default=None)
    music_achievements: Optional[list[MusicAchievement]] = field(default=None)
    music_video_characters: Optional[list[MusicVideoCharacter]] = field(default=None)
    music_asset_variants: Optional[list[MusicAssetVariant]] = field(default=None)
    music_collaborations: Optional[list[MusicCollaboration]] = field(default=None)
    episode_music_video_costumes: Optional[list[EpisodeMusicVideoCostume]] = field(
        default=None
    )
    release_conditions: Optional[list[ReleaseCondition]] = field(default=None)
    play_level_scores: Optional[list[PlayLevelScore]] = field(default=None)
    ingame_combos: Optional[list[IngameCombo]] = field(default=None)
    ingame_notes: Optional[list[IngameNote]] = field(default=None)
    ingame_note_judges: Optional[list[IngameNoteJudge]] = field(default=None)
    ingame_play_levels: Optional[list[IngamePlayLevel]] = field(default=None)
    ingame_cutins: Optional[list[IngameCutin]] = field(default=None)
    ingame_cutin_characters: Optional[list[IngameCutinCharacter]] = field(default=None)
    ingame_judge_frames: Optional[list[IngameJudgeFrame]] = field(default=None)
    ingame_note_judge_technical_scores: Optional[
        list[IngameNoteJudgeTechnicalScore]
    ] = field(default=None)
    shops: Optional[list[Shop]] = field(default=None)
    shop_items: Optional[list[ShopItem]] = field(default=None)
    costume3d_shop_items: Optional[list[Costume3dShopItem]] = field(default=None)
    area_items: Optional[list[AreaItem]] = field(default=None)
    area_item_levels: Optional[list[AreaItemLevel]] = field(default=None)
    materials: Optional[list[Material]] = field(default=None)
    gachas: Optional[list[Gacha]] = field(default=None)
    gacha_bonuses: Optional[list[GachaBonus]] = field(default=None)
    gacha_bonus_points: Optional[list[GachaBonusPoint]] = field(default=None)
    gacha_extras: Optional[list[GachaExtra]] = field(default=None)
    gift_gacha_exchanges: Optional[list[GiftGachaExchange]] = field(default=None)
    gacha_tabs: Optional[list[Union[dict, str, int]]] = field(default=None)
    practice_tickets: Optional[list[PracticeTicket]] = field(default=None)
    skill_practice_tickets: Optional[list[SkillPracticeTicket]] = field(default=None)
    levels: Optional[list[Level]] = field(default=None)
    unit_stories: Optional[list[UnitStory]] = field(default=None)
    special_stories: Optional[list[SpecialStory]] = field(default=None)
    configs: Optional[list[Config]] = field(default=None)
    client_configs: Optional[list[ClientConfig]] = field(default=None)
    wordings: Optional[list[Wording]] = field(default=None)
    costume3ds: Optional[list[Costume3d]] = field(default=None)
    costume3d_models: Optional[list[Costume3dModel]] = field(default=None)
    costume3d_model_available_patterns: Optional[
        list[Costume3dModelAvailablePattern]
    ] = field(default=None)
    game_character_unit3d_motions: Optional[list[GameCharacterUnit3dMotion]] = field(
        default=None
    )
    costume2ds: Optional[list[Costume2d]] = field(default=None)
    costume2d_groups: Optional[list[Costume2dGroup]] = field(default=None)
    topics: Optional[list[Topic]] = field(default=None)
    live_stages: Optional[list[LiveStage]] = field(default=None)
    stamps: Optional[list[Stamp]] = field(default=None)
    multi_live_lobbies: Optional[list[MultiLiveLobby]] = field(default=None)
    master_lessons: Optional[list[MasterLesson]] = field(default=None)
    master_lesson_rewards: Optional[list[MasterLessonReward]] = field(default=None)
    card_exchange_resources: Optional[list[CardExchangeResource]] = field(default=None)
    material_exchanges: Optional[list[MaterialExchange]] = field(default=None)
    material_exchange_summaries: Optional[list[MaterialExchangeSummary]] = field(
        default=None
    )
    boost_items: Optional[list[BoostItem]] = field(default=None)
    billing_products: Optional[list[BillingProduct]] = field(default=None)
    billing_shop_items: Optional[list[BillingShopItem]] = field(default=None)
    billing_shop_item_exchange_costs: Optional[
        list[BillingShopItemExchangeCost]
    ] = field(default=None)
    colorful_passes: Optional[list[ColorfulPass]] = field(default=None)
    jewel_behaviors: Optional[list[JewelBehavior]] = field(default=None)
    character_ranks: Optional[list[CharacterRank]] = field(default=None)
    character_mission_v2s: Optional[list[CharacterMissionV2]] = field(default=None)
    character_mission_v2_parameter_groups: Optional[
        list[CharacterMissionV2ParameterGroup]
    ] = field(default=None)
    character_mission_v2_area_items: Optional[list[CharacterMissionV2AreaItem]] = field(
        default=None
    )
    system_live2ds: Optional[list[SystemLive2d]] = field(default=None)
    normal_missions: Optional[list[NormalMission]] = field(default=None)
    beginner_missions: Optional[list[BeginnerMission]] = field(default=None)
    resource_boxes: Optional[list[ResourceBox]] = field(default=None)
    live_mission_periods: Optional[list[LiveMissionPeriod]] = field(default=None)
    live_missions: Optional[list[LiveMission]] = field(default=None)
    live_mission_passes: Optional[list[LiveMissionPass]] = field(default=None)
    penlight_colors: Optional[list[PenlightColor]] = field(default=None)
    penlights: Optional[list[Penlight]] = field(default=None)
    live_talks: Optional[list[LiveTalk]] = field(default=None)
    tips: Optional[list[Tip]] = field(default=None)
    gacha_ceil_items: Optional[list[GachaCeilItem]] = field(default=None)
    gacha_ceil_exchange_summaries: Optional[list[GachaCeilExchangeSummary]] = field(
        default=None
    )
    player_rank_rewards: Optional[list[PlayerRankReward]] = field(default=None)
    gacha_tickets: Optional[list[GachaTicket]] = field(default=None)
    honor_groups: Optional[list[HonorGroup]] = field(default=None)
    honors: Optional[list[Honor]] = field(default=None)
    honor_missions: Optional[list[HonorMission]] = field(default=None)
    bonds_honors: Optional[list[BondsHonor]] = field(default=None)
    bonds_honor_words: Optional[list[BondsHonorWord]] = field(default=None)
    bonds_rewards: Optional[list[BondsReward]] = field(default=None)
    challenge_lives: Optional[list[ChallengeLive]] = field(default=None)
    challenge_live_decks: Optional[list[ChallengeLiveDeck]] = field(default=None)
    challenge_live_stages: Optional[list[ChallengeLiveStage]] = field(default=None)
    challenge_live_stage_exs: Optional[list[ChallengeLiveStageEx]] = field(default=None)
    challenge_live_high_score_rewards: Optional[
        list[ChallengeLiveHighScoreReward]
    ] = field(default=None)
    challenge_live_characters: Optional[list[ChallengeLiveCharacter]] = field(
        default=None
    )
    challenge_live_play_day_reward_periods: Optional[
        list[ChallengeLivePlayDayRewardPeriod]
    ] = field(default=None)
    virtual_lives: Optional[list[VirtualLive]] = field(default=None)
    virtual_shops: Optional[list[VirtualShop]] = field(default=None)
    virtual_items: Optional[list[VirtualItem]] = field(default=None)
    virtual_live_cheer_messages: Optional[list[VirtualLiveCheerMessage]] = field(
        default=None
    )
    virtual_live_cheer_message_display_limits: Optional[
        list[VirtualLiveCheerMessageDisplayLimit]
    ] = field(default=None)
    virtual_live_tickets: Optional[list[VirtualLiveTicket]] = field(default=None)
    virtual_live_pamphlets: Optional[list[VirtualLivePamphlet]] = field(default=None)
    avatar_accessories: Optional[list[AvatarAccessory]] = field(default=None)
    avatar_costumes: Optional[list[AvatarCostume]] = field(default=None)
    avatar_motions: Optional[list[AvatarMotion]] = field(default=None)
    avatar_skin_colors: Optional[list[AvatarSkinColor]] = field(default=None)
    avatar_coordinates: Optional[list[AvatarCoordinate]] = field(default=None)
    ng_words: Optional[list[NgWord]] = field(default=None)
    rule_slides: Optional[list[RuleSlide]] = field(default=None)
    facilities: Optional[list[Facility]] = field(default=None)
    one_time_behaviors: Optional[list[OneTimeBehavior]] = field(default=None)
    login_bonuses: Optional[list[LoginBonus]] = field(default=None)
    beginner_login_bonuses: Optional[list[BeginnerLoginBonus]] = field(default=None)
    beginner_login_bonus_summaries: Optional[list[BeginnerLoginBonusSummary]] = field(
        default=None
    )
    limited_login_bonuses: Optional[list[LimitedLoginBonus]] = field(default=None)
    login_bonus_live2ds: Optional[list[LoginBonusLive2d]] = field(default=None)
    events: Optional[list[Event]] = field(default=None)
    event_musics: Optional[list[EventMusic]] = field(default=None)
    event_deck_bonuses: Optional[list[EventDeckBonus]] = field(default=None)
    event_rarity_bonus_rates: Optional[list[EventRarityBonusRate]] = field(default=None)
    event_items: Optional[list[EventItem]] = field(default=None)
    event_stories: Optional[list[EventStory]] = field(default=None)
    event_exchange_summaries: Optional[list[EventExchangeSummary]] = field(default=None)
    event_story_units: Optional[list[EventStoryUnit]] = field(default=None)
    event_cards: Optional[list[EventCard]] = field(default=None)
    preliminary_tournaments: Optional[list[PreliminaryTournament]] = field(default=None)
    cheerful_carnival_summaries: Optional[list[CheerfulCarnivalSummary]] = field(
        default=None
    )
    cheerful_carnival_teams: Optional[list[CheerfulCarnivalTeam]] = field(default=None)
    cheerful_carnival_party_names: Optional[list[CheerfulCarnivalPartyName]] = field(
        default=None
    )
    cheerful_carnival_character_party_names: Optional[
        list[CheerfulCarnivalCharacterPartyName]
    ] = field(default=None)
    cheerful_carnival_live_team_point_bonuses: Optional[
        list[CheerfulCarnivalLiveTeamPointBonus]
    ] = field(default=None)
    cheerful_carnival_rewards: Optional[list[CheerfulCarnivalReward]] = field(
        default=None
    )
    cheerful_carnival_result_rewards: Optional[
        list[CheerfulCarnivalResultReward]
    ] = field(default=None)
    appeals: Optional[list[Appeal]] = field(default=None)
    boosts: Optional[list[Boost]] = field(default=None)
    boost_presents: Optional[list[BoostPresent]] = field(default=None)
    boost_present_costs: Optional[list[BoostPresentCost]] = field(default=None)
    episode_characters: Optional[list[EpisodeCharacter]] = field(default=None)
    custom_profile_text_colors: Optional[list[CustomProfileTextColor]] = field(
        default=None
    )
    custom_profile_text_fonts: Optional[list[CustomProfileTextFont]] = field(
        default=None
    )
    custom_profile_player_info_resources: Optional[
        list[CustomProfilePlayerInfoResource]
    ] = field(default=None)
    custom_profile_general_background_resources: Optional[
        list[CustomProfileGeneralBackgroundResource]
    ] = field(default=None)
    custom_profile_story_background_resources: Optional[
        list[CustomProfileStoryBackgroundResource]
    ] = field(default=None)
    custom_profile_collection_resources: Optional[
        list[CustomProfileCollectionResource]
    ] = field(default=None)
    custom_profile_member_standing_picture_resources: Optional[
        list[CustomProfileMemberStandingPictureResource]
    ] = field(default=None)
    custom_profile_shape_resources: Optional[list[CustomProfileShapeResource]] = field(
        default=None
    )
    custom_profile_etc_resources: Optional[list[CustomProfileEtcResource]] = field(
        default=None
    )
    custom_profile_member_resource_exclude_cards: Optional[
        list[Union[dict, str, int]]
    ] = field(default=None)
    custom_profile_gachas: Optional[list[CustomProfileGacha]] = field(default=None)
    custom_profile_gacha_tabs: Optional[list[Union[dict, str, int]]] = field(
        default=None
    )
    streaming_live_bgms: Optional[list[StreamingLiveBgm]] = field(default=None)
    omikujis: Optional[list[Omikuji]] = field(default=None)
    omikuji_groups: Optional[list[OmikujiGroup]] = field(default=None)
    omikuji_rates: Optional[list[OmikujiRate]] = field(default=None)
    omikuji_costs: Optional[list[OmikujiCost]] = field(default=None)
    omikuji_rewards: Optional[list[OmikujiReward]] = field(default=None)
    virtual_booth_shops: Optional[list[VirtualBoothShop]] = field(default=None)
    special_seasons: Optional[list[SpecialSeason]] = field(default=None)
    special_season_areas: Optional[list[SpecialSeasonArea]] = field(default=None)
    rank_match_penalties: Optional[list[RankMatchPenalty]] = field(default=None)
    rank_match_placements: Optional[list[RankMatchPlacement]] = field(default=None)
    rank_match_bonus_point_conditions: Optional[
        list[RankMatchBonusPointCondition]
    ] = field(default=None)
    rank_match_seasons: Optional[list[RankMatchSeason]] = field(default=None)
    rank_match_tiers: Optional[list[RankMatchTier]] = field(default=None)
    rank_match_tier_bonus_points: Optional[list[RankMatchTierBonusPoint]] = field(
        default=None
    )
    rank_match_grades: Optional[list[RankMatchGrade]] = field(default=None)
    rank_match_classes: Optional[list[RankMatchClass]] = field(default=None)
    limited_title_screens: Optional[list[LimitedTitleScreen]] = field(default=None)
    panel_mission_campaigns: Optional[list[Union[dict, str, int]]] = field(default=None)

    @classmethod
    def create(cls: Type[T_MasterData]) -> T_MasterData:
        return cls(**{field.name: None for field in fields(cls)})
