from __future__ import annotations
import csv
from utils import *

# AI stats
from sqlite3 import Cursor
from typing import Optional

# import utils


class Domination:
    def __init__(self, *, find_best_combo: int, improve_monster: int, set_magic: int) -> None:
        self.find_best_combo = find_best_combo
        self.improve_monster = improve_monster
        self.set_magic = set_magic


class AIStat:
    SEE_THROUGH = 0  # ATTACK_PERCENT

    def __init__(self, *, low_lp_threshold: int, critical_deck_size: int, max_fusion_length: int,
                 max_improve_length: int,
                 spell_percent: int, attack_percent: int,
                 total_domination: Domination, lacks_total_domination: Domination) -> None:
        self.low_lp_threshold = low_lp_threshold
        self.critical_deck_size = critical_deck_size
        self.max_fusion_length = max_fusion_length
        self.max_improve_length = max_improve_length
        self.spell_percent = spell_percent
        self.attack_percent = attack_percent
        self.total_domination = total_domination
        self.lacks_total_domination = lacks_total_domination


# LOW_LP_THRESHOLD = 'Low LP Threshold'
# CRITICAL_DECK_SIZE = 'Critical Deck Size'
# MAX_FUSION_LENGTH = 'Max Fusion Length'
# MAX_IMPROVE_LENGTH = 'Max Improve Length'
# SPELL_PERCENT = 'Spell Percent'
# ATTACK_PERCENT = 'Attack Percent'
# TOTAL_DOMINATION = 'Total Domination'
# LACKS_TOTAL_DOMINATION = 'Lacks Total Domination'
# FIND_BEST_COMBO = 'FIND_BEST_COMBO'
# IMPROVE_MONSTER = 'IMPROVE_MONSTER'
# SET_MAGIC = 'SET_MAGIC'


ai_stats: Optional[dict[str, AIStat]] = None


def get_all_ai_stats(_ai_stats: Optional[dict[str, AIStat]] = ai_stats) -> dict[str, AIStat]:
    if _ai_stats is not None:
        return _ai_stats

    _ai_stats = {}
    with open('YFM_AI-stats.csv', newline='') as csvfile:
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

    # for row in reader:
    #     del row['Hand Size']
    #
    #     row[LOW_LP_THRESHOLD] = int(row[LOW_LP_THRESHOLD])
    #     row[CRITICAL_DECK_SIZE] = int(row[CRITICAL_DECK_SIZE])
    #     row[MAX_FUSION_LENGTH] = int(row[MAX_FUSION_LENGTH])
    #     row[MAX_IMPROVE_LENGTH] = int(row[MAX_IMPROVE_LENGTH])
    #
    #     row[SPELL_PERCENT] = int(row['Spell Probability'].split('%')[0])
    #     row[ATTACK_PERCENT] = int(row['Attack Probability'].split('%')[0])
    #     del row['Spell Probability']
    #     del row['Attack Probability']
    #
    #     row[TOTAL_DOMINATION] = {
    #         FIND_BEST_COMBO: row['Total Domination FIND_BEST_COMBO'],
    #         IMPROVE_MONSTER: row['Total Domination IMPROVE_MONSTER'],
    #         SET_MAGIC: row['Total Domination SET_MAGIC']
    #     }
    #     del row['Total Domination FIND_BEST_COMBO']
    #     del row['Total Domination IMPROVE_MONSTER']
    #     del row['Total Domination SET_MAGIC']
    #
    #     row[LACKS_TOTAL_DOMINATION] = {
    #         FIND_BEST_COMBO: row['Lacks Total Domination FIND_BEST_COMBO'],
    #         IMPROVE_MONSTER: row['Lacks Total Domination IMPROVE_MONSTER'],
    #         SET_MAGIC: row['Lacks Total Domination SET_MAGIC']
    #     }
    #     del row['Lacks Total Domination FIND_BEST_COMBO']
    #     del row['Lacks Total Domination IMPROVE_MONSTER']
    #     del row['Lacks Total Domination SET_MAGIC']
    #
    #     row[TOTAL_DOMINATION][FIND_BEST_COMBO] = int(row[TOTAL_DOMINATION][FIND_BEST_COMBO].split('%')[0])
    #     row[TOTAL_DOMINATION][IMPROVE_MONSTER] = int(row[TOTAL_DOMINATION][IMPROVE_MONSTER].split('%')[0])
    #     row[TOTAL_DOMINATION][SET_MAGIC] = int(row[TOTAL_DOMINATION][SET_MAGIC].split('%')[0])
    #     row[LACKS_TOTAL_DOMINATION][FIND_BEST_COMBO] = int(
    #         row[LACKS_TOTAL_DOMINATION][FIND_BEST_COMBO].split('%')[0])
    #     row[LACKS_TOTAL_DOMINATION][IMPROVE_MONSTER] = int(
    #         row[LACKS_TOTAL_DOMINATION][IMPROVE_MONSTER].split('%')[0])
    #     row[LACKS_TOTAL_DOMINATION][SET_MAGIC] = int(row[LACKS_TOTAL_DOMINATION][SET_MAGIC].split('%')[0])
    #
    #     _ai_stats[row['Opponent']] = row
    #
    #     del row['Opponent']


def get_ai_stats(ai_name: str, _ai_stats=ai_stats):
    return get_all_ai_stats()[ai_name]


def ai_thinks_it_lacks_field_control(cur: Cursor, player_monsters: Cards, ai_monsters: Cards, field: Field,
                                     look_facedown_cards: bool) -> bool:
    if any(player_monsters):
        if is_empty(ai_monsters):
            return True

        # Both have a monster
        player_pos, _ = get_first_pos_of_true_max_stat_in(cur, player_monsters, field, look_facedown_cards)
        ai_pos, _ = get_first_pos_of_true_max_stat_in(cur, ai_monsters, field, True)

        player_id, ai_id = player_monsters[player_pos]['id'], ai_monsters[ai_pos]['id']

        # Ignore equips in the comparison
        return calculate_max_base_stat_plus_field(cur, player_id, field=field) \
               >= calculate_max_base_stat_plus_field(cur, ai_id, field=field)

    return False


def ai_has_total_domination(cur: Cursor, player_monsters: Cards, ai_monsters: Cards, field: Field,
                            look_facedown_cards: bool) -> bool:
    if is_empty(player_monsters):
        return True

    ai_lowest_true_max_stat_pos, _ \
        = get_first_pos_of_lowest_true_max_stat_in(cur, ai_monsters, field, look_facedown_cards=True)
    player_true_max_stat_pos, _ \
        = get_first_pos_of_true_max_stat_in(cur, player_monsters, field, look_facedown_cards=look_facedown_cards)

    # Ignore equips in the comparison
    return calculate_max_base_stat_plus_field(cur, ai_monsters[ai_lowest_true_max_stat_pos]['id'], field=field) \
           >= calculate_max_base_stat_plus_field(cur, player_monsters[player_true_max_stat_pos]['id'], field=field)


FRONTROW_OFFSET = 5
MIN_FRONTROW_POS, MAX_FRONTROW_POS = MIN_POS - FRONTROW_OFFSET, MAX_POS - FRONTROW_OFFSET


def encode_frontrow_pos(pos: Position) -> Position:
    assert MIN_POS <= pos <= MAX_POS
    return pos - FRONTROW_OFFSET


def decode_frontrow_pos(board_pos: Position) -> Position:
    assert MIN_FRONTROW_POS <= board_pos <= MAX_FRONTROW_POS
    return board_pos + FRONTROW_OFFSET


# Direct damages / heals

direct_damages = {
    'Sparks': 50,
    'Hinotama': 100,
    'Final Flame': 200,
    'Ookazi': 500,
    'Tremendous Fire': 1_000
}

direct_heals = {
    'Mooyan Curry': 200,
    'Red Medicine': 500,
    "Goblin's Secret Remedy": 1_000,
    "Soul of the Pure": 2_000,
    'Dian Keto the Cure Master': 8_000
}

# Fields and types

mage_fields = {
    'Ocean Mage': 'Umi',
    'Forest Mage': 'Forest',
    'Mountain Mage': 'Mountain',
    'Desert Mage': 'Wasteland',
    'Meadow Mage': 'Sogen',
    'Guardian Neku': 'Yami'
}


# Magics and types

type_counter_magics = {
    'Dragon': 'Dragon Capture Jar',
    'Warrior': 'Warrior Elimination',
    'Zombie': 'Eternal Rest',
    'Machine': 'Stain Storm',
    'Insect': 'Eradicating Aerosol',
    'Rock': 'Breath of Light',
    'Fish': 'Eternal Draught'
}