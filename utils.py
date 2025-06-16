import random
from sqlite3 import Cursor
from typing import Protocol, Generator, Iterable, Reversible

import db
from types_ import Id, Cards, Position, Stat, Field, Type, Card, Face, BattleMode, is_boosted_by, \
    is_nerfed_by, is_non_monster


START_EXODIA_ID, END_EXODIA_ID = 17, 21

CARD_LIMIT = 3
CARD_LIMIT_EXODIA = 1
DECK_SIZE = 40


def generate_decks(cursor: Cursor, duelist_name: str, num_decks: int = 1)\
        -> Generator[list[Id]]:
    """ Creates an iterator of `num_decks` decks of the desired `duelist_name`. """

    pool_type = 'Deck'

    # Pool type id
    pool_type_id, = cursor.execute(
        f"SELECT DuelistPoolTypeID "
        f"FROM DuelistPoolTypes "
        f"WHERE DuelistPoolTypes.DuelistPoolType = ?",
        (pool_type,)
    ).fetchone()

    # (cardID, prob) iterator
    cards_probs = list(cursor.execute(
        f"SELECT CardID, Prob "
        f"FROM DuelistPoolSamplingRates "
        f"LEFT JOIN Duelists ON Duelists.DuelistID = DuelistPoolSamplingRates.DuelistID "
        f"WHERE DuelistPoolSamplingRates.DuelistPoolTypeID = ? "
        f"AND Duelists.DuelistName = ? "
        f"AND DuelistPoolSamplingRates.Prob > 0 ",
        (pool_type_id, duelist_name)
    ))

    if len(cards_probs) == 0:
        raise ValueError(f"Unknown duelist name '{duelist_name}'")

    for _ in range(num_decks):
        cards_to_draw = [
            {
                'id': card_id,
                'prob': prob,  # out of 2048
                'limit': CARD_LIMIT
                if card_id not in range(START_EXODIA_ID, END_EXODIA_ID + 1)
                else CARD_LIMIT_EXODIA
            }
            for (card_id, prob) in cards_probs
        ]

        # Build Deck
        deck_ids = []
        # print(clean_desc(cur.execute("SELECT * FROM Cards").description))
        for _ in range(DECK_SIZE):
            chosen, = random.choices(cards_to_draw, weights=[card['prob'] for card in cards_to_draw])
            # print(chosen)
            deck_ids.append(chosen['id'])
            chosen['limit'] -= 1
            if chosen['limit'] == 0:
                chosen['prob'] = 0
            # print(cards_probs_nums)
        # print(deck_ids)

        yield deck_ids


def generate_new_hands(cursor: Cursor, duelist_name: str, num_hands: int = 1)\
        -> Generator[list[Id]]:
    for deck in generate_decks(cursor, duelist_name, num_decks=num_hands):
        hand_size, = cursor.execute(
            f"SELECT HandSize "
            f"FROM Duelists "
            f"WHERE Duelists.DuelistName = ?",
            (duelist_name,)
        ).fetchone()

        yield deck[:hand_size]


# def get_card_name_from_id(cursor: Cursor, card_id: Id)\
#         -> str | None:
#     card_name, = cursor.execute(
#         f"SELECT CardName "
#         f"FROM Cards "
#         f"WHERE CardID = ?",
#         (card_id,)
#     ).fetchone()
#
#     # card_name, = card_name if card_name else (None,)
#
#     return card_name


# def get_hand_names(hand: Cards)\
#         -> list[str]:
#     hand_names = []
#     for card in hand:
#         # # hand_names.append(get_card_name_from_id(cur, card['id']))
#         # hand_names.append(get_card_name_from_id(cur, card.id))
#         hand_names.append(card.name)
#
#     return hand_names


def get_card_id_from_name(cursor: Cursor, cardname: str)\
        -> Id:
    card_id, = cursor.execute(
        f"SELECT CardID "
        f"FROM Cards "
        f"WHERE CardName = ?",
        (cardname,)
    ).fetchone()

    # card_id, = card_id if card_id else (None,)

    return card_id


def get_card_type_from_id(cursor: Cursor, card_id: Id)\
        -> Type:
    card_type, = cursor.execute(
        f"SELECT CardType "
        f"FROM Cards "
        f"WHERE CardID = ?",
        (card_id,)
    ).fetchone()

    # card_type, = card_type if card_id else (None,)

    return card_type


# def is_monster(cur: Cursor, card_id: Id)\
#         -> bool:
#     _type = get_card_type_from_id(cur, card_id)
#     return _type in Type.monsters


def is_magic(cursor: Cursor, card_id: Id)\
        -> bool:
    _type = get_card_type_from_id(cursor, card_id)
    return _type == Type.MAGIC


def get_first_card_in(target_card_name: str, cards: Iterable[Card],
                     *,
                     only_check_active: bool = False) \
        -> Card | None:
    """ Returns the first card in `cards` matching the provided name.
    Returns `None` if there is none.
    Additionally, if `only_check_active` is `True`, only active cards will be checked. """

    return next(
        (
            card for card in cards
            if card is not None and card.name == target_card_name
            and (not only_check_active or card.is_active)
        ),
        None
    )


def get_last_card_in(target_card_name: str, cards: Reversible[Card],
                    *,
                    only_check_active: bool = False) \
        -> Card | None:
    """ Returns the last card in `cards` with the provided name.
    Returns `None` if there is none.
    Additionally, if `only_check_active` is `True`, only active cards will be checked. """

    return get_first_card_in(
        target_card_name, reversed(cards),
        only_check_active=only_check_active
    )


def get_first_card_equipable_with_in(cursor: Cursor, equip_id: Id, cards: Cards) \
        -> Card | None:
    """ Returns the first card compatible with the provided equip id.
    Returns `None` if no monster is found. """

    for card in cards:
        if card is None:
            continue
        _tuple = cursor.execute(
            f"SELECT * "
            f"FROM 'Equipping' "
            f"WHERE EquipID = ? "
            f"AND EquippedID = ?",
            (equip_id, card.id)
        ).fetchone()
        if _tuple is not None:
            return card

    return None


class StatCalculator(Protocol):
    def __call__(self, card: Card) \
            -> Stat:
        ...


def _first_card_with_best_f_in(f: StatCalculator, cards: Cards,
                               *,
                               look_facedown_cards: bool,
                               only_check_active: bool = False) \
        -> tuple[Card | None, Stat]:
    """ Returns the first card and associated stat with the 'best stat' on a board
    calculated from function `f`. """

    max_card, max_stat = None, None

    for card in cards:
        if card is None \
                or not look_facedown_cards and card.face == Face.DOWN \
                or (only_check_active and not card.is_active) \
                or (stat := f(card)) is None:
            continue

        if max_stat is None or stat > max_stat:
            max_card, max_stat = card, stat

    return max_card, max_stat


def first_card_with_best_true_max_stat_in(cards: Cards,
                                          *,
                                          look_facedown_cards: bool,
                                          only_check_active: bool = False) \
        -> tuple[Card | None, Stat]:
    """ Returns the first position and associated stat of the card with the best true max stat on a board. """

    return _first_card_with_best_f_in(
        lambda card: card.true_max_stat, cards,
        look_facedown_cards=look_facedown_cards,
        only_check_active=only_check_active
    )


def first_card_with_best_true_atk_in(cards: Cards,
                                     *,
                                     look_facedown_cards: bool,
                                     only_check_active: bool = False) \
        -> tuple[Card | None, Stat]:
    """ Returns the first card and associated stat of the card with the best true attack on a board. """

    return _first_card_with_best_f_in(
        lambda card: card.true_attack, cards,
        look_facedown_cards=look_facedown_cards,
        only_check_active=only_check_active
    )


def first_card_with_best_true_def_in(cards: Cards,
                                     *,
                                     look_facedown_cards: bool,
                                     only_check_active: bool = False) \
        -> tuple[Card | None, Stat]:
    """ Returns the first card and associated stat of the card with the best true defense on a board. """

    return _first_card_with_best_f_in(
        lambda card: card.true_defense, cards,
        look_facedown_cards=look_facedown_cards,
        only_check_active=only_check_active
    )


def first_card_with_best_max_base_stat_plus_field_in(cards: Cards,
                                                     *,
                                                     look_facedown_cards: bool) \
        -> tuple[Card | None, Stat]:
    """ Returns the first card and associated stat of the card with the best max stat + field on a board. """

    return _first_card_with_best_f_in(
        lambda card: card.max_base_stat_plus_field, cards,
        look_facedown_cards=look_facedown_cards
    )


def first_card_with_best_max_base_stat_in(cards: Cards,
                                          *,
                                          look_facedown_cards: bool) \
        -> tuple[Card | None, Stat]:
    """ Returns the first card and associated stat of the card with the best max stat on a board. """

    return _first_card_with_best_f_in(
        lambda card: card.max_base_stat, cards,
        look_facedown_cards=look_facedown_cards
    )


def _first_card_worst_f_in(f: StatCalculator, cards: Cards,
                           *,
                           look_facedown_cards: bool,
                           battle_mode: BattleMode = None) \
        -> tuple[Card | None, Stat]:
    """ Returns the first card and associated stat of the card with the worst stat on a board
    from the calculation via function `f`. """

    min_card, min_stat = None, 0
    for card in cards:
        if card is None \
                or is_non_monster(card.type) \
                or not look_facedown_cards and card.face == Face.DOWN \
                or (battle_mode is not None and card.battle_mode != battle_mode):
            continue
        stat = f(card)
        if min_stat == 0 or 0 <= stat < min_stat:
            min_card, min_stat = card, stat

    return min_card, min_stat


def first_card_with_worst_true_max_stat_in(cards: Cards,
                                           *,
                                           look_facedown_cards: bool,
                                           battle_mode: BattleMode = None) \
        -> tuple[Card | None, Stat]:
    """ Returns the first card and associated stat of the card with the lowest true max stat on a board. """

    return _first_card_worst_f_in(
        lambda card: card.true_max_stat, cards,
        look_facedown_cards=look_facedown_cards,
        battle_mode=battle_mode
    )


def first_card_with_worst_true_atk_in(cards: Cards,
                                      *,
                                      look_facedown_cards: bool,
                                      battle_mode: BattleMode = None) \
        -> tuple[Card | None, Stat]:
    """ Returns the first card and associated stat of the card with the lowest true max stat on a board. """

    return _first_card_worst_f_in(
        lambda card: card.true_attack, cards,
        look_facedown_cards=look_facedown_cards,
        battle_mode=battle_mode
    )


def is_stat_increased(type_: Type, old_field: Field, new_field: Field) \
        -> bool:
    """ Returns `True` if and only if a type strictly benefits from the `new_field`. """

    return (
        is_nerfed_by(type_, old_field) and not is_nerfed_by(type_, new_field)
        or not is_boosted_by(type_, old_field) and is_boosted_by(type_, new_field)
    )


def is_stat_decreased(type_: Type, old_field: Field, new_field: Field) \
        -> bool:
    """ Returns `True` if and only if a type is strictly weakened by the `new_field`. """

    return (
        is_boosted_by(type_, old_field) and not is_boosted_by(type_, new_field)
        or not is_nerfed_by(type_, old_field) and is_nerfed_by(type_, new_field)
    )


def first_card_with_type_in(type_: Type, cards: Cards,
                            *,
                            only_check_active: bool = False)\
        -> Card | None:
    """ Returns the first position of a given _type in a hand.
    Returns `None` if there are none. """

    for card in cards:
        if card is None or only_check_active and not card.is_active:
            continue

        # card_type = get_card_type_from_id(cur, card.id)

        if card.type == type_:
            return card

    return None


# Sorting keys

def ascending_true_max_stat_sorting_key(card: Card)\
        -> tuple[Stat, Position]:
    return card.true_max_stat, card.pos


def descending_true_max_stat_sorting_key(card: Card)\
        -> tuple[Stat, Position]:
    return (-1)*card.true_max_stat, card.pos


def descending_true_atk_sorting_key(card: Card)\
        -> tuple[Stat, Position]:
    return -card.true_attack, card.pos


def ascending_true_atk_sorting_key(card: Card)\
        -> tuple[Stat, Position]:
    return card.true_attack, card.pos


def descending_true_def_sorting_key(card: Card) \
        -> tuple[Stat, Position]:
    return -card.true_defense, card.pos


def is_empty(row: Cards) -> bool:
    return all(card is None for card in row)


# def has_advantage_over(atk_star: Star_dic, def_star: Star_dic) -> bool:
#     """ Returns `True` if and only if `atk_star` has the advantage over `def_star`. """
#     return (atk_star, def_star) in {
#         ('Sun', 'Moon'),
#         ('Moon', 'Venus'),
#         ('Venus', 'Mercury'),
#         ('Mercury', 'Sun'),
#
#         ('Mars', 'Jupiter'),
#         ('Jupiter', 'Saturn'),
#         ('Saturn', 'Uranus'),
#         ('Uranus', 'Pluto'),
#         ('Pluto', 'Neptune'),
#         ('Neptune', 'Mars'),
#     }


class Summon:
    def __init__(self, is_successful: bool, sacrifices: set[Id] = None, result_id: Id = None):
        self.is_successful = is_successful
        self.sacrifices = sacrifices
        self.result_id = result_id


def check_ritual(cursor: Cursor, ritual_id: Id, frontrow: Cards)\
        -> Summon:
    frontrow_ids = set(card.id for card in filter(None, frontrow))
    t1, t2, t3, result_id = cursor.execute(
        f"SELECT Tribute1, Tribute2, Tribute3, Result "
        f"FROM Rituals "
        f"WHERE RitualCard = ?",
        (ritual_id,)
    ).fetchone()
    tribute_ids = {t1, t2, t3}

    is_successful = tribute_ids == frontrow_ids
    return Summon(*(is_successful, {t1, t2, t3}, result_id) if is_successful else (False, None, None))
    # return {
    #     'is_successful': is_successful,
    #     'sacrifices': {t1, t2, t3} if is_successful else None,
    #     'result_id': result_id if is_successful else None
    # }


if __name__ == '__main__':
    con, cur = db.connect_to_YFM_database()

    # for hand in generate_new_hands(cur, 'Shadi'):
    #     print(get_hand_names(cur, hand))

    con.close()
