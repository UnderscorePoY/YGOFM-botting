from __future__ import annotations
from ai import *
from probability_tree import *

import db

# Card ids
from types_ import Id, Cards, Position, Stat, Field, EquipStage, Opponent


# ID, NAME, STAR1, STAR2, TYPE, ATTACK, DEFENSE = 0, 1, 3, 4, 6, 8, 9


class Combo:
    """ Represents a combo the AI can play. """

    # def __init__(self, ordering: list[Position] = None, ids: list[Id] = None,
    #              result_id: Id = None, equip_stage: EquipStage = 0, result_max_stat: Stat = 0) \
    #         -> None:
    #     self.ordering: list[Position] = []
    #     if ordering is not None:
    #         for order in ordering:
    #             self.ordering.append(order)
    #
    #     self.ids: list[Id] = []
    #     if ids is not None:
    #         for id_ in ids:
    #             id_.validate()
    #             self.ids.append(id_)
    #
    #     if result_id is not None:
    #         result_id.validate()
    #     self._result_id: Id = result_id
    #
    #     self.equip_stage: EquipStage = equip_stage
    #     self.result_max_stat: Stat = result_max_stat

    def __init__(self, initial_card: Card = None) \
            -> None:
        self.cards: list[Card] = []
        if initial_card is not None:
            self.cards.append(initial_card)

        self.result: Card | None = initial_card

        self.max_stat: Stat | None = None
        self.update_max_stat()

        # self.equip_stage: EquipStage = equip_stage
        # self.result_max_stat: Stat = result_max_stat

    def __len__(self):
        return len(self.cards)

    # @property
    # def result_id(self) -> Id:
    #     return self._result_id
    #
    # @result_id.setter
    # def result_id(self, id_: Id) -> None:
    #     id_.validate()
    #     self.result_id = id_

    # def update(self, ordering: Position = None, id_: Id = None,
    #            result_id: Id = None, delta_equip_stage: EquipStage = 0, result_max_stat: Stat = 0) \
    #         -> None:
    #     """ Updates the combo. Since AI can only play compatible equips, `delta_equip_stage == 0` implies the
    #     equip stage is reset to `0` instead of added to the previous equip stage. """
    #     if ordering is not None:
    #         self.ordering.append(ordering)
    #
    #     if id_ is not None:
    #         id_.validate()
    #         self.ids.append(id_)
    #
    #     if result_id is not None:
    #         result_id.validate()
    #         self._result_id = result_id
    #
    #     if delta_equip_stage is not None:
    #         if delta_equip_stage == 0:
    #             self.equip_stage = 0
    #         else:
    #             self.equip_stage += delta_equip_stage
    #
    #     if result_max_stat is not None:
    #         self.result_max_stat = result_max_stat

    def update(self, combo_card: Card = None, result: Card = None,
               delta_equip_stage: EquipStage = 0, reset_equip_stage: bool = False) \
            -> None:
        """
        Updates the combo.
        `result` must be the card without any equip modifications : these are handled somewhere else TODO.
        `reset_equip_stage == True` ignores `delta_equip_stage` and resets the equip stage to `0`.
        """

        # if result is not None and delta_equip_stage != 0:
        #     raise ValueError("A single card can't both change the card and update its equip stage.")

        if combo_card is not None:
            self.cards.append(combo_card)

        if result is not None:
            self.result = result

        if reset_equip_stage:
            self.result.equip_stage = EquipStage(0)
        else:
            if self.result.equip_stage:
                self.result.equip_stage += delta_equip_stage

        self.update_max_stat()

    def update_max_stat(self) -> None:
        """
        Updates the max stat of the current combo :
            - single card from the hand => max base stat ;
            - single card from the board => true max stat ;
            - otherwise => max base stat plus field.
        """

        if len(self) == 0:
            self.max_stat = None
        elif len(self) == 1:
            if self.cards[0].pos.mode == Position.Mode.HAND:
                self.max_stat = self.result.max_base_stat
            else:
                self.max_stat = self.result.true_max_stat
        else:
            self.max_stat = self.result.max_base_stat_plus_field

    def is_only_cards_from_the_hand(self) \
            -> bool:
        """ Returns `True` if and only if all cards from the combo are from the hand. """

        return all((card.pos >= 0 for card in self.cards)) if len(self) > 0 else False

    def is_playing_on_top_of_a_card_on_the_field(self) \
            -> bool:
        """ Returns `True` if and only if the combo consists of playing on top of a card on the field. """

        return len(self) >= 2 and self.cards[0].pos < 0

    def is_strictly_better_find_best_combo(self, other: Combo):
        """ Return `True` if and only if `self` is a strictly better combo than `other`. """

        s, o = self.max_stat, other.max_stat
        l_s, l_o = len(self), len(other)
        return (
            s and not o
            or s and o and (
                s > o
                or s == o and (
                    min(l_s, l_o) == 1
                    and max(l_s, l_o) > 1
                    and min([c.pos for c in self.cards]) < min([c.pos for c in other.cards])

                    or min(l_s, l_o) > 1
                    # and max(l_s, l_o) > 1  # if min is > 1, then max is > 1 too ...
                    and l_s < l_o
                )
            )
        )

    def is_strictly_better_improve_monster(self, other: Combo):
        s, o = self.max_stat, other.max_stat
        l_s, l_o = len(self), len(other)
        # TODO : maybe the final `min < min` is useless ?
        return (
            s and not o
            or s and o and (
                s > o
                or s == o and (
                    l_s < l_o
                    or l_s == l_o and min([c.pos for c in self.cards]) < min([c.pos for c in other.cards])
                )
            )
        )

# # Best combo attributes
# ORDERING = 'ordering'
# IDS = 'ids'
# RESULT_ID = 'result_id'
# EQUIP_STAGE = 'equip_stage'
# RESULT_MAX_STAT = 'result_max_stat'


DEFAULT_BEST_COMBO_MAX_FUSION_LENGTH = 5


def find_best_combo_in_ai_hand(cursor: Cursor, hand: Cards,
                               /,
                               field: Field, max_fusion_length: int,
                               board_card: Card = None, best_combo: Combo = None, current_combo: Combo = None) \
        -> Combo:
    # Max length reached
    if max_fusion_length == 0:
        return best_combo

    # board_id, board_pos, board_equip_level = (board_card.id, board_card.pos, board_card.equip_stage) \
    #     if board_card is not None \
    #     else (None, None, 0)

    # Base case
    if current_combo is None:
        current_combo = Combo(board_card)
        # if board_card is None:
        #     current_combo = Combo()
        # else:
        #     # current_combo = Combo(ordering=[board_pos], ids=[board_id], result_id=board_id,
        #     #                       equip_stage=board_equip_level,
        #     #                       result_max_stat=board_card.true_max_stat)
        #     current_combo = Combo(board_card)

    if best_combo is None:
        best_combo = deepcopy(current_combo)

    for card in hand:
        # Skip card if same slot in hand than the one on the board
        if board_card is not None and board_card.pos.idx == card.pos.idx:
            continue

        # Skip cards already in the current combo
        if card in current_combo.cards:
            continue

        old_combo = deepcopy(current_combo)

        # Initialise with a card from the hand
        if current_combo.result is None:
            current_combo.update(card, result=card)

        # Continue previous combo with cards from the hand
        else:
            # Check if we're equipping a compatible item or performing a valid fusion
            equipped_equip = cursor.execute(
                f"SELECT EquippedID, EquipID FROM Equipping "
                f"WHERE EquippedID = ? AND EquipID = ? "
                f"   OR EquippedID = ? AND EquipID = ?",
                (current_combo.result.id, card.id, card.id, current_combo.result.id)
            ).fetchone()
            fusion = cursor.execute(
                f"SELECT Result FROM Fusions "
                f"WHERE Material1 = ? AND Material2 = ?",
                (current_combo.result.id, card.id)
            ).fetchone()

            result_id, reset_equip_stage = None, False
            if equipped_equip is not None:
                result_id = equipped_equip[0]
            elif fusion is not None:
                result_id = int(fusion[0])
                reset_equip_stage = True

            # Non-compatible equip / fusion
            if result_id is None:
                continue

            result = Card(cursor, Id(result_id), field)  # TODO: more ?
            delta_equip_stage = (
                0 if equipped_equip is None else
                2 if equipped_equip[1] == Id.MEGAMORPH else
                1
            )
            current_combo.update(
                card, result=result,
                reset_equip_stage=reset_equip_stage,
                delta_equip_stage=EquipStage(delta_equip_stage)
            )

        # Update best combo / don't change the order of the conditions
        if current_combo.is_strictly_better_find_best_combo(best_combo):
            best_combo = deepcopy(current_combo)

        best_combo = find_best_combo_in_ai_hand(
            cursor, hand,
            board_card=board_card, best_combo=best_combo, max_fusion_length=max_fusion_length - 1, field=field,
            current_combo=current_combo
        )

        current_combo = old_combo

    return best_combo


def find_best_combo_in_ai_board_and_hand(cursor: Cursor, hand: Cards,
                                         /,
                                         field: Field,
                                         monster_board: Cards = None, max_fusion_length: int = None) \
        -> Combo:
    best_combo = None

    if max_fusion_length is None:
        max_fusion_length = DEFAULT_BEST_COMBO_MAX_FUSION_LENGTH

    # First, iterate through monster cards on the board
    if monster_board is not None:
        for board_card in monster_board:
            if board_card is None:
                continue

            best_combo = find_best_combo_in_ai_hand(cursor, hand, board_card=board_card, best_combo=best_combo,
                                                    max_fusion_length=max_fusion_length, field=field,
                                                    current_combo=None)

    # Finish with only cards from the hand
    return find_best_combo_in_ai_hand(cursor, hand, board_card=None, best_combo=best_combo,
                                      max_fusion_length=max_fusion_length, field=field,
                                      current_combo=None)


DEFAULT_IMPROVE_MONSTER_MAX_LENGTH = 4


def improve_monster_from_ai_hand(cursor: Cursor, hand: Cards, board_card: Card, field: Field,
                                 /,
                                 max_improve_length: int,
                                 best_combo: Combo = None, current_combo: Combo = None) \
        -> Combo:
    # if max_improve_length is None:
    #     max_improve_length = DEFAULT_IMPROVE_MONSTER_MAX_LENGTH

    # Max length reached
    if max_improve_length == 0:
        return best_combo

    # board_id, board_pos, board_equip_level = (board_card.id, board_card.pos, board_card.equip_stage) \
    #     if board_card is not None \
    #     else (None, None, 0)

    # Base case
    if current_combo is None:
        current_combo = Combo(board_card)

    if best_combo is None:
        best_combo = deepcopy(current_combo)

    for card in hand:
        # Skip cards already in the current combo
        if card in current_combo.cards:
            continue

        old_combo = deepcopy(current_combo)

        # Check if we're equipping a compatible item or performing a valid fusion
        equipped_equip = cursor.execute(
            f"SELECT EquippedID, EquipID FROM Equipping "
            f"WHERE EquippedID = ? AND EquipID = ? "
            f"   OR EquippedID = ? AND EquipID = ?",
            (current_combo.result.id, card.id, card.id, current_combo.result.id)
        ).fetchone()
        fusion = cursor.execute(
            f"SELECT Result FROM Fusions "
            f"WHERE Material1 = ? AND Material2 = ?",
            (current_combo.result.id, card.id)
        ).fetchone()

        result_id, reset_equip_stage = None, False
        if equipped_equip is not None:
            result_id = equipped_equip[0]
        elif fusion is not None:
            result_id = int(fusion[0])
            reset_equip_stage = True

        # Non-compatible equip / fusion
        if result_id is None:
            continue

        current_combo.update(
            card, result=Card(cursor, Id(result_id), field),
            reset_equip_stage=reset_equip_stage,
            delta_equip_stage=EquipStage(
                0 if equipped_equip is None
                else 2 if equipped_equip[1] == Id.MEGAMORPH
                else 1
            )
        )

        # Update best combo
        if current_combo.is_strictly_better_improve_monster(best_combo):
            best_combo = deepcopy(current_combo)

        best_combo = improve_monster_from_ai_hand(
            cursor, hand, board_card, field,
            max_improve_length=max_improve_length - 1,
            best_combo=best_combo, current_combo=current_combo
        )

        current_combo = old_combo

    return best_combo


def improve_monster_from_ai_board_and_hand(cursor: Cursor, hand: Cards, field: Field,
                                           /,
                                           monster_board: Cards = None,
                                           max_improve_length: int = None) \
        -> Action | None:
    """ Returns the 'improve' action, or `None` if no improvement is found. """

    combo = None

    if max_improve_length is None:
        max_improve_length = DEFAULT_IMPROVE_MONSTER_MAX_LENGTH

    if monster_board is None:
        return combo

    # Iterate from lowest *true* max stat to highest (earlier cards are looked at first in case of a tie).
    ordered_monster_board = sorted(
        list(filter(lambda x: x is not None, monster_board)),
        key=ascending_true_max_stat_sorting_key
    )

    for board_card in ordered_monster_board:
        combo = improve_monster_from_ai_hand(
            cursor, hand, board_card, field,
            max_improve_length=max_improve_length,
            best_combo=combo, current_combo=None
        )
        if combo.result == board_card \
                and combo.result.equip_stage == board_card.equip_stage \
                and combo.max_stat <= board_card.max_base_stat_plus_field:
            combo = None

        if combo is not None:
            return convert_best_combo(combo)

    return None


traps_list_descending: list[str] = [  # Order compatible with AI routines
    'Widespread Ruin',
    'Acid Trap Hole',
    'Invisible Wire',
    'Bear Trap',
    'Eatgaboon',
    'House of Adhesive Tape',
    'Fake Trap'
]

# TODO : can you create enums with more data inside ?
support_type_with_field: dict[Type, list[Field]] = {  # Order of fields compatible with AI routines.
    Type.AQUA: [Field.UMI],
    Type.BEAST: [Field.FOREST],
    Type.BEAST_WARRIOR: [Field.SOGEN, Field.FOREST],
    Type.DINOSAUR: [Field.WASTELAND],
    Type.DRAGON: [Field.MOUNTAIN],
    # 'Fairy': [],
    Type.FIEND: [Field.YAMI],
    Type.FISH: [Field.UMI],
    Type.INSECT: [Field.FOREST],
    # 'Machine': [],
    Type.PLANT: [Field.FOREST],
    # 'Pyro': [],
    # 'Reptile': [],
    Type.ROCK: [Field.WASTELAND],
    Type.SEA_SERPENT: [Field.UMI],
    Type.SPELLCASTER: [Field.YAMI],
    Type.THUNDER: [Field.MOUNTAIN, Field.UMI],
    Type.WARRIOR: [Field.SOGEN],
    Type.WINGED_BEAST: [Field.MOUNTAIN],
    Type.ZOMBIE: [Field.WASTELAND]
}


# def best_combo_consists_of_only_cards_from_the_hand(best_combo: Combo) \
#         -> bool:
#     """ Returns `True` if and only if all cards from the combo are from the hand. """
#
#     return False if best_combo is None or len(best_combo.cards) == 0 else \
#         all((card.pos >= 0 for card in best_combo.cards))
#
#
# def best_combo_consists_of_playing_on_top_of_a_card_on_the_field(best_combo: Combo) \
#         -> bool:
#     """ Returns `True` if and only if the combo consists of playing on top of a card on the field. """
#
#     return len(best_combo.cards) >= 2 and best_combo.cards[0].pos < 0


def convert_best_combo(best_combo: Combo) \
        -> Action | None:
    """ Converts the best combo into actions. Returns `None` if no combo is found. """

    if best_combo.is_only_cards_from_the_hand():
        return Action([Action.Description(card.pos, Face.UP) for card in best_combo.cards])

    # Bug : if monster + magic, then simply trigger the magic
    if best_combo.is_playing_on_top_of_a_card_on_the_field():
        # if len(best_combo) == 2 and utils.is_magic(cur, best_combo.ids[1]):  # TODO: get rid of database call
        if len(best_combo) == 2 and best_combo.cards[1].type == Type.MAGIC:
            return Action([Action.Description(best_combo.cards[1].pos, Face.UP)])

        return Action([Action.Description(card.pos, Face.UP) for card in best_combo.cards])

    return None


def lbl_set_magic_ritual_magic(hand_pos: Position, ai_backrow: Cards) -> Action:
    """ Returns an action involving a Magic/Ritual. """

    if all(ai_backrow):
        action = Action([Action.Description(hand_pos, Face.UP)])
    else:
        action = Action([Action.Description(hand_pos, Face.DOWN)])
    return action


def lbl_set_magic_trap(hand_pos: Position, ai_backrow: Cards) -> Actions:
    """ Returns an action involving a Trap. """

    if all(ai_backrow):
        actions = Actions([
            Action([
                Action.Description(Position(back_idx, Position.Mode.BACKROW), Face.UP),
                Action.Description(hand_pos, Face.UP)
            ], odds=(1, 5))
            for back_idx in range(0, 5)
        ])
    else:
        actions = Actions([
            Action([Action.Description(hand_pos, Face.DOWN)])
        ])

    return actions


def lbl_set_magic_equip(hand_pos: Position, ai_backrow: Cards, ai_frontrow: Cards, equip_id: Id) \
        -> Actions:
    """ Returns actions involving an Equip. """

    # Backrow is full
    if all(ai_backrow):
        # Find the first compatible monster
        monster = get_first_card_equipable_with_in(cur, equip_id, ai_frontrow)
        if monster is not None:
            actions = [
                Action([
                    Action.Description(monster.pos, Face.UP),
                    Action.Description(hand_pos, Face.UP)
                ])
            ]
        # No compatible monster
        else:
            # Play over weakest monster
            if any(ai_frontrow):
                monster, _ \
                    = first_card_with_worst_true_max_stat_in(ai_frontrow, look_facedown_cards=True)
                actions = [
                    Action([
                        Action.Description(monster.pos, Face.UP),
                        Action.Description(hand_pos, Face.UP)
                    ])
                ]
            # Play over random backrow slot
            else:
                actions = [
                    Action([
                        Action.Description(Position(back_idx, Position.Mode.BACKROW), Face.UP),
                        Action.Description(hand_pos, Face.UP)
                    ], odds=(1, 5))
                    for back_idx in range(0, 5)
                ]
    # Backrow is not full
    else:
        actions = [
            Action([Action.Description(hand_pos, Face.DOWN)])
        ]

    return Actions(actions)


def lbl_set_magic(ai_player: Opponent) -> Actions:
    """ Returns actions corresponding to the LBL_SET_MAGIC routine. """

    # Trap
    hand_card = first_card_with_type_in(Type.TRAP, ai_player.hand)
    if hand_card is not None:
        actions = lbl_set_magic_trap(hand_card.pos, ai_player.backrow)
        return actions

    # Equip
    hand_card = first_card_with_type_in(Type.EQUIP, ai_player.hand)
    if hand_card is not None:
        actions = lbl_set_magic_equip(hand_card.pos, ai_player.backrow, ai_player.frontrow, hand_card.id)
        return actions

    # Magic
    hand_card = first_card_with_type_in(Type.MAGIC, ai_player.hand)
    if hand_card is not None:
        action = lbl_set_magic_ritual_magic(hand_card.pos, ai_player.backrow)
        return Actions([action])

    # Ritual
    hand_card = first_card_with_type_in(Type.RITUAL, ai_player.hand)
    if hand_card is not None:
        action = lbl_set_magic_ritual_magic(hand_card.pos, ai_player.backrow)
        return Actions([action])

    # Only monsters
    hand_card, _ = first_card_with_best_max_base_stat_in(ai_player.hand, look_facedown_cards=True)
    actions = Actions([
        Action([Action.Description(hand_card.pos, Face.DOWN)])
    ])
    return actions


def lbl_find_best_combo(cursor: Cursor, ai_player: Opponent, field: Field) -> Actions:
    """ Returns a converted list of actions. """

    best_combo = find_best_combo_in_ai_board_and_hand(
        cursor, ai_player.hand,
        monster_board=ai_player.frontrow, max_fusion_length=get_ai_stats(ai_player.name).max_fusion_length,
        field=field
    )

    actions = convert_best_combo(best_combo)
    if actions is not None:
        return Actions([actions])

    # No combo play -> set magic
    # if best_combo.max_stat == 0:
    if best_combo.max_stat is None:  # TODO: verify
        actions = lbl_set_magic(ai_player)
        return actions

    # Doing nothing to a monster from the board -> compatible field
    # best_type = utils.get_card_type_from_id(cur, best_combo.ids[0])
    best_type = best_combo.cards[0].type
    for support_field in support_type_with_field.get(best_type, []):
        # This skips the second field if there is a second one
        if field is not None and field == support_field:
            break

        card = get_first_card_in(support_field, ai_player.hand)
        if card is not None:
            actions = Actions([
                Action([Action.Description(card.pos, Face.UP)])
            ])
            return actions

    # Fallback : best max stat in hand
    card, _ = first_card_with_best_max_base_stat_in(ai_player.hand, look_facedown_cards=True)
    if card is not None:
        actions = Actions([
            Action([Action.Description(card.pos, Face.DOWN)])
        ])
        return actions

    # Fallback² : no monsters
    one_fifth = (1, 5)
    actions = Actions()
    for card in ai_player.hand[:5]:
        # card = ai_player['hand'][pos]
        # _type = utils.get_card_type_from_id(cur, card['id'])

        if card.type == Type.EQUIP:
            sub_combo_equip = lbl_set_magic_equip(
                card.pos, ai_player.backrow, ai_player.frontrow, card.id
            )
            if len(sub_combo_equip) == 1:
                action = sub_combo_equip.actions[0]
                action.odds = one_fifth
                actions.append(action)
            else:
                # actions.append(Action(sub_combo, odds=odds))
                actions.append_horizontally(sub_combo_equip.actions)

        elif card.type == Type.TRAP:
            sub_combo_trap = lbl_set_magic_trap(card.pos, ai_player.backrow)
            if len(sub_combo_trap) == 1:
                action = sub_combo_trap.actions[0]
                action.odds = one_fifth
                actions.append(action)
            else:
                # actions.append(Action(sub_combo, odds=one_fifth))
                actions.append_horizontally(sub_combo_trap.actions)
        elif card.type in {Type.RITUAL, Type.MAGIC}:
            sub_combo_ritual_magic = lbl_set_magic_ritual_magic(card.pos, ai_player.backrow)
            sub_combo_ritual_magic.odds = one_fifth
            # actions.append(sub_combo)
            actions.append(sub_combo_ritual_magic)  # This is always a single action
        else:
            raise ValueError('Fallback should only have non monster cards in hand.')

    return actions


def lbl_improve_monster(cursor: Cursor, ai_player: Opponent, field: Field) \
        -> Actions | None:
    """ Returns actions to improve a monster. """

    improve = improve_monster_from_ai_board_and_hand(
        cursor, ai_player.hand, field,
        monster_board=ai_player.frontrow,
        max_improve_length=get_ai_stats(ai_player.name).max_improve_length
    )

    if improve is None:
        return lbl_find_best_combo(cursor, ai_player, field)

    return None


EARLIEST_TURN_MAGIC_FROM_HAND = 4


def hand_ai(cursor: Cursor, player: Opponent, ai_player: Opponent, field: Field) \
        -> Actions:
    """ Returns the actions the AI can play from the hand.
    Each action can have a certain probability to be triggered. """

    actions: Actions = Actions()
    always_look_facedown_cards = get_ai_stats(ai_player.name).attack_percent == AIStat.SEE_THROUGH

    # 1. Direct kill
    for spell_name, dmg in direct_damages.items():
        if (card := get_first_card_in(spell_name, ai_player.hand)) is not None \
                and is_empty(player.backrow) \
                and dmg >= player.lp:
            actions = Actions([
                Action([Action.Description(card.pos, Face.UP)])
            ])
            return actions

    # 2. Forced field
    # ai_field_name = None  # Prevents a PyCharm strong warning
    if (ai_name := ai_player.name) in mage_fields \
            and (ai_field_name := mage_fields[ai_name]) is not None \
            and (field is None or field != ai_field_name) \
            and (card := get_first_card_in(ai_field_name, ai_player.hand)) is not None:
        actions = Actions([
            Action([Action.Description(card.pos, Face.UP)])
        ])
        return actions

    # 3a. The AI lacks field control
    if ai_thinks_it_lacks_field_control(
            player.frontrow, ai_player.frontrow, look_facedown_cards=always_look_facedown_cards
    ):
        card_base_max_stat_in_ai_hand, stat_base_max_stat_in_ai_hand \
            = first_card_with_best_max_base_stat_in(ai_player.hand, look_facedown_cards=True)

        card_best_visible_player, stat_best_visible_player_true_max_stat \
            = first_card_with_best_true_max_stat_in(player.frontrow, look_facedown_cards=always_look_facedown_cards)

        # 3a1. Regain control with a single monster
        if card_base_max_stat_in_ai_hand is not None:
            if is_empty(ai_player.frontrow):
                actions = Actions([
                    Action([Action.Description(card_base_max_stat_in_ai_hand.pos, Face.DOWN)])
                ])
                return actions

            if stat_base_max_stat_in_ai_hand >= stat_best_visible_player_true_max_stat:
                actions = Actions([
                    Action([Action.Description(card_base_max_stat_in_ai_hand.pos, Face.DOWN)])
                ])
                return actions

        # 3a2. Regain control with magic/trap
        # ai_player['hand'] - 5 + ai_player['remaining_deck'] <= 32:
        if ai_player.current_turn >= EARLIEST_TURN_MAGIC_FROM_HAND:
            # best_player_type = utils.get_card_type_from_id(cur, player['frontrow'][pos_best_visible_player]['id'])
            best_player_type = player.frontrow[card_best_visible_player.pos].type
            # Counter player type
            for type_, counter_magic_name in type_counter_magics.items():
                if type_ == best_player_type:
                    card = get_first_card_in(counter_magic_name, ai_player.hand)
                    if card is not None:
                        actions = Actions([
                            Action([Action.Description(card.pos, Face.UP)])
                        ])
                        return actions

            # Decrease stats
            card = get_first_card_in('Spellbinding Circle', ai_player.hand)
            if card is not None:
                actions = Actions([
                    Action([Action.Description(card.pos, Face.UP)])
                ])
                return actions

            card = get_first_card_in('Shadow Spell', ai_player.hand)
            if card is not None:
                actions = Actions([
                    Action([Action.Description(card.pos, Face.UP)])
                ])
                return actions

            # Destroy monsters
            # stat_best_visible_player_base_max_stat_plus_field
            # = calculate_max_base_stat_plus_field(cur, player['frontrow'][pos_best_visible_player]['id'], field)
            stat_best_visible_player_base_max_stat_plus_field = card_best_visible_player.max_base_stat_plus_field
            if stat_best_visible_player_base_max_stat_plus_field >= CRUSH_CARD_MIN_ATTACK:
                card = get_first_card_in('Crush Card', ai_player.hand)
                if card is not None:
                    actions = Actions([
                        Action([Action.Description(card.pos, Face.UP)])
                    ])
                    return actions

            card = get_first_card_in('Raigeki', ai_player.hand)
            if card is not None:
                actions = Actions([
                    Action([Action.Description(card.pos, Face.UP)])
                ])
                return actions

            # Traps
            for trap_name in traps_list_descending:
                card = get_first_card_in(trap_name, ai_player.hand)
                if card is not None:
                    actions = Actions([
                        Action([Action.Description(card.pos, Face.DOWN)])
                    ])
                    return actions

            # Swords of Revealing Light
            if player.remaining_turns_under_swords == 0:
                card = get_first_card_in('Swords of Revealing Light', ai_player.hand)
                if card is not None:
                    actions = Actions([
                        Action([Action.Description(card.pos, Face.UP)])
                    ])
                    return actions

            # Dark Hole
            if len(list(filter(None, player.frontrow))) > len(list(filter(None, ai_player.frontrow))):
                card = get_first_card_in('Dark Hole', ai_player.hand)
                if card is not None:
                    actions = Actions([
                        Action([Action.Description(card.pos, Face.UP)])
                    ])
                    return actions

        # 3a3. Regain control with a combo
        return lbl_find_best_combo(cursor, ai_player, field)

    # 3b. The AI thinks it has field control

    # 3b1. Clear player's backrow
    next_action_list = actions
    non_harpie_action = None
    if (any(player.backrow)
            and (card := get_first_card_in("Harpie's Feather Duster", ai_player.hand))
            is not None):
        harpie_odds = Odds((get_ai_stats(ai_player.name).spell_percent, 100))
        harpie_action = Action([Action.Description(card.pos, Face.UP)], odds=harpie_odds)
        non_harpie_action = Action(odds=harpie_odds.complementary())
        actions.append_horizontally([
            harpie_action,
            non_harpie_action
        ])
        next_action_list = non_harpie_action.next

    # 3b2. Improve monster if low enough LP
    if ai_player.lp <= get_ai_stats(ai_player.name).low_lp_threshold:
        improve = lbl_improve_monster(cursor, ai_player, field)

        next_action_list.append_horizontally(
            improve.actions,
            level=non_harpie_action.level + 1
            if non_harpie_action is not None
            else Action.BASE_LEVEL
        )

        return actions

    # Choose randomly between IMPROVE_MONSTER, FIND_BEST_COMBO and SET_MAGIC
    domination_mode = 'total_domination' \
        if ai_has_total_domination(player.frontrow, ai_player.frontrow,
                                   look_facedown_cards=always_look_facedown_cards) \
        else 'lacks_total_domination'  # TODO how to avoid string literal

    best_combo_odds = get_ai_stats(ai_player.name).__getattribute__(domination_mode).find_best_combo, 100
    best_combo_action = Action(odds=best_combo_odds, next_=lbl_find_best_combo(cursor, ai_player, field).actions)

    improve_odds = get_ai_stats(ai_player.name).__getattribute__(domination_mode).improve_monster, 100
    improve_action = Action(odds=improve_odds, next_=lbl_improve_monster(cursor, ai_player, field).actions)

    set_magic_odds = get_ai_stats(ai_player.name).__getattribute__(domination_mode).set_magic, 100
    set_magic_action = Action(odds=set_magic_odds, next_=lbl_set_magic(ai_player).actions)

    domination_actions = [best_combo_action, improve_action, set_magic_action]

    next_action_list.append_horizontally(
        domination_actions,
        level=non_harpie_action.level + 1
        if non_harpie_action is not None
        else Action.BASE_LEVEL
    )

    return actions


if __name__ == '__main__':
    conn, curs = db.connect_to_YFM_database()

    # Code here

    # End code
    con.close()
