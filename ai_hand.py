from ai import *
from probability_tree import *

import db
import utils

# Card ids
ID, NAME, STAR1, STAR2, TYPE, ATTACK, DEFENSE = 0, 1, 3, 4, 6, 8, 9

MIN_ID, MAX_ID = 1, 722
MEGAMORPH_ID = 657


def validate_card_id(_id: Id) -> None:
    if not MIN_ID <= _id <= MAX_ID:
        raise ValueError(f"IDs must be between '{MIN_ID}' and '{MAX_ID}', received '{_id}'.")


class Combo:
    """ Represents a combo the AI can play. """

    def __init__(self, ordering: list[Position] = None, ids: list[Id] = None,
                 result_id: Id = None, equip_stage: EquipStage = 0, result_max_stat: Stat = 0) -> None:
        self.ordering = []
        if ordering is not None:
            for order in ordering:
                self.ordering.append(order)

        self.ids = []
        if ids is not None:
            for _id in ids:
                validate_card_id(_id)
                self.ids.append(_id)

        if result_id is not None:
            validate_card_id(result_id)
        self._result_id = result_id

        self.equip_stage = equip_stage
        self.result_max_stat = result_max_stat

    @property
    def result_id(self) -> Id:
        return self._result_id

    @result_id.setter
    def result_id(self, _id: Id) -> None:
        validate_card_id(_id)
        self.result_id = _id

    def update(self, ordering: Position = None, _id: Id = None,
               result_id: Id = None, delta_equip_stage: EquipStage = 0, result_max_stat: Stat = 0) -> None:
        """ Updates the combo. Since AI can only play compatible equips, `delta_equip_stage == 0` implies the
        equip stage is reset to `0` instead of added to the previous equip stage. """
        if ordering is not None:
            self.ordering.append(ordering)

        if _id is not None:
            validate_card_id(_id)
            self.ids.append(_id)

        if result_id is not None:
            validate_card_id(result_id)
            self._result_id = result_id

        if delta_equip_stage is not None:
            if delta_equip_stage == 0:
                self.equip_stage = 0
            else:
                self.equip_stage += delta_equip_stage

        if result_max_stat is not None:
            self.result_max_stat = result_max_stat


# # Best combo attributes
# ORDERING = 'ordering'
# IDS = 'ids'
# RESULT_ID = 'result_id'
# EQUIP_STAGE = 'equip_stage'
# RESULT_MAX_STAT = 'result_max_stat'


def find_best_combo_in_ai_hand(cur: Cursor, hand: Cards,
                               board_card: Card = None, best_combo: Combo = None, max_fusion_length: int = 5,
                               field: Field = None, current_combo: Combo = None) -> Combo:
    """ (Assumes board positions are already encoded.)"""

    # Max length reached
    if max_fusion_length == 0:
        return best_combo

    board_id, board_pos, board_equip_level = (board_card['id'], board_card['pos'], board_card['equip_stage']) \
        if board_card is not None \
        else (None, None, 0)

    # Base case
    if current_combo is None:
        if board_card is None:
            current_combo = Combo()
        else:
            current_combo = Combo(ordering=[board_pos], ids=[board_id], result_id=board_id,
                                  equip_stage=board_equip_level,
                                  result_max_stat=calculate_true_max_stat(cur, board_id, field, board_equip_level))

    if best_combo is None:
        best_combo = deepcopy(current_combo)

    for pos, card in enumerate(hand):
        # Skip card if same slot in hand than the one on the board
        if board_pos is not None and board_pos == pos:
            continue

        # Skip cards already in the current combo
        if pos in current_combo.ordering:
            continue

        old_combo = deepcopy(current_combo)

        # Initialise with a card from the hand
        if current_combo.result_id is None:
            current_combo.update(ordering=pos, _id=card['id'], result_id=card['id'],
                                 result_max_stat=calculate_max_base_stat(cur, board_id))

        # Continue previous combo with cards from the hand
        else:
            # Check if we're equipping a compatible item or performing a valid fusion
            equipped_equip = cur.execute(
                f"SELECT EquippedID, EquipID FROM Equipping "
                f"WHERE EquippedID = {current_combo.result_id} AND EquipID = {card['id']} "
                f"OR    EquippedID = {card['id']} AND EquipID = {current_combo.result_id}"
            ).fetchone()
            fusion = cur.execute(
                f"SELECT Result FROM Fusions "
                f"WHERE Material1 = {current_combo.result_id} AND Material2 = {card['id']}"
            ).fetchone()
            result_id = equipped_equip[0] if equipped_equip is not None \
                else int(fusion[0]) if fusion is not None \
                else None

            # Non-compatible equip / fusion
            if result_id is None:
                continue

            current_combo.update(
                ordering=pos, _id=card['id'], result_id=result_id,
                result_max_stat=calculate_max_base_stat_plus_field(cur, result_id, field),
                delta_equip_stage=
                0 if equipped_equip is None else
                2 if equipped_equip[1] == MEGAMORPH_ID else
                1
            )

        # Update best combo
        b, c = best_combo.result_max_stat, current_combo.result_max_stat
        lb, lc = len(best_combo.ordering), len(current_combo.ordering)
        if b < c \
                or b == c and \
                (min(lb, lc) == 1 and max(lb, lc) > 1 and min(best_combo.ordering) > min(current_combo.ordering)
                 or min(lb, lc) > 1 and max(lb, lc) > 1 and lb > lc):
            best_combo = deepcopy(current_combo)

        best_combo = find_best_combo_in_ai_hand(
            cur, hand,
            board_card=board_card, best_combo=best_combo, max_fusion_length=max_fusion_length - 1, field=field,
            current_combo=current_combo
        )

        current_combo = old_combo

    return best_combo


def find_best_combo_in_ai_board_and_hand(cur: Cursor, hand: Cards,
                                         monster_board: Cards = None, max_fusion_length: int = 5,
                                         field: Field = None) -> Combo:
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


def improve_monster_from_ai_hand(cur: Cursor, hand: Cards, board_card: Card,
                                 best_combo: Combo = None, max_improve_length: int = 4, field: Field = None,
                                 current_combo: Combo = None) -> Combo:
    # Max length reached
    if max_improve_length == 0:
        return best_combo

    board_id, board_pos, board_equip_level = (board_card['id'], board_card['pos'], board_card['equip_stage']) \
        if board_card is not None \
        else (None, None, 0)

    # Base case
    if current_combo is None:
        current_combo = Combo(
            ordering=[board_pos], ids=[board_id], result_id=board_id, equip_stage=board_equip_level,
            result_max_stat=calculate_max_base_stat_plus_field(cur, board_id, field)
        )

    if best_combo is None:
        best_combo = deepcopy(current_combo)

    for pos, card in enumerate(hand):
        # Skip cards already in the current combo
        if pos in current_combo.ordering:
            continue

        old_combo = deepcopy(current_combo)

        # Check if we're equipping a compatible item or performing a valid fusion
        equipped_equip = cur.execute(
            f"SELECT EquippedID, EquipID FROM Equipping "
            f"WHERE EquippedID = {current_combo.result_id} AND EquipID = {card['id']} "
            f"      OR EquippedID = {card['id']} AND EquipID = {current_combo.result_id}"
        ).fetchone()
        fusion = cur.execute(
            f"SELECT Result FROM Fusions "
            f"WHERE Material1 = {current_combo.result_id} AND Material2 = {card['id']}"
        ).fetchone()
        result_id = equipped_equip[0] if equipped_equip is not None \
            else int(fusion[0]) if fusion is not None \
            else None

        # Non-compatible equip / fusion
        if result_id is None:
            continue

        current_combo.update(
            ordering=pos, _id=card['id'], result_id=result_id,
            result_max_stat=calculate_max_base_stat_plus_field(cur, result_id, field),
            delta_equip_stage=0 if equipped_equip is None
            else 2 if equipped_equip[1] == MEGAMORPH_ID
            else 1)

        # Update best combo
        b, c = best_combo.result_max_stat, current_combo.result_max_stat
        lb, lc = len(best_combo.ordering), len(current_combo.ordering)
        if b < c or b == c and lb > lc:
            best_combo = deepcopy(current_combo)

        best_combo = improve_monster_from_ai_hand(
            cur, hand,
            board_card=board_card, best_combo=best_combo, max_improve_length=max_improve_length - 1,
            field=field, current_combo=current_combo
        )

        current_combo = old_combo

    return best_combo


def improve_monster_from_ai_board_and_hand(cur: Cursor, hand: Cards, monster_board: Card = None,
                                           max_improve_length: int = 4, field: Field = None) -> Optional[Action]:
    """Returns a converted list of actions. Returns `None` if no improvement is found."""

    combo = None

    if monster_board is None:
        return combo

    # Iterate from lowest *true* max stat to highest (earlier cards are looked at first in case of a tie).
    ordered_monster_board = sorted(
        list(filter(lambda x: x is not None, monster_board)),
        key=lambda x: ascending_true_max_stat_sorting_key(cur, x, field)
    )

    for board_card in ordered_monster_board:
        combo = improve_monster_from_ai_hand(
            cur, hand,
            board_card=board_card, best_combo=combo, max_improve_length=max_improve_length,
            field=field, current_combo=None
        )
        if combo.result_id == board_card['id'] \
                and combo.equip_stage == board_card['equip_stage'] \
                and combo.result_max_stat <= calculate_max_base_stat_plus_field(cur, board_card['id'], field):
            combo = None

        if combo is not None:
            return convert_best_combo(cur, combo)

    return None


traps_list_descending: list[str] = [
    'Widespread Ruin',
    'Acid Trap Hole',
    'Invisible Wire',
    'Bear Trap',
    'Eatgaboon',
    'House of Adhesive Tape',
    'Fake Trap'
]

support_type_with_field: dict[Type, list[Field]] = {
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


def best_combo_consists_of_only_cards_from_the_hand(best_combo: Combo) -> bool:
    """ Returns `True` if and only if all cards from the combo are from the hand. """

    return False if best_combo is None or len(best_combo.ordering) == 0 else \
        all((pos >= 0 for pos in best_combo.ordering))


def best_combo_consists_of_playing_on_top_of_a_card_on_the_field(best_combo: Combo) -> bool:
    """ Returns `True` if and only if the combo consists of playing on top of a card on the field. """

    return len(best_combo.ordering) >= 2 and best_combo.ordering[0] < 0


def convert_best_combo(cur: Cursor, best_combo: Combo) -> Optional[Action]:
    """ Converts the best combo into actions. Returns `None` if no combo is found. """

    if best_combo_consists_of_only_cards_from_the_hand(best_combo):
        return Action([(pos, FACE_UP) for pos in best_combo.ordering])

    # Bug : if monster + magic, then simply trigger the magic
    if best_combo_consists_of_playing_on_top_of_a_card_on_the_field(best_combo):
        if len(best_combo.ordering) == 2 and utils.is_magic(cur, best_combo.ids[1]):
            return Action([(best_combo.ordering[1], FACE_UP)])

        return Action([(pos, FACE_UP) for pos in best_combo.ordering])

    return None


def lbl_set_magic_ritual_magic(hand_pos: Position, ai_backrow: Cards) -> Action:
    """ Returns an action involving a Magic/Ritual. """

    if all(ai_backrow):
        action = Action([(hand_pos, FACE_UP)])
    else:
        action = Action([(hand_pos, FACE_DOWN)])
    return action


def lbl_set_magic_trap(hand_pos: Position, ai_backrow: Cards) -> Actions:
    """ Returns an action involving a Trap. """

    if all(ai_backrow):
        actions = Actions([
            Action([(encode_backrow_pos(back_pos), FACE_UP), (hand_pos, FACE_UP)], odds=(1, 5))
            for back_pos in range(0, 5)
        ])
    else:
        actions = Actions([
            Action([(hand_pos, FACE_DOWN)])
        ])

    return actions


def lbl_set_magic_equip(hand_pos: Position, ai_backrow: Cards, ai_frontrow: Cards, equip_id: Id, field: Field) \
        -> Actions:
    """ Returns actions involving an Equip. """

    # Backrow is full
    if all(ai_backrow):
        # Find the first compatible monster
        monster_pos = get_first_monster_compatible_in(cur, equip_id, ai_frontrow)
        if monster_pos is not None:
            actions = [
                Action([(monster_pos, FACE_UP), (hand_pos, FACE_UP)])
            ]
        # No compatible monster
        else:
            # Play over weakest monster
            if any(ai_frontrow):
                monster_pos, _ \
                    = get_first_pos_of_lowest_true_max_stat_in(cur, ai_frontrow, field, True)
                actions = [
                    Action([(monster_pos, FACE_UP), (hand_pos, FACE_UP)])
                ]
            # Play over random backrow slot
            else:
                actions = [
                    Action([(encode_backrow_pos(back_pos), FACE_UP), (hand_pos, FACE_UP)], odds=(1, 5))
                    for back_pos in range(0, 5)
                ]
    # Backrow is not full
    else:
        actions = [
            Action([(hand_pos, FACE_DOWN)])
        ]

    return Actions(actions)


def lbl_set_magic(cur: Cursor, ai_player: Opponent, field: Field) -> Actions:
    """ Returns actions corresponding to the LBL_SET_MAGIC routine. """

    # Trap
    hand_pos = get_first_pos_of_type_in(cur, 'Trap', ai_player['hand'])
    if hand_pos is not None:
        actions = lbl_set_magic_trap(hand_pos, ai_player['backrow'])
        return actions

    # Equip
    hand_pos = get_first_pos_of_type_in(cur, 'Equip', ai_player['hand'])
    if hand_pos is not None:
        actions = lbl_set_magic_equip(
            hand_pos, ai_player['backrow'], ai_player['frontrow'], ai_player['hand'][hand_pos], field
        )
        return actions

    # Magic
    hand_pos = get_first_pos_of_type_in(cur, 'Magic', ai_player['hand'])
    if hand_pos is not None:
        action = lbl_set_magic_ritual_magic(hand_pos, ai_player['backrow'])
        return Actions([action])

    # Ritual
    hand_pos = get_first_pos_of_type_in(cur, 'Ritual', ai_player['hand'])
    if hand_pos is not None:
        action = lbl_set_magic_ritual_magic(hand_pos, ai_player['backrow'])
        return Actions([action])

    # Only monsters
    hand_pos = get_first_pos_of_base_max_stat_in(cur, ai_player['hand'], True)
    actions = Actions([
        Action([(hand_pos, FACE_DOWN)])
    ])
    return actions


def lbl_find_best_combo(cur: Cursor, ai_player: Opponent, field: Field) -> Actions:
    """ Returns a converted list of actions. """

    best_combo = find_best_combo_in_ai_board_and_hand(
        cur, ai_player['hand'],
        monster_board=ai_player['frontrow'], max_fusion_length=get_ai_stats(ai_player['name']).max_fusion_length,
        field=field
    )

    actions = convert_best_combo(cur, best_combo)
    if actions is not None:
        return Actions([actions])

    # No combo play -> set magic
    if best_combo.result_max_stat == 0:
        actions = lbl_set_magic(cur, ai_player, field)
        return actions

    # Doing nothing to a monster from the board -> compatible field
    best_type = utils.get_card_type_from_id(cur, best_combo.ids[0])
    for support_field in support_type_with_field.get(best_type, []):
        # This skips the second field if there is a second one
        if field is not None and field == support_field:
            break

        pos = get_first_pos_in(cur, support_field, ai_player['hand'])
        if pos is not None:
            actions = Actions([
                Action([(pos, FACE_UP)])
            ])
            return actions

    # Fallback : best max stat in hand
    pos, _ = get_first_pos_of_base_max_stat_in(cur, ai_player['hand'], True)
    if pos is not None:
        actions = Actions([
            Action([(pos, FACE_DOWN)])
        ])
        return actions

    # Fallback² : no monsters
    odds = (1, 5)
    actions = Actions()
    # TODO : use the append_horizontally method to exploit the tree structure
    for pos in range(5):
        card = ai_player['hand'][pos]
        _type = utils.get_card_type_from_id(cur, card['id'])

        if _type == 'Equip':
            sub_combo = lbl_set_magic_equip(
                pos, ai_player['backrow'], ai_player['frontrow'], ai_player['hand'][pos]['id'], field
            )
            if len(sub_combo) == 1:
                action = sub_combo.actions[0]
                action.odds = odds
                actions.append(action)
            else:
                actions.append(Action(sub_combo, odds=odds))
        elif _type == 'Trap':
            sub_combo = lbl_set_magic_trap(pos, ai_player['backrow'])
            if len(sub_combo) == 1:
                action = sub_combo.actions[0]
                action.odds = odds
                actions.append(action)
            else:
                actions.append(Action(sub_combo, odds=odds))
        else:
            sub_combo = lbl_set_magic_ritual_magic(pos, ai_player['backrow'])
            sub_combo.odds = odds
            actions.append(sub_combo)


    return actions


def lbl_improve_monster(cur: Cursor, ai_player: Opponent, field: Field) -> Actions:
    """ Returns actions to improve a monster. """

    improve = improve_monster_from_ai_board_and_hand(
        cur, ai_player['hand'], ai_player['frontrow'],
        max_improve_length=get_ai_stats(ai_player['name']).max_improve_length, field=field
    )

    if improve is None:
        return lbl_find_best_combo(cur, ai_player, field)


def hand_ai(cur: Cursor, player: Opponent, ai_player: Opponent, current_ai_turn: int, field: Field = None) -> Actions:
    """ Returns the actions the ai can play from the hand.
    Each action can have a certain probability to be triggered. """

    actions: Actions = Actions()
    always_look_facedown_cards = get_ai_stats(ai_player['name']).attack_percent == AIStat.SEE_THROUGH

    # 1. Direct kill
    for spell_name, dmg in direct_damages.items():
        if (pos := get_first_pos_in(cur, spell_name, ai_player['hand'])) is not None \
                and is_empty(player['backrow']) \
                and dmg >= player['LP']:
            actions = Actions([
                Action([(pos, FACE_UP)])
            ])
            return actions

    # 2. Forced field
    ai_field_name = None  # Prevents a PyCharm strong warning
    if (ai_name := ai_player['name']) in mage_fields \
        and (ai_field_name := mage_fields[ai_name]) is not None \
        and (field is None or field != ai_field_name) \
        and (pos := get_first_pos_in(cur, ai_field_name, ai_player['hand'])) is not None:
        actions = Actions([
            Action([(pos, FACE_UP)])
        ])
        return actions

    # 3a. The AI lacks field control
    if ai_thinks_it_lacks_field_control(
            cur, player['frontrow'], ai_player['frontrow'], field, always_look_facedown_cards
    ):
        pos_base_max_stat_in_ai_hand, stat_base_max_stat_in_ai_hand \
            = get_first_pos_of_base_max_stat_in(cur, ai_player['hand'], True)

        pos_best_visible_player, stat_best_visible_player_true_max_stat \
            = get_first_pos_of_true_max_stat_in(cur, player['frontrow'], field, always_look_facedown_cards)

        # 3a1. Regain control with a single monster
        if pos_base_max_stat_in_ai_hand is not None:
            if is_empty(ai_player['frontrow']):
                actions = Actions([
                    Action([(pos_base_max_stat_in_ai_hand, FACE_DOWN)])
                ])
                return actions

            if stat_base_max_stat_in_ai_hand >= stat_best_visible_player_true_max_stat:
                actions = Actions([
                    Action([(pos_base_max_stat_in_ai_hand, FACE_DOWN)])
                ])
                return actions

        # 3a2. Regain control with magic/trap
        if current_ai_turn >= 4:  # ai_player['hand'] - 5 + ai_player['remaining_deck'] <= 32:
            best_player_type = utils.get_card_type_from_id(cur, player['frontrow'][pos_best_visible_player]['id'])

            # Counter player type
            for _type, counter_magic_name in type_counter_magics.items():
                if _type == best_player_type:
                    pos = get_first_pos_in(cur, counter_magic_name, ai_player['hand'])
                    if pos is not None:
                        actions = Actions([
                            Action([(pos, FACE_UP)])
                        ])
                        return actions

            # Decrease stats
            pos = get_first_pos_in(cur, 'Spellbinding Circle', ai_player['hand'])
            if pos is not None:
                actions = Actions([
                    Action([(pos, FACE_UP)])
                ])
                return actions

            pos = get_first_pos_in(cur, 'Shadow Spell', ai_player['hand'])
            if pos is not None:
                actions = Actions([
                    Action([(pos, FACE_UP)])
                ])
                return actions

            # Destroy monsters
            stat_best_visible_player_base_max_stat_plus_field \
                = calculate_max_base_stat_plus_field(cur, player['frontrow'][pos_best_visible_player]['id'], field)
            if stat_best_visible_player_base_max_stat_plus_field >= 1_500:
                pos = get_first_pos_in(cur, 'Crush Card', ai_player['hand'])
                if pos is not None:
                    actions = Actions([
                        Action([(pos, FACE_UP)])
                    ])
                    return actions

            pos = get_first_pos_in(cur, 'Raigeki', ai_player['hand'])
            if pos is not None:
                actions = Actions([
                    Action([(pos, FACE_UP)])
                ])
                return actions

            # Traps
            for trap_name in traps_list_descending:
                pos = get_first_pos_in(cur, trap_name, ai_player['hand'])
                if pos is not None:
                    actions = Actions([
                        Action([(pos, FACE_DOWN)])
                    ])
                    return actions

            # Swords of Revealing Light
            if player.get('remaining_turns_under_swords', 0) == 0:
                pos = get_first_pos_in(cur, 'Swords of Revealing Light', ai_player['hand'])
                if pos is not None:
                    actions = Actions([
                        Action([(pos, FACE_UP)])
                    ])
                    return actions

            # Dark Hole
            if len(list(filter(None, player['frontrow']))) > len(list(filter(None, ai_player['frontrow']))):
                pos = get_first_pos_in(cur, 'Dark Hole', ai_player['hand'])
                if pos is not None:
                    actions = Actions([
                        Action([(pos, FACE_UP)])
                    ])
                    return actions

        # 3a3. Regain control with a combo
        return lbl_find_best_combo(cur, ai_player, field)

    # 3b. The AI thinks it has field control

    # 3b1. Clear player's backrow
    next_action_list = actions
    non_harpie_action = None
    if any(player['backrow'])\
            and (pos := get_first_pos_in(cur, "Harpie's Feather Duster", ai_player['hand'])) is not None:
        harpie_odds = Odds((get_ai_stats(ai_player['name']).spell_percent, 100))
        harpie_action = Action([(pos, FACE_UP)], odds=harpie_odds)
        non_harpie_action = Action(odds=harpie_odds.complementary())
        actions.append_horizontally([
            harpie_action,
            non_harpie_action
        ])
        next_action_list = non_harpie_action.next

    # 3b2. Improve monster if low enough LP
    if ai_player['LP'] <= get_ai_stats(ai_player['name']).low_lp_threshold:
        improve = lbl_improve_monster(cur, ai_player, field)

        next_action_list.append_horizontally(improve.actions, level=non_harpie_action.level+1 if non_harpie_action is not None else Action.BASE_LEVEL)

        return actions

    # Choose randomly between IMPROVE_MONSTER, FIND_BEST_COMBO and SET_MAGIC
    domination_mode = 'total_domination' \
        if ai_has_total_domination(cur, player['frontrow'], ai_player['frontrow'], field, always_look_facedown_cards) \
        else 'lacks_total_domination'

    best_combo_odds = get_ai_stats(ai_player['name']).__getattribute__(domination_mode).find_best_combo, 100
    best_combo_action = Action(odds=best_combo_odds, _next=lbl_find_best_combo(cur, ai_player, field).actions)

    improve_odds = get_ai_stats(ai_player['name']).__getattribute__(domination_mode).improve_monster, 100
    improve_action = Action(odds=improve_odds, _next=lbl_improve_monster(cur, ai_player, field).actions)

    set_magic_odds = get_ai_stats(ai_player['name']).__getattribute__(domination_mode).set_magic, 100
    set_magic_action = Action(odds=set_magic_odds, _next=lbl_set_magic(cur, ai_player, field).actions)

    domination_actions = [best_combo_action, improve_action, set_magic_action]

    next_action_list.append_horizontally(domination_actions, level=non_harpie_action.level+1 if non_harpie_action is not None else Action.BASE_LEVEL)

    return actions


if __name__ == '__main__':
    con, cur = db.connect_to_YFM_database()

    # Code here

    # End code
    con.close()
