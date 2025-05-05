import random
from sqlite3 import Cursor
from typing import Optional, Protocol

import db

Id = int
Card = dict
Cards = list[Card]
Position = int
Stat = int
Field = Optional[str]
EquipStage = int
Type = str

# Board
Opponent = dict
OpponentId = int
PLAYER, AI = 0, 1

Act = int
BattleMode = int
FACE_DOWN, FACE_UP, DARKEN, ATTACK, DEFENSE = 0, 1, 2, 3, 4

START_EXODIA_ID, END_EXODIA_ID = 17, 21
CARD_LIMIT = 3
CARD_LIMIT_EXODIA = 1

DECK_SIZE = 40


def generate_decks(cur: Cursor, duelist_name: str, num_decks: int = 1):
    """ Creates an iterator of `num_decks` decks of the desired `duelist_name`."""

    pool_type = 'Deck'

    # Pool type id
    pool_type_id, = cur.execute(f"SELECT DuelistPoolTypeID "
                                f"FROM DuelistPoolTypes "
                                f"WHERE DuelistPoolTypes.DuelistPoolType = '{pool_type}'").fetchone()

    # (cardID, prob) iterator
    cards_probs = list(cur.execute(
        f"SELECT CardID, Prob "
        f"FROM DuelistPoolSamplingRates "
        f"LEFT JOIN Duelists ON Duelists.DuelistID = DuelistPoolSamplingRates.DuelistID "
        f"WHERE DuelistPoolSamplingRates.DuelistPoolTypeID = {pool_type_id} "
        f"AND Duelists.DuelistName = '{duelist_name}' "
        f"AND DuelistPoolSamplingRates.Prob > 0 "
    ))

    if len(cards_probs) == 0:
        raise ValueError(f"Unknown duelist name '{duelist_name}'")

    PROB, NUM = 1, 2
    for _ in range(num_decks):
        cards_probs_nums = [
            [card_id, prob, CARD_LIMIT if card_id not in range(START_EXODIA_ID, END_EXODIA_ID + 1) else CARD_LIMIT_EXODIA]
            for (card_id, prob) in cards_probs
        ]

        # Build Deck
        deck_ids = []
        # print(clean_desc(cur.execute("SELECT * FROM Cards").description))
        for _ in range(DECK_SIZE):
            chosen, = random.choices(cards_probs_nums, weights=[prob for (_, prob, _) in cards_probs_nums])
            # print(chosen)
            deck_ids.append(chosen[0])
            chosen[NUM] -= 1
            if chosen[NUM] == 0:
                chosen[PROB] = 0
            # print(cards_probs_nums)
        # print(deck_ids)

        yield deck_ids


def generate_new_hands(cur: Cursor, duelist_name: str, num_hands: int = 1):
    for deck in generate_decks(cur, duelist_name, num_decks=num_hands):
        hand_size, = cur.execute(f"SELECT HandSize "
                                 f"FROM Duelists "
                                 f"WHERE Duelists.DuelistName = \"{duelist_name}\"").fetchone()
        yield deck[:hand_size]


def get_card_name_from_id(cur: Cursor, card_id: Id):
    card_name = cur.execute(f"SELECT CardName from Cards WHERE CardID = '{card_id}'").fetchone()

    if card_name is not None:
        card_name, = card_name

    return card_name


def get_hand_names(cur: Cursor, hand: Cards):
    hand_names = []
    for card in hand:
        hand_names.append(get_card_name_from_id(cur, card['id']))

    return hand_names


def get_card_id_from_name(cur: Cursor, player_cardname: str):
    card_id = cur.execute(f"SELECT CardID from Cards WHERE CardName = \"{player_cardname}\"").fetchone()

    if card_id is not None:
        card_id, = card_id

    return card_id


def get_card_type_from_id(cur: Cursor, card_id: Id):
    card_type = cur.execute(f"SELECT CardType from Cards WHERE CardID = \"{card_id}\"").fetchone()

    if card_type is not None:
        card_type, = card_type

    return card_type


def is_magic(cur: Cursor, card_id: Id):
    _type = get_card_type_from_id(cur, card_id)
    return _type is not None and _type == 'Magic'


def get_first_pos_in(cur: Cursor, target_card_name: str, cards: Cards, only_check_active: bool = False) \
        -> Optional[Position]:
    """ Returns the first position of the card name in `cards`. Returns `None` if there is none.
    Additionally, if `only_check_active` is `True`, only active cards will be checked. """

    return next((
        pos for (pos, card) in enumerate(cards)
        if card is not None and card['id'] == get_card_id_from_name(cur, target_card_name)
        and (not only_check_active or card['is_active'])
    ), None
    )


def get_first_monster_compatible_in(cur: Cursor, equip_id: Id, cards: Cards) -> Optional[Position]:
    """ Returns the position on the board of the first compatible monster with the given equip.
    Returns `None` if no monster is found. """

    for pos, card in enumerate(cards):
        if card is None:
            continue
        _tuple = cur.execute(
            f"SELECT * FROM 'Equipping' WHERE EquipID = '{equip_id}' AND EquippedID = '{card['id']}'"
        ).fetchone()
        if _tuple is not None:
            return pos

    return None


class StatCalculator(Protocol):
    def __call__(self, c: Cursor, i: Id, field: Field, equip_stage: EquipStage) -> Stat: ...


def _get_first_pos_max_f_in(cur: Cursor, f: StatCalculator, cards: Cards, field: Field, *,
                            look_facedown_cards: bool, only_check_active: bool = False) \
        -> tuple[Optional[Position], Stat]:
    """ Returns the first position and associated stat of the card with the best stat on a board
    from the calculation via function `f`. """

    pos, _max = None, 0
    for i, card in enumerate(cards):
        if card is None \
                or not look_facedown_cards and card['face'] == FACE_DOWN \
                or (only_check_active and not card['is_active']):
            continue
        stat = f(cur, card['id'], field, card.get('equip_stage'))
        if stat > _max:
            pos, _max = i, stat

    return pos, _max


def get_first_pos_of_true_max_stat_in(cur: Cursor, cards: Cards, field: Field, look_facedown_cards: bool,
                                      only_check_active: bool = False) -> tuple[Optional[Position], Stat]:
    """ Returns the first position and associated stat of the card with the best true max stat on a board. """

    return _get_first_pos_max_f_in(cur, calculate_true_max_stat, cards, field,
                                   look_facedown_cards=look_facedown_cards, only_check_active=only_check_active)


def get_first_pos_of_max_true_atk_in(cur: Cursor, cards: Cards, field: Field, look_facedown_cards: bool,
                                     only_check_active: bool = False) -> tuple[Optional[Position], Stat]:
    """ Returns the first position and associated stat of the card with the best true attack on a board. """

    return _get_first_pos_max_f_in(cur, calculate_true_atk_stat, cards, field,
                                   look_facedown_cards=look_facedown_cards, only_check_active=only_check_active)


def get_first_pos_of_max_true_def_in(cur: Cursor, cards: Cards, field: Field, look_facedown_cards: bool,
                                     only_check_active: bool = False) -> tuple[Optional[Position], Stat]:
    """ Returns the first position and associated stat of the card with the best true defense on a board. """

    return _get_first_pos_max_f_in(cur, calculate_true_def_stat, cards, field,
                                   look_facedown_cards=look_facedown_cards, only_check_active=only_check_active)


def get_first_pos_of_base_max_stat_plus_field_in(cur: Cursor, cards: Cards, field: Field, look_facedown_cards: bool) \
        -> tuple[Optional[Position], Stat]:
    """ Returns the first position and associated stat of the card with the best max stat + field on a board. """

    return _get_first_pos_max_f_in(cur, (lambda cs, c, f, s: calculate_max_base_stat_plus_field(cs, c, f)),
                                   cards, field, look_facedown_cards=look_facedown_cards)


def get_first_pos_of_base_max_stat_in(cur: Cursor, cards: Cards, look_facedown_cards: bool) \
        -> tuple[Optional[Position], Stat]:
    """ Returns the first position and associated stat of the card with the best max stat on a board. """

    return _get_first_pos_max_f_in(cur, (lambda cs, c, f, s: calculate_max_base_stat(cs, c)),
                                   cards, None, look_facedown_cards=look_facedown_cards)


def _get_first_pos_lowest_f_in(cur: Cursor, f: StatCalculator, cards: Cards, field: Field, *, look_facedown_cards: bool,
                               battle_mode: BattleMode = None) -> tuple[Optional[Position], Stat]:
    """ Returns the first position and associated stat of the card with the worst stat on a board
    from the calculation via function `f`. """

    pos, _min = None, 0
    for i, card in enumerate(cards):
        if card is None \
                or not look_facedown_cards and card['face'] == FACE_DOWN \
                or (battle_mode is not None and card['battle_mode'] != battle_mode):
            continue
        stat = f(cur, card['id'], field=field, equip_stage=card['equip_stage'])
        if _min == 0 or 0 < stat < _min:
            pos, _min = i, stat

    return pos, _min


def get_first_pos_of_lowest_true_max_stat_in(cur: Cursor, cards: Cards, field: Field, look_facedown_cards: bool,
                                             battle_mode: BattleMode = None) -> tuple[Optional[Position], Stat]:
    """ Returns the first position and associated stat of the card with the lowest true max stat on a board. """

    return _get_first_pos_lowest_f_in(cur, _calculate_max_stat_ai, cards, field,
                                      look_facedown_cards=look_facedown_cards, battle_mode=battle_mode)


def get_first_pos_of_lowest_true_atk_in(cur: Cursor, cards: Cards, field: Field, look_facedown_cards: bool,
                                        battle_mode: BattleMode = None) -> tuple[Optional[Position], Stat]:
    """ Returns the first position and associated stat of the card with the lowest true max stat on a board. """

    return _get_first_pos_lowest_f_in(cur, calculate_true_atk_stat, cards, field,
                                      look_facedown_cards=look_facedown_cards, battle_mode=battle_mode)


def is_boosted(typ: Type, field: Field = None) -> bool:
    return field is not None and \
           (field == 'Forest' and typ in ['Beast-Warrior', 'Insect', 'Plant', 'Beast']
            or field == 'Wasteland' and typ in ['Zombie', 'Dinosaur', 'Rock']
            or field == 'Mountain' and typ in ['Dragon', 'Winged-Beast', 'Thunder']
            or field == 'Sogen' and typ in ['Beast-Warrior', 'Warrior']
            or field == 'Umi' and typ in ['Aqua', 'Thunder', 'Sea Serpent']
            or field == 'Yami' and typ in ['Fiend', 'Spellcaster'])


def is_nerfed(typ: Type, field: Field = None) -> bool:
    return field is not None and \
           (field == 'Umi' and typ in ['Machine', 'Pyro']
            or field == 'Yami' and typ in ['Fairy'])


def is_stat_increased(_type: Type, old_field: Field, new_field: Field) -> bool:
    return is_nerfed(_type, old_field) and not is_nerfed(_type, new_field) \
           or not is_boosted(_type, old_field) and is_boosted(_type, new_field)


def is_stat_decreased(_type: Type, old_field: Field, new_field: Field) -> bool:
    return is_boosted(_type, old_field) and not is_boosted(_type, new_field) \
           or not is_nerfed(_type, old_field) and is_nerfed(_type, new_field)


def get_first_pos_of_type_in(cur: Cursor, _type: Type, cards: Cards, *, only_check_active: bool = False):
    """ Returns the first position of a given _type in a hand.
    Returns `None` if there are none. """

    pos = None
    for i, card in enumerate(cards):
        if card is None or only_check_active and not card['is_active']:
            continue

        card_type = get_card_type_from_id(cur, card['id'])

        if card_type == _type:
            return i

    return pos


def _apply_mods_stat(stat: Stat, _type: Type, field: Field = None, equip_stage: EquipStage = 0) -> Stat:
    result = stat
    result += 500 * is_boosted(_type, field=field)
    result -= 500 * is_nerfed(_type, field=field)
    result += 500 * equip_stage if equip_stage is not None else 0
    result = min(max(result, 0), 9_999)

    return result


def _calculate_max_stat_ai(cur: Cursor, card_id: Id, field: Field = None, equip_stage: EquipStage = 0) -> Stat:
    if card_id is None:
        return 0

    _type, _atk, _def = cur.execute(f"SELECT CardType, Attack, Defense FROM Cards WHERE CardID = {card_id}").fetchone()

    return _apply_mods_stat(max(_atk, _def), _type, field=field, equip_stage=equip_stage)


def calculate_true_max_stat(cur: Cursor, card_id: Id, field: Field, equip_stage: EquipStage) -> Stat:
    return _calculate_max_stat_ai(cur, card_id, field=field, equip_stage=equip_stage)


def calculate_max_base_stat_plus_field(cur: Cursor, card_id: Id, field: Field) -> Stat:
    return _calculate_max_stat_ai(cur, card_id, field=field)


def calculate_max_base_stat(cur: Cursor, card_id: Id) -> Stat:
    return _calculate_max_stat_ai(cur, card_id)


def calculate_true_atk_stat(cur: Cursor, card_id: Id, field: Field, equip_stage: EquipStage) -> Stat:
    if card_id is None:
        return 0

    _type, _atk = cur.execute(f"SELECT CardType, Attack FROM Cards WHERE CardID = {card_id}").fetchone()

    return _apply_mods_stat(_atk, _type, field=field, equip_stage=equip_stage)


def calculate_true_def_stat(cur: Cursor, card_id: Id, field: Field, equip_stage: EquipStage) -> Stat:
    if card_id is None:
        return 0

    _type, _def = cur.execute(f"SELECT CardType, Defense FROM Cards WHERE CardID = {card_id}").fetchone()

    return _apply_mods_stat(_def, _type, field=field, equip_stage=equip_stage)


# Sorting keys

def ascending_true_max_stat_sorting_key(cur: Cursor, card: Card, field: Field):
    return calculate_true_max_stat(cur, card['id'], field, card['equip_stage']), card['pos']


def descending_true_max_stat_sorting_key(cur: Cursor, card: Card, field: Field):
    return -calculate_true_max_stat(cur, card['id'], field, card['equip_stage']), card['pos']


def descending_true_atk_sorting_key(cur: Cursor, card: Card, field: Field):
    return -calculate_true_atk_stat(cur, card['id'], field=field, equip_stage=card['equip_stage']), card['pos']


def ascending_true_atk_sorting_key(cur: Cursor, card: Card, field: Field):
    return calculate_true_atk_stat(cur, card['id'], field=field, equip_stage=card['equip_stage']), card['pos']


def descending_true_def_sorting_key(cur: Cursor, card: Card, field: Field):
    return -calculate_true_def_stat(cur, card['id'], field=field, equip_stage=card['equip_stage']), card['pos']


def is_empty(row: Cards) -> bool:
    return row == [None] * 5


MIN_POS, MAX_POS = 0, 4
BACKROW_OFFSET = 10
MIN_BACKROW_POS, MAX_BACKROW_POS = MIN_POS - BACKROW_OFFSET, MAX_POS - BACKROW_OFFSET


def encode_backrow_pos(pos: Position) -> Position:
    assert MIN_POS <= pos <= MAX_POS
    return pos - BACKROW_OFFSET


def decode_backrow_pos(board_pos: Position) -> Position:
    assert MIN_BACKROW_POS <= board_pos <= MAX_BACKROW_POS
    return board_pos + BACKROW_OFFSET


Star = str


def has_advantage_over(atk_star: Star, def_star: Star) -> bool:
    """ Returns `True` if and only if `atk_star` has the advantage over `def_star`. """
    return (atk_star, def_star) in [
        ('Sun', 'Moon'),
        ('Moon', 'Venus'),
        ('Venus', 'Mercury'),
        ('Mercury', 'Sun'),

        ('Mars', 'Jupiter'),
        ('Jupiter', 'Saturn'),
        ('Saturn', 'Uranus'),
        ('Uranus', 'Pluto'),
        ('Pluto', 'Neptune'),
        ('Neptune', 'Mars'),
    ]


def check_ritual(cur: Cursor, ritual_id: Id, frontrow: Cards) -> bool:
    frontrow_ids = set(card['id'] for card in filter(None, frontrow))
    t1, t2, t3, result_id = cur.execute(
        f"SELECT Tribute1, Tribute2, Tribute3, Result FROM Rituals WHERE RitualCard = '{ritual_id}'"
    ).fetchone()
    tribute_ids = {t1, t2, t3}

    return tribute_ids == frontrow_ids


if __name__ == '__main__':
    con, cur = db.connect_to_YFM_database()

    for hand in generate_new_hands(cur, 'Shadi'):
        print(get_hand_names(cur, hand))

    con.close()

