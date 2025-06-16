import itertools

from ai import *
from probability_tree import *
from types_ import Field, Opponent, IsActive, EndOfTurn

skip_defend_monsters: list[str] = [  # Order compatible with AI routine
    'Blue-eyes Ultimate Dragon',
    'Gate Guardian',
    'Perfectly Ultimate Great Moth',
    'Meteor B. Dragon',
    'B. Skull Dragon',
    'Black Luster Soldier',
    'Blue-Eyes White Dragon',
    'Metalzoa'
]


forced_defend_monsters: list[str] = [  # Order compatible with AI routine
    'Cocoon of Evolution',
    'Millennium Shield',
    'Labyrinth Wall',
    'Mystical Elf',
    'Dragon Piper',
    'Castle of Dark Illusions',
    'Metal Guardian',
    'Sleeping Lion',
    'Hard Armor',
    'Spirit of the Harp',
    'Prevent Rat',
    'Green Phantom King',
    'Gorgon Egg',
    'Wall Shadow',
    'Blocker',
    'Golgoil',
    '30,000-Year White Turtle',
    'Queen Bird',
    'Yado Karu',
    'Boulder Tortoise'
]


def is_active(card: Card) -> bool:
    return card is not None and card.is_active


def is_faceup(card: Card, always_look_facedown_cards: bool) -> bool:
    return (
        card is not None
        and (always_look_facedown_cards or card.face == Face.UP)
    )


def is_faceup_attack(card: Card, always_look_facedown_cards: bool) -> bool:
    return (
        card is not None
        and (always_look_facedown_cards or card.face == Face.UP)
        and card.battle_mode == BattleMode.ATTACK
    )


def is_faceup_defense(card: Card, always_look_facedown_cards: bool) -> bool:
    return (
        card is not None
        and (always_look_facedown_cards or card.face == Face.UP)
        and card.battle_mode == BattleMode.DEFENSE
    )


def is_facedown(card: Card, always_look_facedown_cards: bool) -> bool:
    return (
        card is not None
        and not always_look_facedown_cards
        and card.face == Face.DOWN
    )


def lbl_next_battle(player: Opponent, ai_player: Opponent, always_look_facedown_cards: bool) \
        -> Actions | None:
    """ Returns `None` if there is no more battle. Does not modify the opponent. """

    actions: Actions | None

    # End of turn
    if is_empty(ai_player.frontrow):
        actions = None
        return actions

    # Player has no monsters : attack with all remaining AI monsters
    # TODO : this was changed to only yield one monster at a time. Change it back if it's justified
    if is_empty(player.frontrow):
        # actions = Actions()
        # for card in sorted(
        #         list(filter(is_active, ai_player.frontrow)),
        #         key=descending_true_atk_sorting_key
        # ):
        #     action = Action([Action.Description(card.pos, BattleMode.ATTACK, Position(2, Position.Mode.FRONTROW))])
        #     actions.append_deepest_horizontally([action])
        #
        # if len(actions) > 0:
        #     return actions
        for card in sorted(
            list(filter(is_active, ai_player.frontrow)),
            key=descending_true_atk_sorting_key
        ):
            actions = Actions([
                Action([Action.Description(card.pos, BattleMode.ATTACK, Position(2, Position.Mode.FRONTROW))])
            ])
            return actions

    # Check for lethal if player has visible monsters
    if any(filter(lambda x: is_faceup_attack(x, always_look_facedown_cards), player.frontrow)):
        ai_card, _ = first_card_with_best_true_atk_in(ai_player.frontrow,
                                                      look_facedown_cards=True, only_check_active=True)
        pl_card, _ = first_card_with_worst_true_atk_in(player.frontrow,
                                                       look_facedown_cards=always_look_facedown_cards,
                                                       battle_mode=BattleMode.ATTACK)

        ai_atk = ai_card.base_attack_plus_field
        pl_atl = pl_card.base_attack_plus_field

        if ai_atk - pl_atl >= player.lp:  # and pl_card is not None:  # TODO: and any(player.frontrow) \ ?
            actions = Actions([
                Action([Action.Description(ai_card.pos, BattleMode.ATTACK, pl_card.pos)])
            ])
            return actions

    # Battle visible player monsters in attack
    for pl_card in sorted(list(filter(lambda x: is_faceup_attack(x, always_look_facedown_cards),
                                      player.frontrow)),
                          key=descending_true_atk_sorting_key):
        for ai_card in sorted(list(filter(is_active,
                                          ai_player.frontrow)),
                              key=ascending_true_atk_sorting_key):
            pl_atk = (
                pl_card.true_attack
                + 500 * pl_card.star.has_advantage_over(ai_card.star)
            )
            ai_atk = (
                ai_card.true_attack
                + 500 * ai_card.star.has_advantage_over(pl_card.star)
            )

            if ai_atk > pl_atk:
                actions = Actions([
                    Action([Action.Description(ai_card.pos, BattleMode.ATTACK, pl_card.pos)])
                ])
                return actions

    # Battle visible player monsters in defense
    for pl_card in sorted(list(filter(lambda x: is_faceup_defense(x, always_look_facedown_cards),
                                      player.frontrow)),
                          key=descending_true_def_sorting_key):
        for ai_card in sorted(list(filter(is_active,
                                          ai_player.frontrow)),
                              key=ascending_true_atk_sorting_key):
            pl_def = (
                pl_card.true_defense
                + 500 * pl_card.star.has_advantage_over(ai_card.star)
            )
            ai_atk = (
                ai_card.true_attack
                + 500 * ai_card.star.has_advantage_over(pl_card.star)
            )

            if ai_atk > pl_def:
                actions = Actions([
                    Action([Action.Description(ai_card.pos, BattleMode.ATTACK, pl_card.pos)])
                ])
                return actions

    # Battle facedown player monsters
    actions = Actions()
    attack_odds = Odds((get_ai_stats(ai_player.name).attack_percent, 100))
    no_attack_odds = attack_odds.complementary()

    for ai_card in sorted(list(filter(is_active,
                                      ai_player.frontrow)),
                          key=descending_true_atk_sorting_key):
        _next: Actions = actions
        no_attack: Action | None = None
        cur_level = Action.BASE_LEVEL - 1
        for pl_card in sorted(list(filter(lambda x: is_facedown(x, always_look_facedown_cards),
                                          player.frontrow)),
                              key=lambda x: x.pos):
            cur_level += 1
            attack = Action(
                [Action.Description(ai_card.pos, BattleMode.ATTACK, pl_card.pos)],
                odds=attack_odds
            )
            no_attack = Action([], odds=no_attack_odds)
            _next.append_horizontally([attack, no_attack], level=cur_level)

            _next = no_attack.next

        # If the player has monsters left
        if any(list(filter(None, player.frontrow))):
            if ai_card.name in skip_defend_monsters:
                no_attack.descriptions.append(Action.Description(ai_card.pos, BattleMode.ATTACK))
            else:
                no_attack.descriptions.append(Action.Description(ai_card.pos, BattleMode.DEFENSE))

        return actions

    assert False, "Should never be reached"


def board_ai(cursor: Cursor, player: Opponent, ai_player: Opponent, field: Field) \
        -> Iterator[Actions]:
    """ Creates an iterator of actions to perform on the board. This does not modify the board. """

    actions: Actions | None
    always_look_facedown_cards = get_ai_stats(ai_player.name).attack_percent == AIStat.SEE_THROUGH

    # Magic zone
    if any(ai_player.backrow):
        # Harpie's Feather Duster
        while (card := get_first_card_in("Harpie's Feather Duster", ai_player.backrow, 
                                         only_check_active=True)) \
                      is not None:
            if any(player.backrow):
                harpie_odds = Odds((get_ai_stats(ai_player.name).spell_percent, 100))
                actions = Actions([
                    Action([Action.Description(card.pos, Face.UP)], odds=harpie_odds),
                    Action([Action.Description(card.pos, IsActive.DARKEN)], odds=harpie_odds.complementary())
                ])
            else:
                actions = Actions([
                    Action([Action.Description(card.pos, IsActive.DARKEN)])
                ])
            yield actions

    if any(ai_player.backrow):
        # Direct damage / heal
        for card_name, _ in itertools.chain(direct_damages.items(), direct_heals.items()):
            while (card := get_first_card_in(card_name, ai_player.backrow, only_check_active=True)) \
                          is not None:
                if player.lp > ai_player.lp:
                    if ai_player.lp > get_ai_stats(ai_player.name).low_lp_threshold \
                            or not any(player.backrow):
                        actions = Actions([
                            Action([Action.Description(card.pos, Face.UP)])
                        ])
                    else:
                        magic_odds = Odds((100 - get_ai_stats(ai_player.name).spell_percent, 100))
                        actions = Actions([
                            Action([Action.Description(card.pos, Face.UP)], odds=magic_odds),
                            Action([Action.Description(card.pos, IsActive.DARKEN)], odds=magic_odds.complementary())
                        ])
                else:
                    actions = Actions([
                        Action([Action.Description(card.pos, IsActive.DARKEN)])
                    ])
                yield actions

    if any(ai_player.backrow):
        # Equips
        while (equip_card := first_card_with_type_in(Type.EQUIP, ai_player.backrow, only_check_active=True)) \
                            is not None:
            monster_card = get_first_card_equipable_with_in(cursor, equip_card.id, ai_player.frontrow)
            if monster_card is not None:
                actions = Actions([
                    Action([Action.Description(equip_card.pos, Face.UP, monster_card.pos)])
                ])
            else:
                actions = Actions([
                    Action([Action.Description(equip_card.pos, IsActive.DARKEN)])
                ])
            yield actions

    if any(ai_player.backrow):
        # Rituals
        while (ritual_card := first_card_with_type_in(Type.RITUAL, ai_player.backrow, only_check_active=True)) \
                             is not None:
            if check_ritual(cursor, ritual_card.id, ai_player.frontrow).is_successful:
                actions = Actions([  # TODO: check_ritual has all ritual info
                    Action([Action.Description(ritual_card.pos, Face.UP)])
                ])
            else:
                actions = Actions([
                    Action([Action.Description(ritual_card.pos, IsActive.DARKEN)])
                ])
            yield actions

    if any(ai_player.backrow):
        # Dark-piercing Light
        while (card := get_first_card_in('Dark-piercing Light', ai_player.backrow, only_check_active=True)) \
                      is not None:
            if any(player.frontrow) \
                    and all([card.face == Face.DOWN for card in filter(None, player.frontrow)]) \
                    and len(list(filter(None, player.frontrow))) > len(list(filter(None, ai_player.frontrow))):
                actions = Actions([
                    Action([Action.Description(card.pos, Face.UP)])
                ])
            else:
                actions = Actions([
                    Action([Action.Description(card.pos, IsActive.DARKEN)])
                ])
            yield actions

    if any(ai_player.backrow):
        # Swords of Revealing Light
        while (card := get_first_card_in('Swords of Revealing Light', ai_player.backrow, only_check_active=True)) \
                      is not None:
            if player.remaining_turns_under_swords == 0 \
                    and any(filter(lambda x: is_faceup(x, always_look_facedown_cards),
                                   player.frontrow)):
                if is_empty(ai_player.frontrow):
                    actions = Actions([
                        Action([Action.Description(card.pos, Face.UP)])
                    ])
                else:
                    player_card, _ = first_card_with_best_true_max_stat_in(
                        player.frontrow,
                        look_facedown_cards=always_look_facedown_cards
                    )
                    player_stat = player_card.max_base_stat_plus_field
                    ai_card, _ = first_card_with_best_true_max_stat_in(ai_player.frontrow, look_facedown_cards=True)
                    if ai_card is None or player_stat >= ai_card.max_base_stat_plus_field:
                        actions = Actions([
                            Action([Action.Description(card.pos, Face.UP)])
                        ])
                    else:
                        actions = Actions([
                            Action([Action.Description(card.pos, IsActive.DARKEN)])
                        ])
            else:
                actions = Actions([
                    Action([Action.Description(card.pos, IsActive.DARKEN)])
                ])
            yield actions

    if any(ai_player.backrow):
        # Stop Defense
        while (card := get_first_card_in('Stop Defense', ai_player.backrow, only_check_active=True)) \
                      is not None:
            # Both players must have monster(s) with AI not under swords
            if not (
                ai_player.remaining_turns_under_swords == 0
                and any(filter(None, player.frontrow))
                and any(filter(None, ai_player.frontrow))
            ):
                actions = Actions([
                    Action([Action.Description(card.pos, IsActive.DARKEN)])
                ])
                yield actions
                continue

            ai_card, _ = first_card_with_best_true_max_stat_in(ai_player.frontrow, look_facedown_cards=True)
            pl_card, _ = first_card_with_worst_true_max_stat_in(player.frontrow,
                                                                look_facedown_cards=always_look_facedown_cards)

            # Lethal
            if ai_card.base_attack_plus_field - pl_card.base_attack_plus_field >= player.lp:
                actions = Actions([
                    Action([Action.Description(card.pos, Face.UP)])
                ])
                yield actions
                continue

            # AI must have at least as many monsters as the player has visible monsters
            if not (
                len(list(filter(None, ai_player.frontrow)))
                >= len(list(filter(lambda x: is_faceup(x, always_look_facedown_cards),
                                   player.frontrow)))
            ):
                actions = Actions([
                    Action([Action.Description(card.pos, IsActive.DARKEN)])
                ])
                yield actions
                continue

            # each element of the sorted (in descending order) set of
            # true attacks of visible player monsters is less than the
            # corresponding element of the similarly sorted set
            # of true attacks of AI monsters.

            sort_info = {}
            for side_key, player_dic in {'ai': ai_player, 'pl': player}.items():
                sort_info[side_key] = []
                for monster in sorted(filter(
                            None if player_dic == ai_player
                            else lambda x: is_faceup(x, always_look_facedown_cards),
                            player_dic.frontrow),
                        key=descending_true_max_stat_sorting_key):
                    sort_info[side_key].append(monster.true_max_stat)

            if all([ai_stat > pl_stat for ai_stat, pl_stat in zip(sort_info['ai'], sort_info['pl'])]):
                actions = Actions([
                    Action([Action.Description(card.pos, Face.UP)])
                ])
            else:
                actions = Actions([
                    Action([Action.Description(card.pos, IsActive.DARKEN)])
                ])
            yield actions

    if any(ai_player.backrow):
        # Type counters
        for _type, counter in type_counter_magics.items():
            while (card := get_first_card_in(counter, ai_player.backrow, only_check_active=True)) \
                          is not None:
                if ai_thinks_it_lacks_field_control(player.frontrow, ai_player.frontrow,
                                                    look_facedown_cards=always_look_facedown_cards):
                    player_card, _ = first_card_with_best_true_max_stat_in(
                        player.frontrow,
                        look_facedown_cards=always_look_facedown_cards
                    )
                    if _type == player_card.type:
                        actions = Actions([
                            Action([Action.Description(card.pos, Face.UP)])
                        ])
                    else:
                        actions = Actions([
                            Action([Action.Description(card.pos, IsActive.DARKEN)])
                        ])
                else:
                    actions = Actions([
                        Action([Action.Description(card.pos, IsActive.DARKEN)])
                    ])
                yield actions

    if any(ai_player.backrow):
        # Decrease stats
        for name in ['Spellbinding Circle', 'Shadow Spell']:
            while (card := get_first_card_in(name, ai_player.backrow)) \
                          is not None:
                if ai_thinks_it_lacks_field_control(player.frontrow, ai_player.frontrow,
                                                    look_facedown_cards=always_look_facedown_cards):
                    actions = Actions([
                        Action([Action.Description(card.pos, Face.UP)])
                    ])
                else:
                    actions = Actions([
                        Action([Action.Description(card.pos, IsActive.DARKEN)])
                    ])
                yield actions

    if any(ai_player.backrow):
        # Crush Card
        while (card := get_first_card_in('Crush Card', ai_player.backrow)) \
                      is not None:
            if ai_thinks_it_lacks_field_control(player.frontrow, ai_player.frontrow,
                                                look_facedown_cards=always_look_facedown_cards):
                player_card, _ = first_card_with_best_true_max_stat_in(player.frontrow,
                                                                       look_facedown_cards=always_look_facedown_cards)

                if player_card.base_attack_plus_field >= CRUSH_CARD_MIN_ATTACK:
                    actions = Actions([
                        Action([Action.Description(card.pos, Face.UP)])
                    ])
                else:
                    actions = Actions([
                        Action([Action.Description(card.pos, IsActive.DARKEN)])
                    ])
            else:
                actions = Actions([
                    Action([Action.Description(card.pos, IsActive.DARKEN)])
                ])
            yield actions

    if any(ai_player.backrow):
        # Raigeki
        while (card := get_first_card_in('Raigeki', ai_player.backrow)) \
                      is not None:
            if ai_thinks_it_lacks_field_control(player.frontrow, ai_player.frontrow,
                                                look_facedown_cards=always_look_facedown_cards) \
                    and len(list(filter(lambda x: is_faceup(x, always_look_facedown_cards),
                                        player.frontrow))) \
                    >= len(list(filter(None, ai_player.frontrow))):
                actions = Actions([
                    Action([Action.Description(card.pos, Face.UP)])
                ])
            else:
                actions = Actions([
                    Action([Action.Description(card.pos, IsActive.DARKEN)])
                ])
            yield actions

    if any(ai_player.backrow):
        # Fields
        for new_field in Field:
            while (card := get_first_card_in(new_field, ai_player.backrow)) \
                          is not None:
                if ai_thinks_it_lacks_field_control(player.frontrow, ai_player.frontrow,
                                                    look_facedown_cards=always_look_facedown_cards) \
                        and field != new_field:
                    player_card, _ = first_card_with_best_true_max_stat_in(
                        player.frontrow,
                        look_facedown_cards=always_look_facedown_cards
                    )

                    ai_card, _ = first_card_with_best_true_max_stat_in(ai_player.frontrow,
                                                                       look_facedown_cards=True)
                    type_ai = ai_card.type if ai_card is not None else Type.DRAGON

                    is_player_boosted = is_stat_increased(player_card.type, field, new_field)
                    is_player_weakened = is_stat_decreased(player_card.type, field, new_field)
                    is_ai_boosted = is_stat_increased(type_ai, field, new_field)
                    is_ai_weakened = is_stat_decreased(type_ai, field, new_field)

                    if not is_player_boosted and not is_ai_weakened and (is_player_weakened or is_ai_boosted):
                        actions = Actions([
                            Action([Action.Description(card.pos, Face.UP)])
                        ])
                    else:
                        actions = Actions([
                            Action([Action.Description(card.pos, IsActive.DARKEN)])
                        ])
                else:
                    actions = Actions([
                        Action([Action.Description(card.pos, IsActive.DARKEN)])
                    ])
                yield actions

    if any(ai_player.backrow):
        # Dark Hole
        while (card := get_first_card_in('Dark Hole', ai_player.backrow)) \
                      is not None:
            if ai_thinks_it_lacks_field_control(player.frontrow, ai_player.frontrow,
                                                look_facedown_cards=always_look_facedown_cards) \
                    and len(list(filter(None, player.frontrow))) > len(list(filter(None, ai_player.frontrow))):
                actions = Actions([
                    Action([Action.Description(card.pos, Face.UP)])
                ])
            else:
                actions = Actions([
                    Action([Action.Description(card.pos, IsActive.DARKEN)])
                ])
            yield actions

    # Frontrow

    if any(ai_player.frontrow):
        # Forced defend
        for name in forced_defend_monsters:
            while (card := get_first_card_in(name, ai_player.frontrow, only_check_active=True)) \
                          is not None:
                actions = Actions([
                    Action([Action.Description(card.pos, BattleMode.DEFENSE)])
                ])
                yield actions

    if any(ai_player.frontrow):
        # Execute defend if under Swords
        if ai_player.remaining_turns_under_swords > 0:
            while (card_stat := first_card_with_best_true_max_stat_in(ai_player.frontrow,
                                                                    look_facedown_cards=True,
                                                                    only_check_active=True)) \
                                is not None:
                card, _ = card_stat
                if card.name in skip_defend_monsters:
                    actions = Actions([
                        Action([Action.Description(card.pos, BattleMode.ATTACK)])
                    ])
                else:
                    actions = Actions([
                        Action([Action.Description(card.pos, BattleMode.DEFENSE)])
                    ])
                yield actions
        else:
            while (actions := lbl_next_battle(player, ai_player, always_look_facedown_cards)) \
                             is not None:
                yield actions

    # End of turn
    actions = Actions([
        Action([Action.Description(None, EndOfTurn)])
    ])
    yield actions
