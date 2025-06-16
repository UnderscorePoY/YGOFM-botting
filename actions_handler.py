import random
from sqlite3 import Cursor

import ai
import utils
from probability_tree import Actions, Action
from types_ import Card, Field, Type, is_monster, Id, Opponent, BattleMode, Face, Position, IsActive, EndOfTurnType, \
    EndOfTurn


def combine(cur: Cursor, card1: Card, card2: Card, field: Field) -> tuple[Card, bool]:
    """
    Returns the result card of the combination of `card1` and `card2`, and whether it failed.
    Knowing whether the fusion failed is useful for handling the Reverse Trap bug.
    """

    type1 = card1.type  # utils.get_card_type_from_id(cur, card1['id'])
    type2 = card2.type  # utils.get_card_type_from_id(cur, card2['id'])

    # Fusion
    fusion = cur.execute(
        f"SELECT Result FROM Fusions "
        f"WHERE Material1 = ? AND Material2 = ?",
        (card1.id, card2.id)
    ).fetchone()

    if fusion is not None:
        result_id, = fusion
        result_id = Id(int(result_id))
        # return create_new_card(cur, result_id), False
        card, is_failed_fusion = Card(cur, result_id, field, face=Face.UP), False
        return card, is_failed_fusion

    # Equip
    equipped, equip = card1, card2
    if is_monster(type1) and type2 == Type.EQUIP:
        equipped, equip = card2, card1

    equipped_equip = cur.execute(
        f"SELECT EquippedID, EquipID FROM Equipping "
        f"WHERE EquippedID = ? AND EquipID = ?",
        (equipped.id, equip.id)
    ).fetchone()

    if equipped_equip is not None:
        equipped.equip_stage += (2 if equip.id == Id.MEGAMORPH else 1)
        # return equipped, False
        card, is_failed_fusion = equipped, False
        return card, is_failed_fusion

    # Failed combined
    if is_monster(card1.type) and not is_monster(card2.type):
        # return card1, False
        card1.face = Face.UP
        card, is_failed_fusion = card1, True
        return card, is_failed_fusion

    # return card2, (card1 in monster_types and card2 in monster_types)
    card2.face = Face.UP
    card, is_failed_fusion = card2, (is_monster(card1.type) and is_monster(card2.type))
    return card, is_failed_fusion


def try_ritual(cur: Cursor, ritual_id: Id, source_opp: Opponent, field: Field):  # -> None
    ritual_info = utils.check_ritual(cur, ritual_id, source_opp.frontrow)
    if ritual_info.is_successful:
        sacrifices_positions: list[Position] = []
        for card in filter(None, source_opp.frontrow):
            if card.id in ritual_info.sacrifices:
                sacrifices_positions.append(card.pos)
                ritual_info.sacrifices.remove(card.id)
                source_opp.frontrow[card.pos] = None
            if len(ritual_info.sacrifices) == 0:
                break
        _, summon_pos, _ = sorted(sacrifices_positions)

        source_opp.frontrow[summon_pos] = Card(
            cur, ritual_info.result_id, field,
            pos=summon_pos,
            face=Face.UP,
            battle_mode=BattleMode.ATTACK,
            is_active=True
        )


def play_magic(card_name: str, source_opp: Opponent, target_opp: Opponent) -> Field | None:
    """
    Applies the effects of `card_name` onto both players.
    Returns the new field, or `None` if no change to the field should be made.
    """

    if card_name == 'Stop Defense':
        for card in filter(None, target_opp.frontrow):
            card.battle_mode = BattleMode.ATTACK

    elif card_name in ai.magics_type_counter:
        for card in filter(None, target_opp.frontrow):
            destroyed_type = ai.magics_type_counter[card_name]
            if card.type == destroyed_type:
                target_opp.frontrow[card.pos] = None

    elif (field_ := Field.by_name(card_name)) is not None:
        for row in [source_opp.frontrow, target_opp.frontrow]:
            for card in filter(None, row):
                card.field = field_
        return field_

    elif card_name == 'Dark Hole':
        for row in [source_opp.frontrow, source_opp.backrow, target_opp.frontrow, target_opp.backrow]:
            for card in filter(None, row):
                row[card.pos] = None

    elif card_name == 'Raigeki':
        for card in filter(None, target_opp.frontrow):
            target_opp.frontrow[card.pos] = None

    elif card_name in ai.direct_heals:
        heal = ai.direct_heals[card_name]
        if (card := utils.get_last_card_in('Bad Reaction to Simochi', target_opp.backrow)) \
                is not None:
            source_opp.lp = source_opp.lp - heal  # max(source_opp.lp - heal, Opponent.MIN_LP)
            target_opp.backrow[card.pos] = None
        else:
            source_opp.lp = source_opp.lp + heal  # min(source_opp.lp + heal, Opponent.MAX_LP)

    elif card_name in ai.direct_damages:
        damage = ai.direct_damages[card_name]
        if (card := utils.get_last_card_in('Goblin Fan', target_opp.backrow)) \
                is not None:
            source_opp.lp = source_opp.lp - damage  # max(source_opp.lp - damage, Opponent.MIN_LP)
            target_opp.backrow[card.pos] = None
        else:
            target_opp.lp = target_opp.lp - damage  # max(target_opp.lp - damage, Opponent.MIN_LP)

    elif card_name == 'Swords of Revealing Light':
        target_opp.remaining_turns_under_swords = Opponent.MAX_REMAINING_TURNS_UNDER_SWORDS
        for card in filter(None, target_opp.frontrow):
            card.face = Face.UP

    elif card_name == 'Spellbinding Circle':
        for card in filter(None, target_opp.frontrow):
            card.equip_stage -= 1

    elif card_name == 'Dark-piercing Light':
        for card in filter(None, target_opp.frontrow):
            card.face = Face.UP

    elif card_name == 'Cursebreaker':
        for card in filter(None, source_opp.frontrow):
            card.equip_stage = max(0, card.equip_stage)

    elif card_name == 'Crush Card':
        for card in filter(None, target_opp.frontrow):
            if card.true_attack >= ai.CRUSH_CARD_MIN_ATTACK:
                target_opp.frontrow[card.pos] = None

    elif card_name == 'Shadow Spell':
        for card in filter(None, target_opp.frontrow):
            card.equip_stage -= 2

    elif card_name == "Harpie's Feather Duster":
        for card in filter(None, target_opp.backrow):
            target_opp.backrow[card.pos] = None

    else:
        raise RuntimeError(f"Magic {card_name} can't be played.")

    return None


def play_from_hand(cur: Cursor, actions: Actions, *, source_opp: Opponent, target_opp: Opponent, field: Field)\
        -> Field | None:
    """
    Modifies the board according to the `actions`.
    Returns the new field, or `None` if no field update should be done.
    """

    next_: Actions = actions
    descriptions: list[Action.Description] = []

    while next_ is not None and len(next_) > 0:
        chosen_action = actions.actions[0]

        # Random is involved: choose an action
        if len(next_) > 1:
            sum_num = 0.0
            target_opp = random.randrange(chosen_action.odds.denom)  # TODO: implement LCRNG from YGOFM
            for act in actions:
                sum_num += act.odds.num * chosen_action.odds.denom / act.odds.denom
                if sum_num >= target_opp:
                    chosen_action = act

        next_ = chosen_action.next

        descriptions.extend(chosen_action.descriptions)

    bugged_reverse_trap_equip_stage, reverse_trap_equip_stage_current_streak = 0, 0

    desc1 = descriptions[0]
    final_pos: Position | None = None

    if desc1.source.mode == Position.Mode.HAND:
        row = source_opp.hand
    elif desc1.source.mode == Position.Mode.FRONTROW:
        row = source_opp.frontrow
    elif desc1.source.mode == Position.Mode.BACKROW:
        row = source_opp.backrow
    else:
        raise ValueError(f'Invalid card position {desc1.source}.')

    new_card: Card = row[desc1.source]
    new_card.face = desc1.action

    for desc2 in descriptions[1:]:
        old_id, old_equip_stage = new_card.id, new_card.equip_stage

        if desc2.source.mode == Position.Mode.HAND:
            row = source_opp.hand
        elif desc2.source.mode == Position.Mode.FRONTROW:
            row = source_opp.frontrow
        elif desc2.source.mode == Position.Mode.BACKROW:
            row = source_opp.backrow
        else:
            raise ValueError(f'Invalid card position {desc2.source}.')
        second_card = row[desc2.source]

        new_card, is_failed_fusion = combine(cur, new_card, second_card, field)
        new_id, new_equip_stage = new_card.id, new_card.equip_stage
        new_card.face = Face.UP

        fusion_succeeded = (old_id != new_id and new_id != second_card.id)  # TODO: get it from combine ?
        equip_succeeded = (new_equip_stage > old_equip_stage)  # TODO: get it from combine ?
        if fusion_succeeded:
            bugged_reverse_trap_equip_stage = 0
            reverse_trap_equip_stage_current_streak = 0
        elif equip_succeeded:
            reverse_trap_equip_stage_current_streak += (new_equip_stage - old_equip_stage)
        elif is_failed_fusion:
            bugged_reverse_trap_equip_stage += 2 * reverse_trap_equip_stage_current_streak
            reverse_trap_equip_stage_current_streak = 0

    # Handle Reverse Trap + associated bug
    if (reverse_trap := utils.get_last_card_in('Reverse Trap', target_opp.backrow)) \
            is not None \
            and (bugged_reverse_trap_equip_stage > 0 or reverse_trap_equip_stage_current_streak > 0):
        new_card.equip_stage -= (bugged_reverse_trap_equip_stage + reverse_trap_equip_stage_current_streak)
        target_opp.backrow[reverse_trap.pos] = None

    # Get rid of cards in hand
    for desc in descriptions:
        source_opp.hand[desc.source] = None

    # Handles non-forced position
    if final_pos is None:
        if is_monster(new_card.type):
            for idx, card in enumerate(source_opp.frontrow):
                if card is None:
                    final_pos = Position(idx, Position.Mode.FRONTROW)

                    new_card.pos = final_pos
                    new_card.face = desc1.action
                    source_opp.frontrow[final_pos] = new_card
                    return None

            raise RuntimeError('Trying to place a Monster without a forced position on a full board.')

        elif new_card.type in {Type.EQUIP, Type.MAGIC, Type.RITUAL} and new_card.face == Face.DOWN \
                or new_card.type == Type.TRAP:
            for idx, card in enumerate(source_opp.backrow):
                if card is None:
                    final_pos = Position(idx, Position.Mode.BACKROW)

                    new_card.pos = final_pos
                    new_card.face = Face.DOWN
                    source_opp.backrow[final_pos] = new_card
                    return None
            else:
                raise RuntimeError(f"Trying to place a {repr(new_card.type)} {repr(new_card.face)} "
                                   f"without a forced position on a full board.")

    # Handles direct activations from the hand
    if final_pos is None:
        if not new_card.face == Face.UP:
            raise RuntimeError('At this point, played cards should only be face-up (directly activated).')

        if new_card.type == Type.RITUAL:
            try_ritual(cur, new_card.id, source_opp, field)
            return None

        elif new_card.type == Type.MAGIC:
            return play_magic(new_card.name, source_opp, target_opp)

    raise RuntimeError('Should never be reached.')


def play_from_board(cur: Cursor, actions: Actions, *, source_opp: Opponent, target_opp: Opponent, field: Field)\
        -> EndOfTurnType | Field | None:
    """
    Applies `actions` on opponents.
    Returns whether `actions` leads to the end of the turn, the new field if changed or `None` otherwise.
    """

    desc = actions.actions[0].descriptions[0]

    # End of turn
    if desc.action is EndOfTurn:
        return EndOfTurn

    # Darken
    if desc.action == IsActive.DARKEN:
        source_opp[desc.source].is_active = False

    # Put in defense
    elif desc.action == BattleMode.DEFENSE:
        source_opp[desc.source].battle_mode = BattleMode.DEFENSE
        source_opp[desc.source].is_active = False

    # Activate a non-equip
    elif desc.source.mode == Position.Mode.BACKROW and desc.action == Face.UP and desc.target is None:
        src = source_opp[desc.source]
        src_name, src_id, src_type = src.name, src.id, src.type

        source_opp[desc.source] = None
        if src_type == Type.MAGIC:
            new_field = play_magic(src_name, source_opp, target_opp)
            return new_field
        elif src_type == Type.RITUAL:
            try_ritual(cur, src_id, source_opp, field)
            return None
        # else no other effect

    # Activate an equip
    elif desc.source.mode == Position.Mode.BACKROW and desc.action == Face.UP and desc.target is not None:
        equipped, equip_id = source_opp[desc.target], source_opp[desc.source].id
        equipped.face = Face.UP
        source_opp[desc.source] = None

        equipped_equip = cur.execute(
            f"SELECT EquippedID, EquipID FROM Equipping "
            f"WHERE EquippedID = ? AND EquipID = ?",
            (equipped.id, equip_id)
        ).fetchone()

        if equipped_equip is not None:
            delta_stage = (2 if equip_id == Id.MEGAMORPH else 1)
            if (reverse_trap := utils.get_last_card_in('Reverse Trap', target_opp.backrow)) \
                    is not None:
                delta_stage = -delta_stage
                target_opp.backrow[reverse_trap.pos] = None
            equipped.equip_stage += delta_stage

    elif desc.action == BattleMode.ATTACK:
        source = source_opp[desc.source]
        # Forced attacker which doesn't attack
        if desc.target is None:
            source.battle_mode = BattleMode.ATTACK
            source.is_active = False
            return None

        # Source attacks a target
        target = target_opp[desc.target]
        # Direct attack
        if target is None:
            target_opp.lp -= source.true_attack
            source.is_active = False
            return None

        # Source monster vs. target monster
        source.face = Face.UP
        target.face = Face.UP
        source.is_active = False

        # source.star.has_advantage_over(target.star)
        source_true_atk_plus_star = (
                source.true_attack
                + 500 * source.star.has_advantage_over(target.star)
        )
        target_true_stat = target.true_attack if target.battle_mode == BattleMode.ATTACK else target.true_defense
        target_true_stat_plus_star = (
                target_true_stat
                + 500 * target.star.has_advantage_over(source.star)
        )

        delta_damage = source_true_atk_plus_star - target_true_stat_plus_star
        if delta_damage > 0:
            if target_opp[target.pos].battle_mode == BattleMode.ATTACK:
                target_opp.lp -= delta_damage
            target_opp[target.pos] = None
        elif delta_damage < 0:
            true_delta_damage = -delta_damage
            source_opp.lp -= true_delta_damage
            if target_opp[target.pos].battle_mode == BattleMode.ATTACK:
                source_opp[source.pos] = None

    else:
        raise NotImplementedError

    return None
