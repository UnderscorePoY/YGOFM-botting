from __future__ import annotations
import csv
from typing import Iterator

from probability_tree import Actions
from utils import *
from types_ import Type, Opponent, EndOfTurnType


class Domination:
    def __init__(self, *, find_best_combo: int, improve_monster: int, set_magic: int) \
            -> None:
        self.find_best_combo = find_best_combo
        self.improve_monster = improve_monster
        self.set_magic = set_magic


class AIStat:
    SEE_THROUGH = 0  # ATTACK_PERCENT

    def __init__(self, *, low_lp_threshold: int, critical_deck_size: int, max_fusion_length: int,
                 max_improve_length: int,
                 spell_percent: int, attack_percent: int,
                 total_domination: Domination, lacks_total_domination: Domination) \
            -> None:
        self.low_lp_threshold = low_lp_threshold
        self.critical_deck_size = critical_deck_size
        self.max_fusion_length = max_fusion_length
        self.max_improve_length = max_improve_length
        self.spell_percent = spell_percent
        self.attack_percent = attack_percent
        self.total_domination = total_domination
        self.lacks_total_domination = lacks_total_domination


ai_stats: dict[str, AIStat] | None = None


# Voluntary mutable argument, this emulates a singleton behaviour
def get_all_ai_stats(_ai_stats: dict[str, AIStat] | None = ai_stats,
                     csvdata_filename: str | None = 'YFM_AI-stats.csv') \
        -> dict[str, AIStat]:
    if _ai_stats is not None:
        return _ai_stats

    _ai_stats = {}
    with open(csvdata_filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)  # csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            _ai_stats[row['Opponent']] = AIStat(
                low_lp_threshold=int(row['Low LP Threshold']),
                critical_deck_size=int(row['Critical Deck Size']),
                max_fusion_length=int(row['Max Fusion Length']),
                max_improve_length=int(row['Max Improve Length']),
                spell_percent=int(row['Spell Probability'].split('%')[0]),
                attack_percent=int(row['Attack Probability'].split('%')[0]),
                total_domination=Domination(
                    find_best_combo=int(row['Total Domination FIND_BEST_COMBO'].split('%')[0]),
                    improve_monster=int(row['Total Domination IMPROVE_MONSTER'].split('%')[0]),
                    set_magic=int(row['Total Domination SET_MAGIC'].split('%')[0])
                ),
                lacks_total_domination=Domination(
                    find_best_combo=int(row['Lacks Total Domination FIND_BEST_COMBO'].split('%')[0]),
                    improve_monster=int(row['Lacks Total Domination IMPROVE_MONSTER'].split('%')[0]),
                    set_magic=int(row['Lacks Total Domination SET_MAGIC'].split('%')[0])
                )
            )

    return _ai_stats


def get_ai_stats(ai_name: str, _ai_stats=None) -> AIStat:
    return get_all_ai_stats(_ai_stats)[ai_name]


def ai_thinks_it_lacks_field_control(player_monsters: Cards, ai_monsters: Cards,
                                     *,
                                     look_facedown_cards: bool) \
        -> bool:
    if any(player_monsters):
        if is_empty(ai_monsters):
            return True

        # Both have a monster
        player_card, _ = first_card_with_best_true_max_stat_in(player_monsters,
                                                               look_facedown_cards=look_facedown_cards)
        ai_card, _ = first_card_with_best_true_max_stat_in(ai_monsters, look_facedown_cards=True)

        return player_card.max_base_stat_plus_field >= ai_card.max_base_stat_plus_field

    return False


def ai_has_total_domination(player_monsters: Cards, ai_monsters: Cards,
                            *,
                            look_facedown_cards: bool) \
        -> bool:
    if is_empty(player_monsters):
        return True

    ai_card, _ \
        = first_card_with_worst_true_max_stat_in(ai_monsters, look_facedown_cards=True)
    player_card, _ \
        = first_card_with_best_true_max_stat_in(player_monsters, look_facedown_cards=look_facedown_cards)

    return ai_card.max_base_stat_plus_field >= player_card.max_base_stat_plus_field


# Direct damages / heals

direct_damages = {  # Order compatible with AI routine
    'Sparks': 50,
    'Hinotama': 100,
    'Final Flame': 200,
    'Ookazi': 500,
    'Tremendous Fire': 1_000
}

direct_heals = {  # Order compatible with AI routine
    'Mooyan Curry': 200,
    'Red Medicine': 500,
    "Goblin's Secret Remedy": 1_000,
    "Soul of the Pure": 2_000,
    'Dian Keto the Cure Master': 5_000
}

# Fields and types

mage_fields: dict[str, Field] = {
    'Ocean Mage': Field.UMI,
    'Forest Mage': Field.FOREST,
    'Mountain Mage': Field.MOUNTAIN,
    'Desert Mage': Field.WASTELAND,
    'Meadow Mage': Field.SOGEN,
    'Guardian Neku': Field.YAMI
}


# Magics and types

type_counter_magics: dict[Type, str] = {  # Order compatible with AI routine
    Type.DRAGON: 'Dragon Capture Jar',
    Type.WARRIOR: 'Warrior Elimination',
    Type.ZOMBIE: 'Eternal Rest',
    Type.MACHINE: 'Stain Storm',
    Type.INSECT: 'Eradicating Aerosol',
    Type.ROCK: 'Breath of Light',
    Type.FISH: 'Eternal Draught'
}

magics_type_counter = {card_name: _type for _type, card_name in type_counter_magics.items()}

CRUSH_CARD_MIN_ATTACK = 1_500
#
#
# class Activate(Action):
#     def __init__(self, card: Card, odds: Odds = None, next_: Actions = None) -> None:
#         super().__init__([Action.Description(card.pos, Face.UP)], odds, next_)
#
#
# class Fuse(Action):
#     def __init__(self, cards: list[Card], odds: Odds = None, next_: Actions = None) -> None:
#         super().__init__([Action.Description(card.pos, Face.UP) for card in cards], odds, next_)
#
#
# class PlayFaceDown(Action):
#     def __init__(self, card: Card, odds: Odds = None, next_: Actions = None) -> None:
#         super().__init__([Action.Description(card.pos, Face.DOWN)], odds, next_)


class AIDecider(Protocol):
    def __call__(self, cursor: Cursor, player: Opponent, ai_player: Opponent, field: Field = ...) \
            -> Actions | Iterator[Actions | EndOfTurnType]:
        ...


class ActionHandler(Protocol):
    def __call__(self, cursor: Cursor, actions: Actions, player: Opponent, ai_player: Opponent, field: Field = ...) \
            -> Field | None:
        ...
