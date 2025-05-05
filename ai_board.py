import itertools
from typing import Iterator

from ai import *
from probability_tree import *

skip_defend_monsters: list[str] = [
    'Blue-eyes Ultimate Dragon',
    'Gate Guardian',
    'Perfectly Ultimate Great Moth',
    'Meteor B. Dragon',
    'B. Skull Dragon',
    'Black Luster Soldier',
    'Blue-Eyes White Dragon',
    'Metalzoa'
]

fields_board_ai: list[str] = [
    'Forest',
    'Wasteland',
    'Mountain',
    'Sogen',
    'Umi',
    'Yami'
]

forced_defend_monsters: list[str] = [
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


def lbl_next_battle(cur: Cursor, player: Opponent, ai_player: Opponent, field: Field,
                    always_look_facedown_cards: bool) -> Optional[Actions]:
    """ Returns `None` when no more battle is available. """

    actions: Optional[Actions] = None

    # End of turn
    if is_empty(ai_player['frontrow']):
        actions = None
        return actions

    # Player has no monsters : attack with all remaining AI monsters
    if is_empty(player['frontrow']):
        actions = Actions([
            Action([(card['pos'], ATTACK, encode_frontrow_pos(2))])
            for card in sorted(list(filter(lambda x: x is not None
                                                     and x['is_active'],
                                           ai_player['frontrow'])),
                               key=lambda x: descending_true_atk_sorting_key(cur, x, field))
        ])
        return actions

    # Check for lethal if player has visible monsters
    if 0 < len(list(filter(lambda x: x is not None
                                     and (always_look_facedown_cards or x['face'] == FACE_UP)
                                     and x['battle_mode'] == ATTACK,
                           player['frontrow']))):
        ai_pos, _ = get_first_pos_of_max_true_atk_in(cur, ai_player['frontrow'], field, True, only_check_active=True)
        pl_pos, _ = get_first_pos_of_lowest_true_atk_in(cur, player['frontrow'], field, always_look_facedown_cards,
                                                        battle_mode=ATTACK)

        ai_stat = calculate_max_base_stat_plus_field(cur, ai_player['frontrow'][ai_pos]['id'], field)
        pl_stat = calculate_max_base_stat_plus_field(cur, player['frontrow'][pl_pos]['id'], field) \
            if any(player['frontrow']) else 0

        if ai_stat - pl_stat >= player['LP'] \
                and any(player['frontrow']) \
                and pl_pos is not None:
            actions = Actions([
                Action([(encode_frontrow_pos(ai_pos), ATTACK, encode_frontrow_pos(pl_pos))])
            ])
            return actions

    # Battle visible player monsters in attack
    for pl_card in sorted(list(filter(lambda x: x is not None
                                                and (always_look_facedown_cards or x['face'] == FACE_UP)
                                                and x['battle_mode'] == ATTACK,
                                      player['frontrow'])),
                          key=lambda x: descending_true_atk_sorting_key(cur, x, field)):
        for ai_card in sorted(list(filter(lambda x: x is not None
                                                    and x['is_active'],
                                          ai_player['frontrow'])),
                              key=lambda x: ascending_true_atk_sorting_key(cur, x, field)):
            pl_atk = calculate_true_atk_stat(cur, pl_card['id'], field, pl_card['equip_stage']) \
                     + 500 * has_advantage_over(pl_card['star'], ai_card['star'])
            ai_atk = calculate_true_atk_stat(cur, ai_card['id'], field, ai_card['equip_stage']) \
                     + 500 * has_advantage_over(ai_card['star'], pl_card['star'])

            if ai_atk > pl_atk:
                actions = Actions([
                    Action([(ai_card['pos'], ATTACK, pl_card['pos'])])
                ])
                return actions

    # Battle visible player monsters in defense
    for pl_card in sorted(list(filter(lambda x: x is not None
                                                and (always_look_facedown_cards or x['face'] == FACE_UP)
                                                and x['battle_mode'] == DEFENSE,
                                      player['frontrow'])),
                          key=lambda x: descending_true_def_sorting_key(cur, x, field)):
        for ai_card in sorted(list(filter(lambda x: x is not None
                                                    and x['is_active'],
                                          ai_player['frontrow'])),
                              key=lambda x: ascending_true_atk_sorting_key(cur, x, field)):
            pl_def = calculate_true_def_stat(cur, pl_card['id'], field, pl_card['equip_stage']) \
                     + 500 * has_advantage_over(pl_card['star'], ai_card['star'])
            ai_atk = calculate_true_atk_stat(cur, ai_card['id'], field, ai_card['equip_stage']) \
                     + 500 * has_advantage_over(ai_card['star'], pl_card['star'])

            if ai_atk > pl_def:
                actions = Actions([
                    Action([(ai_card['pos'], ATTACK, pl_card['pos'])])
                ])
                return actions

    # Battle facedown player monsters
    actions = Actions()
    attack_odds = Odds((get_ai_stats(ai_player['name']).attack_percent, 100))
    no_attack_odds = attack_odds.complementary()

    for ai_card in sorted(list(filter(lambda x: x is not None
                                                and x['is_active'],
                                      ai_player['frontrow'])),
                          key=lambda x: descending_true_atk_sorting_key(cur, x, field)):
        _next: Actions = actions
        no_attack: Optional[Action] = None
        cur_level = Action.BASE_LEVEL - 1
        for pl_card in sorted(list(filter(lambda x: x is not None
                                                    and not always_look_facedown_cards
                                                    and x['face'] == FACE_DOWN,
                                          player['frontrow'])),
                              key=lambda x: x['pos']):
            cur_level += 1
            attack = Action([(ai_card['pos'], ATTACK, pl_card['pos'])], odds=attack_odds)
            no_attack = Action([], odds=no_attack_odds)
            _next.append_horizontally([attack, no_attack], level=cur_level)

            _next = no_attack.next

        # If the player has monsters left
        if any(list(filter(None, player['frontrow']))):
            if ai_card['name'] in skip_defend_monsters:
                no_attack.description.append((ai_card['pos'], ATTACK))
            else:
                no_attack.description.append((ai_card['pos'], DEFENSE))

        return actions

    assert(False, "Should never be reached")


def board_ai(cur: Cursor, player: Opponent, ai_player: Opponent, field: Field = None) -> Iterator[Actions]:
    """ Creates an iterator of actions to perform on the board. This does not modify the board.
    Odds are not cumulated. Returns `None` when no more action is possible. """

    actions: Optional[Actions] = None
    always_look_facedown_cards = get_ai_stats(ai_player['name']).attack_percent == AIStat.SEE_THROUGH

    # Magic zone
    if any(ai_player['backrow']):
        # Harpie's Feather Duster
        while (pos := get_first_pos_in(cur, "Harpie's Feather Duster", ai_player['backrow'], only_check_active=True)) \
                      is not None:
            if any(player['backrow']):
                harpie_odds = Odds((get_ai_stats(ai_player['name']).spell_percent, 100))
                actions = Actions([
                    Action([(encode_backrow_pos(pos), FACE_UP)], odds=harpie_odds),
                    Action([(encode_backrow_pos(pos), DARKEN)], odds=harpie_odds.complementary())
                ])
            else:
                actions = Actions([
                    Action([(encode_backrow_pos(pos), DARKEN)])
                ])
            yield actions

    if any(ai_player['backrow']):
        # Direct damage / heal
        for card_name, _ in itertools.chain(direct_damages.items(), direct_heals.items()):
            while (pos := get_first_pos_in(cur, card_name, ai_player['backrow'], only_check_active=True)) \
                          is not None:
                if player['LP'] > ai_player['LP']:
                    if ai_player['LP'] > get_ai_stats(ai_player['name']).low_lp_threshold \
                            or not any(player['backrow']):
                        actions = Actions([
                            Action([(encode_backrow_pos(pos), FACE_UP)])
                        ])
                    else:
                        magic_odds = Odds((100 - get_ai_stats(ai_player['name']).spell_percent, 100))
                        actions = Actions([
                            Action([(encode_backrow_pos(pos), FACE_UP)], odds=magic_odds),
                            Action([(encode_backrow_pos(pos), DARKEN)], odds=magic_odds.complementary())
                        ])
                else:
                    actions = Actions([
                        Action([(encode_backrow_pos(pos), DARKEN)])
                    ])
                yield actions

    if any(ai_player['backrow']):
        # Equips
        while (equip_pos := get_first_pos_of_type_in(cur, 'Equip', ai_player['backrow'], only_check_active=True)) \
                            is not None:
            equip_id: int = ai_player['backrow'][equip_pos]['id']
            monster_pos = get_first_monster_compatible_in(cur, equip_id, ai_player['frontrow'])
            if monster_pos is not None:
                actions = Actions([
                    Action([(encode_backrow_pos(equip_pos), FACE_UP), (encode_frontrow_pos(monster_pos), FACE_UP)])
                ])
            else:
                actions = Actions([
                    Action([(encode_backrow_pos(equip_pos), DARKEN)])
                ])
            yield actions

    if any(ai_player['backrow']):
        # Rituals
        while (ritual_pos := get_first_pos_of_type_in(cur, 'Ritual', ai_player['backrow'], only_check_active=True)) \
                             is not None:
            ritual_id = ai_player['backrow'][ritual_pos]['id']
            if check_ritual(cur, ritual_id, ai_player['frontrow']):
                actions = Actions([
                    Action([(encode_backrow_pos(ritual_pos), FACE_UP)])
                ])
            else:
                actions = Actions([
                    Action([(encode_backrow_pos(ritual_pos), DARKEN)])
                ])
            yield actions

    if any(ai_player['backrow']):
        # Dark-piercing Light
        while (pos := get_first_pos_in(cur, 'Dark-piercing Light', ai_player['backrow'], only_check_active=True)) \
                      is not None:
            if any(player['frontrow']) \
                    and all([card['face'] == FACE_DOWN for card in filter(None, player['frontrow'])]) \
                    and len(list(filter(None, player['frontrow']))) > len(list(filter(None, ai_player['frontrow']))):
                actions = Actions([
                    Action([(encode_backrow_pos(pos), FACE_UP)])
                ])
            else:
                actions = Actions([
                    Action([(encode_backrow_pos(pos), DARKEN)])
                ])
            yield actions

    if any(ai_player['backrow']):
        # Swords of Revealing Light
        while (pos := get_first_pos_in(cur, 'Swords of Revealing Light', ai_player['backrow'], only_check_active=True)) \
                      is not None:
            if player['remaining_turns_under_swords'] == 0 \
                    and any(filter(lambda x: x is not None
                                             and (always_look_facedown_cards or x['face'] == FACE_UP),
                                   player['frontrow'])):
                if is_empty(ai_player['frontrow']):
                    actions = Actions([
                        Action([(encode_backrow_pos(pos), FACE_UP)])
                    ])
                else:
                    player_pos, _ = get_first_pos_of_true_max_stat_in(cur, player['frontrow'], field,
                                                                      always_look_facedown_cards)
                    player_stat = calculate_max_base_stat_plus_field(cur, player['frontrow'][player_pos]['id'], field)
                    ai_pos, _ = get_first_pos_of_true_max_stat_in(cur, ai_player['frontrow'], field, True)
                    ai_stat = calculate_max_base_stat_plus_field(cur, ai_player['frontrow'][player_pos]['id'], field)
                    if player_stat >= ai_stat:
                        actions = Actions([
                            Action([(encode_backrow_pos(pos), FACE_UP)])
                        ])
                    else:
                        actions = Actions([
                            Action([(encode_backrow_pos(pos), DARKEN)])
                        ])
            else:
                actions = Actions([
                    Action([(encode_backrow_pos(pos), DARKEN)])
                ])
            yield actions

    if any(ai_player['backrow']):
        # Stop Defense
        while (pos := get_first_pos_in(cur, 'Stop Defense', ai_player['backrow'], only_check_active=True)) \
                      is not None:
            if ai_player['remaining_turns_under_swords'] == 0 \
                    and any(filter(None, player['frontrow'])) \
                    and any(filter(None, ai_player['frontrow'])):
                ai_pos, _ = get_first_pos_of_true_max_stat_in(cur, ai_player['frontrow'], field, True)
                pl_pos, _ = get_first_pos_of_lowest_true_max_stat_in(cur, player['frontrow'], field,
                                                                     always_look_facedown_cards)

                ai_stat = calculate_true_atk_stat(cur, ai_player['frontrow'][ai_pos]['id'], field, ai_player['frontrow'][ai_pos]['equip_stage'])
                pl_stat = calculate_true_atk_stat(cur, player['frontrow'][pl_pos]['id'], field, ai_player['frontrow'][ai_pos]['equip_stage'])

                # Lethal
                if ai_stat - pl_stat >= player['LP']:
                    actions = Actions([
                        Action([(encode_backrow_pos(pos), FACE_UP)])
                    ])
                # AI has at least as many monsters as the player
                elif len([filter(None, ai_player['frontrow'])]) \
                        >= len([filter(lambda x: x is not None and (always_look_facedown_cards or x['face'] == FACE_UP),
                                      player['frontrow'])]):
                    # each element of the sorted (in descending order) set of
                    # true attacks of visible player monsters is less than the
                    # corresponding element of the similarly sorted set
                    # of true attacks of AI monsters.

                    sort_info = {}
                    for side_key, player_dic in {'ai': ai_player, 'pl': player}.items():
                        sort_info[side_key] = []
                        for card in sorted(filter(
                                    None if player_dic == ai_player
                                    else lambda x: x is not None and (always_look_facedown_cards or x['face'] == FACE_UP),
                                    player_dic['frontrow']),
                                key=lambda card: descending_true_max_stat_sorting_key(cur, card, field)):
                            sort_info[side_key].append(
                                calculate_true_max_stat(cur, card['id'], field, card['equip_stage']))

                    if all([pl_stat < ai_stat for ai_stat, pl_stat in zip(sort_info['ai'], sort_info['pl'])]):
                        actions = Actions([
                            Action([(encode_backrow_pos(pos), FACE_UP)])
                        ])
                    else:
                        actions = Actions([
                            Action([(encode_backrow_pos(pos), DARKEN)])
                        ])
                else:
                    actions = Actions([
                        Action([(encode_backrow_pos(pos), DARKEN)])
                    ])
            else:
                actions = Actions([
                    Action([(encode_backrow_pos(pos), DARKEN)])
                ])
            yield actions

    if any(ai_player['backrow']):
        # Type counters
        for _type, counter in type_counter_magics.items():
            while (pos := get_first_pos_in(cur, counter, ai_player['backrow'], only_check_active=True)) \
                          is not None:
                if ai_thinks_it_lacks_field_control(cur, player['frontrow'], ai_player['frontrow'], field,
                                                    always_look_facedown_cards):
                    player_pos, _ = get_first_pos_of_true_max_stat_in(cur, player['frontrow'], field,
                                                                      always_look_facedown_cards)
                    if _type == get_card_type_from_id(cur, player['frontrow'][player_pos]['id']):
                        actions = Actions([
                            Action([(encode_backrow_pos(pos), FACE_UP)])
                        ])
                    else:
                        actions = Actions([
                            Action([(encode_backrow_pos(pos), DARKEN)])
                        ])
                else:
                    actions = Actions([
                        Action([(encode_backrow_pos(pos), DARKEN)])
                    ])
                yield actions

    if any(ai_player['backrow']):
        # Decrease stats
        for name in ['Spellbinding Circle', 'Shadow Spell']:
            while (pos := get_first_pos_in(cur, name, ai_player['backrow'])) \
                          is not None:
                if ai_thinks_it_lacks_field_control(cur, player['frontrow'], ai_player['frontrow'], field,
                                                    always_look_facedown_cards):
                    actions = Actions([
                        Action([(encode_backrow_pos(pos), FACE_UP)])
                    ])
                else:
                    actions = Actions([
                        Action([(encode_backrow_pos(pos), DARKEN)])
                    ])
                yield actions

    if any(ai_player['backrow']):
        # Crush Card
        while (pos := get_first_pos_in(cur, 'Crush Card', ai_player['backrow'])) \
                      is not None:
            if ai_thinks_it_lacks_field_control(cur, player['frontrow'], ai_player['frontrow'], field,
                                                always_look_facedown_cards):
                player_pos, _ = get_first_pos_of_true_max_stat_in(cur, player['frontrow'], field,
                                                                  always_look_facedown_cards)
                # Skips equips
                player_stat = calculate_max_base_stat_plus_field(cur, player['frontrow'][player_pos]['id'], field)
                if player_stat >= 1_500:
                    actions = Actions([
                        Action([(encode_backrow_pos(pos), FACE_UP)])
                    ])
                else:
                    actions = Actions([
                        Action([(encode_backrow_pos(pos), DARKEN)])
                    ])
            else:
                actions = Actions([
                    Action([(encode_backrow_pos(pos), DARKEN)])
                ])
            yield actions

    if any(ai_player['backrow']):
        # Raigeki
        while (pos := get_first_pos_in(cur, 'Raigeki', ai_player['backrow'])) \
                      is not None:
            if ai_thinks_it_lacks_field_control(cur, player['frontrow'], ai_player['frontrow'], field,
                                                always_look_facedown_cards) \
                    and len(list(filter(lambda x: x is not None and (always_look_facedown_cards or ['face'] == FACE_UP),
                                        player['frontrow']))) \
                    >= len(list(filter(None, ai_player['frontrow']))):
                actions = Actions([
                    Action([(encode_backrow_pos(pos), FACE_UP)])
                ])
            else:
                actions = Actions([
                    Action([(encode_backrow_pos(pos), DARKEN)])
                ])
            yield actions

    if any(ai_player['backrow']):
        # Fields
        for new_field in fields_board_ai:
            while (pos := get_first_pos_in(cur, new_field, ai_player['backrow'])) \
                          is not None:
                if ai_thinks_it_lacks_field_control(cur, player['frontrow'], ai_player['frontrow'], field,
                                                    always_look_facedown_cards) \
                        and field != new_field:
                    pos_player, _ \
                        = get_first_pos_of_true_max_stat_in(cur, player['frontrow'], field, always_look_facedown_cards)
                    type_player = get_card_type_from_id(cur, player['frontrow'][pos_player]['id'])

                    pos_ai, _ = get_first_pos_of_true_max_stat_in(cur, ai_player['frontrow'], field, True)
                    type_ai = get_card_type_from_id(cur, ai_player['frontrow'][pos_player]['id']) \
                        if pos_ai is not None \
                        else 'Dragon'

                    is_player_boosted = is_stat_increased(type_player, field, new_field)
                    is_player_weakened = is_stat_decreased(type_player, field, new_field)
                    is_ai_boosted = is_stat_increased(type_ai, field, new_field)
                    is_ai_weakened = is_stat_decreased(type_ai, field, new_field)

                    if not is_player_boosted and not is_ai_weakened and (is_player_weakened or is_ai_boosted):
                        actions = Actions([
                            Action([(encode_backrow_pos(pos), FACE_UP)])
                        ])
                    else:
                        actions = Actions([
                            Action([(encode_backrow_pos(pos), DARKEN)])
                        ])
                else:
                    actions = Actions([
                        Action([(encode_backrow_pos(pos), DARKEN)])
                    ])
                yield actions

    if any(ai_player['backrow']):
        # Dark Hole
        while (pos := get_first_pos_in(cur, 'Dark Hole', ai_player['backrow'])) \
                      is not None:
            if ai_thinks_it_lacks_field_control(cur, player['frontrow'], ai_player['frontrow'], field,
                                                always_look_facedown_cards) \
                    and len(list(filter(None, player['frontrow']))) > len(list(filter(None, ai_player['frontrow']))):
                actions = Actions([
                    Action([(encode_backrow_pos(pos), FACE_UP)])
                ])
            else:
                actions = Actions([
                    Action([(encode_backrow_pos(pos), DARKEN)])
                ])
            yield actions

    if any(ai_player['frontrow']):
        # Forced defend
        for name in forced_defend_monsters:
            while (pos := get_first_pos_in(cur, name, ai_player['frontrow'], only_check_active=True)) \
                          is not None:
                actions = Actions([
                    Action([(encode_frontrow_pos(pos), DEFENSE)])
                ])
                yield actions

    if any(ai_player['frontrow']):
        # Execute defend if under Swords
        if ai_player['remaining_turns_under_swords'] > 0:
            while (pos_stat := get_first_pos_of_true_max_stat_in(cur, ai_player['frontrow'], field, True,
                                                           only_check_active=True)) \
                               is not None:
                pos, _ = pos_stat
                if ai_player['frontrow'][pos]['name'] in skip_defend_monsters:
                    actions = Actions([
                        Action([(encode_frontrow_pos(pos), ATTACK)])
                    ])
                else:
                    actions = Actions([
                        Action([(encode_frontrow_pos(pos), DEFENSE)])
                    ])
                yield actions
        else:
            while (actions := lbl_next_battle(cur, player, ai_player, field, always_look_facedown_cards)) \
                             is not None:
                yield actions

    yield None
