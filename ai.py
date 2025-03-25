import operator
import sqlite3
import csv

# Card ids
from copy import deepcopy
from functools import reduce

import db
import utils

ID, NAME, STAR1, STAR2, TYPE, ATTACK, DEFENSE = 0, 1, 3, 4, 6, 8, 9


def is_boosted(typ, field=None):
    return field is not None and \
           (field == 'Forest' and typ in ['Beast-Warrior', 'Insect', 'Plant', 'Beast']
            or field == 'Wasteland' and typ in ['Zombie', 'Dinosaur', 'Rock']
            or field == 'Mountain' and typ in ['Dragon', 'Winged-Beast', 'Thunder']
            or field == 'Sogen' and typ in ['Beast-Warrior', 'Warrior']
            or field == 'Umi' and typ in ['Aqua', 'Thunder']
            or field == 'Yami' and typ in ['Fiend', 'Spellcaster'])


def is_nerfed(typ, field=None):
    return field is not None and \
           (field == 'Umi' and typ in ['Machine', 'Pyro']
            or field == 'Yami' and typ in ['Fairy'])


START_LP = 8_000

pl_lp = START_LP
pl_deck = []
pl_hand = []
pl_monster_board = [None] * 5
pl_backrow_board = [None] * 5

ai_lp = START_LP
ai_deck = []
ai_hand = []
ai_monster_board = [None] * 5
ai_backrow_board = [None] * 5

# Best combo attributes
ORDERING = 'ordering'
IDS = 'ids'
RESULT_ID = 'result_id'
EQUIP_STAGE = 'equip_stage'
RESULT_MAX_STAT = 'result_max_stat'

MEGAMORPH_ID = 657


def encode_board_pos(pos):
    return pos - 5

def decode_board_pos(board_pos):
    return board_pos + 5

# def HACK_BOARD_POS(board_pos):
#     # It's an involution, so the conversion works both ways.
#     return -board_pos - 1


def calculate_max_stat_ai(cur, card_id, field=None, equip_stage=0):
    _type, _atk, _def = cur.execute(f"SELECT CardType, Attack, Defense FROM Cards WHERE CardID = {card_id}").fetchone()

    result = max(_atk, _def)
    result += 500 * is_boosted(_type, field=field)
    result -= 500 * is_nerfed(_type, field=field)
    result += 500 * equip_stage if equip_stage is not None else 0
    result = min(max(result, 0), 9_999)

    return result


def calculate_true_max_stat_ai(cur, card_id, field, equip_stage):
    return calculate_max_stat_ai(cur, card_id, field=field, equip_stage=equip_stage)


def find_best_combo_in_ai_hand(cur, hand, board_card=None, best_combo=None, max_fusion_length=5, field=None,
                               current_combo=None):
    """ (Assumes board positions are already encoded.)"""
    # Max length reached
    if max_fusion_length == 0:
        return best_combo

    board_id, board_pos, board_equip_level = (
        board_card['id'], board_card['pos'], board_card['equip_stage']) if board_card is not None else (None, None, 0)

    # Base case
    if current_combo is None:
        current_combo = {ORDERING: [], IDS: [], RESULT_ID: None, EQUIP_STAGE: 0, RESULT_MAX_STAT: 0}

        if board_card is not None:
            max_fusion_length -= 1

            current_combo[ORDERING].append(board_pos)
            current_combo[IDS].append(board_id)
            current_combo[RESULT_ID] = board_id
            current_combo[EQUIP_STAGE] = board_equip_level

            # This should consider max base stat, field and equip level
            current_combo[RESULT_MAX_STAT] = calculate_max_stat_ai(cur, board_id, field=field,
                                                                   equip_stage=board_equip_level)

    if best_combo is None:
        best_combo = deepcopy(current_combo)

    for pos, card_id in enumerate(hand):  # enumerate(itertools.chain(monster_board, hand)):
        # Skip card if same slot in hand than the one on the board
        if board_pos is not None and board_pos == pos:
            continue

        # Skip cards already in the current combo
        if pos in current_combo[ORDERING]:
            continue

        old_combo = deepcopy(current_combo)

        # Initialise with a card from the hand
        if current_combo[RESULT_ID] is None:
            current_combo[ORDERING].append(pos)
            current_combo[IDS].append(card_id)
            current_combo[RESULT_ID] = card_id

            # This should consider max base stat only
            current_combo[RESULT_MAX_STAT] = calculate_max_stat_ai(cur, card_id)

        # Continue previous combo with cards from the hand
        else:
            # Check if we're equipping a compatible item or performing a valid fusion
            equipped_equip = cur.execute(f"SELECT EquippedID, EquipID FROM Equipping "
                                         f"WHERE EquippedID = {current_combo[RESULT_ID]} AND EquipID = {card_id} "
                                         f"OR    EquippedID = {card_id} AND EquipID = {current_combo[RESULT_ID]}").fetchone()
            fusion = cur.execute(f"SELECT Result FROM Fusions "
                                 f"WHERE Material1 = {current_combo[RESULT_ID]} AND Material2 = {card_id}").fetchone()
            result_id = equipped_equip[0] if equipped_equip is not None \
                else int(fusion[0]) if fusion is not None \
                else None

            # Non-compatible equip / fusion
            if result_id is None:
                continue

            # Update currently explored combo
            current_combo[ORDERING].append(pos)
            current_combo[IDS].append(card_id)
            current_combo[RESULT_ID] = result_id

            # This should consider max base stat and field
            current_combo[RESULT_MAX_STAT] = calculate_max_stat_ai(cur, result_id, field=field)

            if equipped_equip is not None:
                current_combo[EQUIP_STAGE] += 2 if equipped_equip[1] == MEGAMORPH_ID else 1
            else:
                current_combo[EQUIP_STAGE] = 0

        # Update best combo
        b, c = best_combo[RESULT_MAX_STAT], current_combo[RESULT_MAX_STAT]
        lb, lc = len(best_combo[ORDERING]), len(current_combo[ORDERING])
        if b < c \
                or b == c and \
                (min(lb, lc) == 1 and max(lb, lc) > 1 and min(best_combo[ORDERING]) > min(current_combo[ORDERING])
                 or min(lb, lc) > 1 and max(lb, lc) > 1 and lb > lc):
            best_combo = deepcopy(current_combo)

        best_combo = find_best_combo_in_ai_hand(cur, hand, board_card=board_card, best_combo=best_combo,
                                                max_fusion_length=max_fusion_length - 1, field=field,
                                                current_combo=current_combo)

        current_combo = old_combo

    return best_combo


def find_best_combo_in_ai_board_and_hand(cur, hand, monster_board=None, max_fusion_length=5, field=None):
    best_combo = None

    # First, iterate through monster cards on the board
    if monster_board is not None:
        for board_card in monster_board:
            if board_card is None:
                continue

            best_combo = find_best_combo_in_ai_hand(cur, hand, board_card=board_card, best_combo=best_combo,
                                                    max_fusion_length=max_fusion_length, field=field,
                                                    current_combo=None)

    # Finish with only cards from the hand
    return find_best_combo_in_ai_hand(cur, hand, board_card=None, best_combo=best_combo,
                                      max_fusion_length=max_fusion_length, field=field,
                                      current_combo=None)


def improve_monster_from_ai_hand(cur, hand, board_card, best_combo=None, max_improve_length=4, field=None,
                                 current_combo=None):
    # Max length reached
    if max_improve_length == 0:
        return best_combo

    board_id, board_pos, board_equip_level = (
        board_card['id'], board_card['pos'], board_card['equip_stage']) if board_card is not None else (None, None, 0)

    # Base case
    if current_combo is None:
        current_combo = {
            ORDERING: [board_pos],
            IDS: [board_id],
            RESULT_ID: board_id,
            EQUIP_STAGE: board_equip_level,
            # This should consider max base stat and field
            RESULT_MAX_STAT: calculate_max_stat_ai(cur, board_id, field=field)
        }

    if best_combo is None:
        best_combo = deepcopy(current_combo)

    for pos, card_id in enumerate(hand):  # enumerate(itertools.chain(monster_board, hand)):
        # Skip cards already in the current combo
        if pos in current_combo[ORDERING]:
            continue

        old_combo = deepcopy(current_combo)

        # Check if we're equipping a compatible item or performing a valid fusion
        equipped_equip = cur.execute(f"SELECT EquippedID, EquipID FROM Equipping "
                                     f"WHERE EquippedID = {current_combo[RESULT_ID]} AND EquipID = {card_id} "
                                     f"OR    EquippedID = {card_id} AND EquipID = {current_combo[RESULT_ID]}").fetchone()
        fusion = cur.execute(f"SELECT Result FROM Fusions "
                             f"WHERE Material1 = {current_combo[RESULT_ID]} AND Material2 = {card_id}").fetchone()
        result_id = equipped_equip[0] if equipped_equip is not None \
            else int(fusion[0]) if fusion is not None \
            else None

        # Non-compatible equip / fusion
        if result_id is None:
            continue

        # Update currently explored combo
        current_combo[ORDERING].append(pos)
        current_combo[IDS].append(card_id)
        current_combo[RESULT_ID] = result_id

        # This should consider max base stat and field
        current_combo[RESULT_MAX_STAT] = calculate_max_stat_ai(cur, result_id, field=field)

        if equipped_equip is not None:
            current_combo[EQUIP_STAGE] += 2 if equipped_equip[1] == MEGAMORPH_ID else 1
        else:
            current_combo[EQUIP_STAGE] = 0

        # Update best combo
        b, c = best_combo[RESULT_MAX_STAT], current_combo[RESULT_MAX_STAT]
        lb, lc = len(best_combo[ORDERING]), len(current_combo[ORDERING])
        if b < c or b == c and lb > lc:  # or b == c and lb == lc and min(filter(lambda x: x >= 0, best_combo[ORDERING]) > min(filter(lambda x: x >= 0, current_combo[ORDERING])):
            best_combo = deepcopy(current_combo)

        best_combo = improve_monster_from_ai_hand(cur, hand, board_card=board_card, best_combo=best_combo,
                                                  max_improve_length=max_improve_length - 1, field=field,
                                                  current_combo=current_combo)

        current_combo = old_combo

    return best_combo


def improve_monster_from_ai_board_and_hand(cur, hand, monster_board=None, max_improve_length=4, field=None):
    """Returns a converted list of actions. Returns `None` if no improvement is found."""
    best_combo = None

    # Iterate from lowest *true* max stat to highest (earlier cards are looked at first in case of a tie).
    if monster_board is not None:
        ordered_monster_board = list(filter(lambda x: x is not None, monster_board))
        ordered_monster_board.sort(
            key=lambda x: (calculate_max_stat_ai(cur, x['id'], field=field, equip_stage=x['equip_stage']), x['pos']))

        for board_card in ordered_monster_board:
            best_combo = improve_monster_from_ai_hand(cur, hand, board_card=board_card, best_combo=best_combo,
                                                      max_improve_length=max_improve_length, field=field,
                                                      current_combo=None)
            if best_combo[RESULT_ID] == board_card['id'] \
                    and best_combo[EQUIP_STAGE] == board_card['equip_stage'] \
                    and best_combo[RESULT_MAX_STAT] <= calculate_max_stat_ai(cur, board_card['id'], field=field):
                best_combo = None

            if best_combo is not None:
                return convert_best_combo(cur, best_combo)

    return None


direct_damages = {
    'Sparks': 50,
    'Hinotama': 100,
    'Final Flame': 200,
    'Ookazi': 500,
    'Tremendous Fire': 1_000
}

FACE_DOWN, FACE_UP = 0, 1

mage_fields = {
    'Ocean Mage': 'Umi',
    'Forest Mage': 'Forest',
    'Mountain Mage': 'Mountain',
    'Desert Mage': 'Wasteland',
    'Meadow Mage': 'Sogen',
    'Guardian Neku': 'Yami'
}

type_counter_magics = {
    'Dragon': 'Dragon Capture Jar',
    'Warrior': 'Warrior Elimination',
    'Zombie': 'Eternal Rest',
    'Machine': 'Stain Storm',
    'Insect': 'Eradicating Aerosol',
    'Rock': 'Breath of Light',
    'Fish': 'Eternal Draught'
}

traps_list_descending = [
    'Widespread Ruin',
    'Acid Trap Hole',
    'Invisible Wire',
    'Bear Trap',
    'Eatgaboon',
    'House of Adhesive Tape',
    'Fake Trap'
]

support_type_with_field = {
    'Aqua': ['Umi'],
    'Beast': ['Forest'],
    'Beast-Warrior': ['Sogen', 'Forest'],
    'Dinosaur': ['Wasteland'],
    'Dragon': ['Mountain'],
    # 'Fairy': [None],
    'Fiend': ['Yami'],
    'Fish': ['Umi'],
    'Insect': ['Forest'],
    # 'Machine': [None],
    'Plant': ['Forest'],
    # 'Pyro': [None],
    # 'Reptile': [None],
    'Rock': ['Wasteland'],
    'Sea Serpent': ['Umi'],
    'Spellcaster': ['Yami'],
    'Thunder': ['Mountain', 'Umi'],
    'Warrior': ['Sogen'],
    'Winged Beast': ['Mountain'],
    'Zombie': ['Wasteland']
}


def is_empty(row):
    return row == [None] * 5


def get_first_pos_in_hand(cur, card_name, hand):
    """ Return the first position of the card name in the hand. Returns None if not found."""
    return next((pos for (pos, card_id) in enumerate(hand) if card_id == utils.get_card_id_from_name(cur, card_name)),
                None)


def get_first_pos_of_true_max_stat_on_board(cur, monster_board, field, look_facedown_cards):
    """ Returns the first position and associated stat of the card with the best true max stat on a board. """
    pos, _max = None, 0
    for i, monster in enumerate(monster_board):
        if monster is None or not look_facedown_cards and monster['face'] == FACE_DOWN:
            continue
        stat = calculate_max_stat_ai(cur, monster['id'], field=field, equip_stage=monster.get('equip_stage'))
        if stat > _max:
            pos, _max = i, stat

    return pos, _max


def get_first_pos_of_lowest_true_max_stat_on_board(cur, monster_board, field, look_facedown_cards):
    """ Returns the first position and associated stat of the card with the lowest true max stat on a board. """
    pos, _min = None, 0
    for i, monster in enumerate(monster_board):
        if monster is None or not look_facedown_cards and monster['face'] == FACE_DOWN:
            continue
        stat = calculate_max_stat_ai(cur, monster['id'], field=field, equip_stage=monster['equip_stage'])
        if _min == 0 or 0 < stat < _min:
            pos, _min = i, stat

    return pos, _min


def get_first_pos_of_base_max_stat_plus_field_on_board(cur, monster_board, field, look_facedown_cards):
    """ Returns the first position and associated stat of the card with the best max stat + field on a board. """
    pos, _max = None, 0
    for i, monster in enumerate(monster_board):
        if monster is None or not look_facedown_cards and monster['face'] == FACE_DOWN:
            continue
        stat = calculate_max_stat_ai(cur, monster['id'], field=field)
        if stat > _max:
            pos, _max = i, stat

    return pos, _max


def get_first_pos_of_base_max_stat_in_hand(cur, hand):
    """ Returns the first position and associated stat of the card with the best base max stat in a hand. """
    pos, _max = None, 0
    for i, card_id in enumerate(hand):
        if card_id is None:
            continue
        stat = calculate_max_stat_ai(cur, card_id)
        if stat > _max:
            pos, _max = i, stat

    return pos, _max


def get_first_pos_of_type_in_hand(cur, hand, _type):
    """ Returns the first position of a given _type in a hand. Returns None if there are none. """
    pos = None
    for i, card_id in enumerate(hand):
        if card_id is None:
            continue
        card_type = utils.get_card_type_from_id(cur, card_id)

        if card_type == _type:
            return i

    return pos


def get_first_monster_compatible_on_board(cur, monster_board, equip_id):
    """ Returns the position on the board of the first compatible monster with the given equip. Returns None if no monster is found. """

    for card_id in monster_board:
        if card_id is None:
            continue
        _tuple = cur.execute(
            f"SELECT * FROM 'Equipping' WHERE EquipID = '{equip_id}' AND EquippedID = '{card_id}'").fetchone()
        if _tuple is not None:
            return card_id['pos']

    return None


def ai_thinks_it_lacks_field_control(cur, player_monsters, ai_monsters, field, look_facedown_cards):
    if any(player_monsters):
        if not any(ai_monsters):
            return True

        # Both have a monster
        player_pos, _ = get_first_pos_of_true_max_stat_on_board(cur, player_monsters, field, look_facedown_cards)
        ai_pos, _ = get_first_pos_of_true_max_stat_on_board(cur, ai_monsters, field, True)

        player_id, ai_id = player_monsters[player_pos]['id'], ai_monsters[ai_pos]['id']

        # Ignore equips in the comparison
        return calculate_max_stat_ai(cur, player_id, field=field) >= calculate_max_stat_ai(cur, ai_id, field=field)

    return False


def ai_has_total_domination(cur, player_monsters, ai_monsters, field, look_facedown_cards):
    ai_lowest_true_max_stat_pos, _ = get_first_pos_of_lowest_true_max_stat_on_board(cur, ai_monsters, field,
                                                                                    look_facedown_cards=True)
    player_true_max_stat_pos, _ = get_first_pos_of_true_max_stat_on_board(cur, player_monsters, field,
                                                                          look_facedown_cards=look_facedown_cards)
    return calculate_max_stat_ai(cur, ai_monsters[ai_lowest_true_max_stat_pos]['id'], field=field) \
           >= calculate_max_stat_ai(cur, player_monsters[player_true_max_stat_pos]['id'], field=field)


def best_combo_consists_of_only_cards_from_the_hand(best_combo):
    return False if best_combo is None or len(best_combo[ORDERING]) == 0 else \
        all((pos >= 0 for pos in best_combo[ORDERING]))


def best_combo_consists_of_playing_on_top_of_a_card_on_the_field(best_combo):
    return len(best_combo[ORDERING]) >= 2 and best_combo[ORDERING][0] < 0


def convert_best_combo(cur, best_combo):
    """ Converts the best combo into a list of actions. Returns None if no combo is found. """
    # ORDERING = 'ordering'
    # IDS = 'ids'
    # RESULT_ID = 'result_id'
    # EQUIP_STAGE = 'equip_stage'
    # RESULT_MAX_STAT = 'result_max_stat'
    if best_combo_consists_of_only_cards_from_the_hand(best_combo):
        return [(pos, FACE_UP) for pos in best_combo[ORDERING]]

    # Bug : if monster + magic, then simply trigger the magic
    if best_combo_consists_of_playing_on_top_of_a_card_on_the_field(best_combo):
        if len(best_combo[ORDERING]) == 2 and utils.is_magic(cur, best_combo[IDS][1]):
            return [(best_combo[ORDERING][1], FACE_UP)]

        return [(pos, FACE_UP) for pos in best_combo[ORDERING]]

    return None


def combo_non_equip(pos, ai_backrow):
    combo = None
    if all(ai_backrow):
        combo = [(pos, FACE_UP)]
    else:
        combo = [(pos, FACE_DOWN)]
    return combo


def combo_equip(pos, ai_backrow, ai_frontrow, equip):
    combo = None
    # Backrow is full
    if all(ai_backrow):
        # Find the first compatible monster
        monster_pos = get_first_monster_compatible_on_board(cur, ai_frontrow, equip)
        if monster_pos is not None:
            combo = [(monster_pos, FACE_UP), (pos, FACE_UP)]
        # No compatible monster
        else:
            if any(ai_frontrow):
                monster_pos, _ = get_first_pos_of_lowest_true_max_stat_on_board(cur, ai_frontrow,
                                                                                equip,
                                                                                look_facedown_cards=True)
                combo = [(monster_pos, FACE_UP), (pos, FACE_UP)]
            else:
                combo = [(pos, FACE_DOWN)]  # random slot
    # Backrow is not full
    else:
        combo = [(pos, FACE_DOWN)]

    return combo


def lbl_set_magic(cur, ai):
    # Trap
    pos = get_first_pos_of_type_in_hand(cur, ai['hand'], 'Trap')
    if pos is not None:
        return combo_non_equip(pos, ai['backrow'])

    # Equip
    pos = get_first_pos_of_type_in_hand(cur, ai['hand'], 'Equip')
    if pos is not None:
        return combo_equip(pos, ai['backrow'], ai['frontrow'], ai['hand'][pos])

    # Magic
    pos = get_first_pos_of_type_in_hand(cur, ai['hand'], 'Magic')
    if pos is not None:
        return combo_non_equip(pos, ai['backrow'])

    # Ritual
    pos = get_first_pos_of_type_in_hand(cur, ai['hand'], 'Ritual')
    if pos is not None:
        return combo_non_equip(pos, ai['backrow'])

    # Only monsters
    pos = get_first_pos_of_base_max_stat_in_hand(cur, ai['hand'])
    combo = [(pos, FACE_DOWN)]
    return combo


SEE_THROUGH = 0


def lbl_find_best_combo(cur, ai_player, field):
    """ Returns a converted best combo. """
    best_combo = find_best_combo_in_ai_board_and_hand(cur, ai_player['hand'], monster_board=ai_player['frontrow'],
                                                      max_fusion_length=utils.get_ai_stats(ai_player['name'])[
                                                          utils.MAX_FUSION_LENGTH],
                                                      field=field)

    combo = convert_best_combo(cur, best_combo)
    if combo is not None:
        return combo

    # No combo play -> set magic
    if best_combo[RESULT_MAX_STAT] == 0:
        combo = lbl_set_magic(cur, ai_player)
        return combo

    # Doing nothing to a monster from the board -> compatible field
    best_type = utils.get_card_type_from_id(cur, best_combo[IDS][0])
    for support_field in support_type_with_field.get(best_type, []):
        # This skips the second field if there is a second one
        if field == support_field:
            break

        pos = get_first_pos_in_hand(cur, support_field, ai_player['hand'])
        if pos is not None:
            combo = [(pos, FACE_UP)]
            return combo

    # Fallback : best max stat in hand
    pos, _ = get_first_pos_of_base_max_stat_in_hand(cur, ai_player['hand'])
    if pos is not None:
        combo = [(pos, FACE_DOWN)]
        return combo

    # Fallback² : no monsters
    odds = (1, 5)
    combo = []
    for pos in range(5):
        card = ai_player['hand'][pos]
        _type = utils.get_card_type_from_id(cur, card)

        if _type == 'Equip':
            sub_combo = combo_non_equip(pos, ai_player['backrow'])
        else:
            sub_combo = combo_equip(pos, ai_player['backrow'], ai_player['frontrow'], ai_player['hand'][pos])
        combo.append((sub_combo, odds))

    return combo


def lbl_improve_monster(cur, ai_player, field):
    """ Returns a converted combo of the monster to be improved. """
    improve = improve_monster_from_ai_board_and_hand(cur, ai_player['hand'], ai_player['frontrow'],
                                           max_improve_length=utils.get_ai_stats(ai_player['name'])[utils.MAX_IMPROVE_LENGTH],
                                           field=field)

    if improve is None:
        return lbl_find_best_combo(cur, ai_player, field)


def hand_ai(cur, player, ai_player, current_ai_turn, field=None):
    """ Returns the position of the chosen card(s) and whether the play is face-down or face-up.
        If probabilities are involved, returns a list of tuples, each containing a summary of the play associated with its probability.
    """
    combo = []
    always_look_facedown_cards = utils.get_ai_stats(ai_player['name'])[utils.ATTACK_PERCENT] == SEE_THROUGH

    # 1. Direct kill
    for spell_name, dmg in direct_damages.items():
        if is_empty(player['backrow']) and dmg >= player['LP'] \
                and (pos := get_first_pos_in_hand(cur, spell_name, ai_player['hand'])) is not None:
            combo = [(pos, FACE_UP)]
            return combo

    # 2. Forced field
    if (ai_name := ai_player['name']) in mage_fields and field != (ai_field := mage_fields[ai_name]) \
            and (pos := get_first_pos_in_hand(cur, ai_field, ai_player['hand'])) is not None:
        combo = [(pos, FACE_UP)]
        return combo

    # 3a. The AI lacks field control
    if ai_thinks_it_lacks_field_control(cur, player['frontrow'], ai_player['frontrow'], field, always_look_facedown_cards):
        pos_base_max_stat_in_ai_hand, stat_base_max_stat_in_ai_hand = get_first_pos_of_base_max_stat_in_hand(cur,
                                                                                                             ai_player[
                                                                                                                 'hand'])

        pos_best_visible_player, stat_best_visible_player_true_max_stat = get_first_pos_of_true_max_stat_on_board(cur,
                                                                                                                  player[
                                                                                                                      'frontrow'],
                                                                                                                  field,
                                                                                                                  always_look_facedown_cards)

        # 3a1. Regain control with a single monster
        if pos_base_max_stat_in_ai_hand is not None:
            if is_empty(ai_player['frontrow']):
                combo = [(pos_base_max_stat_in_ai_hand, FACE_DOWN)]
                return combo

            if stat_base_max_stat_in_ai_hand >= stat_best_visible_player_true_max_stat:
                combo = [(pos_base_max_stat_in_ai_hand, FACE_DOWN)]
                return combo

        # 3a2. Regain control with magic/trap
        if current_ai_turn >= 4:  # ai_player['hand'] - 5 + ai_player['remaining_deck'] <= 32:
            best_player_type = utils.get_card_type_from_id(cur, player['frontrow'][pos_best_visible_player]['id'])

            # Counter player type
            for _type, counter_magic_name in type_counter_magics.items():
                if _type == best_player_type:
                    pos = get_first_pos_in_hand(cur, counter_magic_name, ai_player['hand'])
                    if pos is not None:
                        combo = [(pos, FACE_UP)]
                        return combo

            # Decrease stats
            pos = get_first_pos_in_hand(cur, 'Spellbinding Circle', ai_player['hand'])
            if pos is not None:
                combo = [(pos, FACE_UP)]
                return combo

            pos = get_first_pos_in_hand(cur, 'Shadow Spell', ai_player['hand'])
            if pos is not None:
                combo = [(pos, FACE_UP)]
                return combo

            # Destroy monsters
            stat_best_visible_player_base_max_stat_plus_field = calculate_max_stat_ai(cur, player['frontrow'][
                pos_best_visible_player]['id'], field)
            if stat_best_visible_player_base_max_stat_plus_field >= 1_500:
                pos = get_first_pos_in_hand(cur, 'Crush Card', ai_player['hand'])
                if pos is not None:
                    combo = [(pos, FACE_UP)]
                    return combo

            pos = get_first_pos_in_hand(cur, 'Raigeki', ai_player['hand'])
            if pos is not None:
                combo = [(pos, FACE_UP)]
                return combo

            # Traps
            for trap_name in traps_list_descending:
                pos = get_first_pos_in_hand(cur, trap_name, ai_player['hand'])
                if pos is not None:
                    combo = [(pos, FACE_DOWN)]
                    return combo

            # Swords of Revealing Light
            if player.get('remaining_turns_under_swords', 0) == 0:
                pos = get_first_pos_in_hand(cur, 'Swords of Revealing Light', ai_player['hand'])
                if pos is not None:
                    combo = [(pos, FACE_UP)]
                    return combo

            # Dark Hole
            if len(list(filter(None, player['frontrow']))) > len(list(filter(None, ai_player['frontrow']))):
                pos = get_first_pos_in_hand(cur, 'Dark Hole', ai_player['hand'])
                if pos is not None:
                    combo = [(pos, FACE_UP)]
                    return combo

        # 3a3. Regain control with a combo
        return lbl_find_best_combo(cur, ai_player, field)

    # 3b. The AI thinks it has field control
    odds_num, odds_denom = 1, 1
    # 3b1. Clear player's backrow
    if any(player['backrow']) and (pos := get_first_pos_in_hand(cur, "Harpie's Feather Duster", ai_player['hand'])) is not None:
        odds_num *= utils.get_ai_stats(ai_player['name'])[utils.SPELL_PERCENT]
        odds_denom *= 100
        combo = [([(pos, FACE_DOWN)], (odds_num, odds_denom))]

    # 3b2. Improve monster if low enough LP
    if ai_player['LP'] <= utils.get_ai_stats(ai_player['name'])[utils.LOW_LP_THRESHOLD]:
        # improve = improve_monster_from_ai_board_and_hand(cur, ai_player['hand'],
        #                                                  monster_board=ai_player['frontrow'],
        #                                                  max_improve_length=utils.get_ai_stats()[ai_player['name']][
        #                                                      utils.MAX_IMPROVE_LENGTH],
        #                                                  field=field)
        #
        # if improve is None:
        #     improve = find_best_combo_in_ai_board_and_hand(cur, ai_player['hand'], monster_board=ai_player['frontrow'],
        #                                               max_fusion_length=utils.get_ai_stats(ai_player['name')[
        #                                                   utils.MAX_FUSION_LENGTH],
        #                                               field=field)
        #     if improve is None:
        #         improve = lbl_set_magic(cur, ai_player)
        improve = lbl_improve_monster(cur, ai_player, field)
        if len(combo) == 0:
            combo = improve
        else:
            combo.append((improve, (odds_denom - odds_num, odds_denom)))
        return combo

    # If we already have conditional combos, consider the remaining probabilities
    if len(combo) > 0:
        odds_num = odds_denom - odds_num
        odds_denom = 100

    # Choose randomly between IMPROVE_MONSTER, FIND_BEST_COMBO and SET_MAGIC
    domination_mode = utils.TOTAL_DOMINATION \
        if ai_has_total_domination(cur, player['frontrow'], ai_player['frontrow'], field, always_look_facedown_cards) \
        else utils.LACKS_TOTAL_DOMINATION

    best_combo = lbl_find_best_combo(cur, ai_player, field)
    best_combo_odds = (odds_num*utils.get_ai_stats(ai_player['name'])[domination_mode][utils.FIND_BEST_COMBO],
                       odds_denom * 100)
    combo.append((best_combo, best_combo_odds))

    improve = lbl_improve_monster(cur, ai_player, field)
    improve_odds = (odds_num * utils.get_ai_stats(ai_player['name'])[domination_mode][utils.IMPROVE_MONSTER],
                    odds_denom * 100)
    combo.append((improve, improve_odds))

    set_magic = lbl_set_magic(cur, ai_player)
    set_magic_odds = (odds_num*utils.get_ai_stats(ai_player['name'])[domination_mode][utils.SET_MAGIC],
                      odds_denom * 100)
    combo.append((set_magic, set_magic_odds))

    return combo


if __name__ == '__main__':
    con, cur = db.connect_to_YFM_database()

    # Code here

    # End code
    con.close()
