from ai_hand import *


# Hand AI subfunctions

def test_find_best_combo_in_ai_hand(cur, tests):
    results = []
    best_combos = []
    for index, test in enumerate(tests):
        board_card = test.get('board_card')
        if board_card is not None:
            board_card_name, board_card_pos, board_card_equip_level = board_card['name'], board_card['pos'], board_card[
                'equip_stage']
            board_card_id = get_card_id_from_name(cur, board_card_name)
            if board_card_name is not None and board_card_id is None:
                raise ValueError(f"{index}. Couldn't find id of board card name '{board_card_name}'.")
            board_card['id'] = board_card_id

        hand_names = test['hand_names']
        max_fusion_length = test['max_fusion_length']
        field = test['field'] if 'field' in test else None

        exp_ordering = test.get('exp_ordering')
        exp_result_name = test.get('exp_result_name')
        exp_result_id = get_card_id_from_name(cur, exp_result_name)
        if exp_result_name is not None and exp_result_id is None:
            raise ValueError(f"{index}. Couldn't find id of expected card name '{exp_result_name}'.")
        exp_equip_stage = test.get('exp_equip_stage')
        exp_result_max_stat = test.get('exp_result_max_stat')

        hand = [get_card_id_from_name(cur, card_name) for card_name in hand_names]
        if None in hand:
            raise ValueError(f"{index}. Couldn't find id of certain card names.\n{hand}, {hand_names}")

        best_combo = find_best_combo_in_ai_hand(cur, hand, board_card=board_card, field=field,
                                                max_fusion_length=max_fusion_length)
        best_combos.append(best_combo)

        actual_tests = [x for x in [exp_ordering, exp_result_id, exp_equip_stage, exp_result_max_stat] if x is not None]

        is_passed = True
        for actual_test in actual_tests:
            if actual_test == exp_ordering:
                for (res_pos, exp_pos) in zip(actual_test, best_combo.ordering):
                    is_passed &= res_pos == exp_pos
            elif actual_test == exp_result_id:
                is_passed &= exp_result_id == best_combo.result_id
            elif actual_test == exp_equip_stage:
                is_passed &= exp_equip_stage == best_combo.equip_stage
            elif actual_test == exp_result_max_stat:
                is_passed &= exp_result_max_stat == best_combo.result_max_stat

        results.append(is_passed)

    print(f"Successes: {len(list(filter(None, results)))} / {len(results)} :Total")
    print(f"Differences :", end=' ')
    print(*[{'index': index, 'found': best_combo, 'expected': test} for index, result, best_combo, test in
            zip(range(0, len(tests)), results, best_combos, tests) if not result], sep='\n')


def test_find_best_combo_in_ai_hand_and_board(cur, tests):
    results = []
    best_combos = []
    for index, test in enumerate(tests):
        monster_board = test.get('monster_board')
        if monster_board is not None:
            for board_card in monster_board:
                if board_card is not None:
                    board_card_name, board_card_pos, board_card_equip_level = board_card['name'], board_card['pos'], \
                                                                              board_card['equip_stage']
                    board_card_id = get_card_id_from_name(cur, board_card_name)
                    if board_card_name is not None and board_card_id is None:
                        raise ValueError(f"{index}. Couldn't find id of board card name '{board_card_name}'.")
                    board_card['id'] = board_card_id

        hand_names = test['hand_names']
        max_fusion_length = test['max_fusion_length']
        field = test['field'] if 'field' in test else None

        exp_ordering = test.get('exp_ordering')
        exp_result_name = test.get('exp_result_name')
        exp_result_id = get_card_id_from_name(cur, exp_result_name)
        if exp_result_name is not None and exp_result_id is None:
            raise ValueError(f"{index}. Couldn't find id of expected card name '{exp_result_name}'.")
        exp_equip_stage = test.get('exp_equip_stage')
        exp_result_max_stat = test.get('exp_result_max_stat')

        hand = [get_card_id_from_name(cur, card_name) for card_name in hand_names]
        if None in hand:
            raise ValueError(f"{index}. Couldn't find id of certain card names.\n{hand}, {hand_names}")

        best_combo = find_best_combo_in_ai_board_and_hand(cur, hand, monster_board=monster_board, field=field,
                                                          max_fusion_length=max_fusion_length)
        best_combos.append(best_combo)

        actual_tests = [x for x in [exp_ordering, exp_result_id, exp_equip_stage, exp_result_max_stat] if x is not None]

        is_passed = True
        for actual_test in actual_tests:
            if actual_test == exp_ordering:
                for (res_pos, exp_pos) in zip(actual_test, best_combo.ordering):
                    is_passed &= res_pos == exp_pos
            elif actual_test == exp_result_id:
                is_passed &= exp_result_id == best_combo.result_id
            elif actual_test == exp_equip_stage:
                is_passed &= exp_equip_stage == best_combo.equip_stage
            elif actual_test == exp_result_max_stat:
                is_passed &= exp_result_max_stat == best_combo.result_max_stat

        results.append(is_passed)

    print(f"Successes: {len(list(filter(None, results)))} / {len(results)} :Total")
    print(f"Differences :", end=' ')
    print(*[{'index': index, 'found': best_combo, 'expected': test} for index, result, best_combo, test in
            zip(range(0, len(tests)), results, best_combos, tests) if not result], sep='\n')


def test_improve_monster_from_ai_hand(cur, tests):
    results = []
    best_combos = []
    for index, test in enumerate(tests):
        board_card = test.get('board_card')
        if board_card is not None:
            board_card_name, board_card_pos, board_card_equip_level = board_card['name'], board_card['pos'], board_card[
                'equip_stage']
            board_card_id = get_card_id_from_name(cur, board_card_name)
            if board_card_name is not None and board_card_id is None:
                raise ValueError(f"{index}. Couldn't find id of board card name '{board_card_name}'.")
            board_card['id'] = board_card_id

        hand_names = test['hand_names']
        max_improve_length = test['max_improve_length']
        field = test['field'] if 'field' in test else None

        exp_ordering = test.get('exp_ordering')
        exp_result_name = test.get('exp_result_name')
        exp_result_id = get_card_id_from_name(cur, exp_result_name)
        if exp_result_name is not None and exp_result_id is None:
            raise ValueError(f"{index}. Couldn't find id of expected card name '{exp_result_name}'.")
        exp_equip_stage = test.get('exp_equip_stage')
        exp_result_max_stat = test.get('exp_result_max_stat')

        hand = [get_card_id_from_name(cur, card_name) for card_name in hand_names]
        if None in hand:
            raise ValueError(f"{index}. Couldn't find id of certain card names.\n{hand}, {hand_names}")

        best_combo = improve_monster_from_ai_hand(cur, hand, board_card=board_card, field=field,
                                                  max_improve_length=max_improve_length)
        best_combos.append(best_combo)

        actual_tests = [x for x in [exp_ordering, exp_result_id, exp_equip_stage, exp_result_max_stat] if x is not None]

        is_passed = True
        for actual_test in actual_tests:
            if actual_test == exp_ordering:
                for (res_pos, exp_pos) in zip(actual_test, best_combo.ordering):
                    is_passed &= res_pos == exp_pos
            elif actual_test == exp_result_id:
                is_passed &= exp_result_id == best_combo.result_id
            elif actual_test == exp_equip_stage:
                is_passed &= exp_equip_stage == best_combo.equip_stage
            elif actual_test == exp_result_max_stat:
                is_passed &= exp_result_max_stat == best_combo.result_max_stat

        results.append(is_passed)

    print(f"Successes: {len(list(filter(None, results)))} / {len(results)} :Total")
    print(f"Differences :", end=' ')
    print(*[{'index': index, 'found': best_combo, 'expected': test} for index, result, best_combo, test in
            zip(range(0, len(tests)), results, best_combos, tests) if not result], sep='\n')


def test_improve_monster_from_ai_hand_and_board(cur, tests):
    results = []
    best_combos = []
    for index, test in enumerate(tests):
        monster_board = test.get('monster_board')
        if monster_board is not None:
            for board_card in monster_board:
                if board_card is not None:
                    board_card_name, board_card_pos, board_card_equip_level = board_card['name'], board_card['pos'], \
                                                                              board_card['equip_stage']
                    board_card_id = get_card_id_from_name(cur, board_card_name)
                    if board_card_name is not None and board_card_id is None:
                        raise ValueError(f"{index}. Couldn't find id of board card name '{board_card_name}'.")
                    board_card['id'] = board_card_id

        hand_names = test['hand_names']
        max_improve_length = test['max_improve_length']
        field = test['field'] if 'field' in test else None

        exp_ordering = test.get('exp_ordering')
        exp_result_name = test.get('exp_result_name')
        exp_result_id = get_card_id_from_name(cur, exp_result_name)
        if exp_result_name is not None and exp_result_id is None:
            raise ValueError(f"{index}. Couldn't find id of expected card name '{exp_result_name}'.")
        exp_equip_stage = test.get('exp_equip_stage')
        exp_result_max_stat = test.get('exp_result_max_stat')

        hand = [get_card_id_from_name(cur, card_name) for card_name in hand_names]
        if None in hand:
            raise ValueError(f"{index}. Couldn't find id of certain card names.\n{hand}, {hand_names}")

        action = improve_monster_from_ai_board_and_hand(cur, hand, monster_board=monster_board, field=field,
                                                        max_improve_length=max_improve_length)
        best_combos.append(action)

        actual_tests = [x for x in [exp_ordering, exp_result_id, exp_equip_stage, exp_result_max_stat] if x is not None]

        is_passed = True
        for actual_test in actual_tests:
            # if actual_test == exp_ordering:
            for (res_pos, exp_pos) in zip(actual_test, action.descriptions):
                is_passed &= res_pos == exp_pos
            # elif actual_test == exp_result_id:
            #     is_passed &= exp_result_id == action.result_id
            # elif actual_test == exp_equip_stage:
            #     is_passed &= exp_equip_stage == action.equip_stage
            # elif actual_test == exp_result_max_stat:
            #     is_passed &= exp_result_max_stat == action.result_max_stat

        results.append(is_passed)

    print(f"Successes: {len(list(filter(None, results)))} / {len(results)} :Total")
    print(f"Differences :", end=' ')
    print(*[{'index': index, 'found': best_combo, 'expected': test} for index, result, best_combo, test in
            zip(range(0, len(tests)), results, best_combos, tests) if not result], sep='\n')


def test_all_hand_ai_subfunctions(cur):
    tests_find_best_combo_in_ai_hand = [
        {  # 1-card combo
            'board_card': None,
            'hand_names': [
                'Gate Guardian',
                'Blue-eyes Ultimate Dragon',
                'Zera The Mant',
                'Cosmo Queen',
                'Blue-eyes Ultimate Dragon',
            ],
            'field': None,
            'max_fusion_length': 3,
            'exp_result_name': 'Blue-eyes Ultimate Dragon',
            'exp_ordering': [1],
            'exp_equip_stage': 0,
            'exp_result_max_stat': 4_500
        },
        {  # 1-card combo, field shouldn't matter (.1)
            'board_card': None,
            'hand_names': [
                'Twin-headed Thunder Dragon',
                'Dark Magician',
                'Zera The Mant',
                'Cosmo Queen',
                'B. Skull Dragon',
            ],
            'field': 'Yami',
            'max_fusion_length': 3,
            'exp_result_name': 'B. Skull Dragon',
            'exp_ordering': [4],
            'exp_equip_stage': 0,
            'exp_result_max_stat': 3_200
        },
        {  # 1-card combo, field shouldn't matter (.2)
            'board_card': None,
            'hand_names': [
                'Twin-headed Thunder Dragon',
                'Dark Magician',
                'Zera The Mant',
                'B. Skull Dragon',
                'Cosmo Queen',
            ],
            'field': 'Umi',
            'max_fusion_length': 3,
            'exp_result_name': 'B. Skull Dragon',
            'exp_ordering': [3],
            'exp_equip_stage': 0,
            'exp_result_max_stat': 3_200
        },
        {  # 2-card combo, field shouldn't matter (.2)
            'board_card': None,
            'hand_names': [
                'Twin-headed Thunder Dragon',
                'Dark Magician',
                'Zera The Mant',
                'B. Skull Dragon',
                'Cosmo Queen',
            ],
            'field': 'Umi',
            'max_fusion_length': 3,
            'exp_result_name': 'B. Skull Dragon',
            'exp_ordering': [3],
            'exp_equip_stage': 0,
            'exp_result_max_stat': 3_200
        },
        {  # 3-card combo
            'board_card': None,
            'hand_names': [
                'Flame Ghost',
                'Petit Dragon',
                'Niwatori',
                'Air Marmot of Nefariousness',
                'Niwatori',
            ],
            'field': None,
            'max_fusion_length': 3,
            'exp_result_name': 'Crimson Sunbird',
            'exp_ordering': [0, 2, 4],
            'exp_equip_stage': 0,
            'exp_result_max_stat': 2_300
        },
        {  # 2-card combo due to max_fusion_length being reached
            'board_card': None,
            'hand_names': [
                'Flame Ghost',
                'Petit Dragon',
                'Niwatori',
                'Air Marmot of Nefariousness',
                'Niwatori',
            ],
            'field': None,
            'max_fusion_length': 2,
            'exp_result_name': 'Flame Cerebrus',
            'exp_ordering': [0, 3],
            'exp_equip_stage': 0,
            'exp_result_max_stat': 2_100
        },
        {  # Equip due to 2-card combo having priority over 1-card combo thanks to earlier card
            'board_card': None,
            'hand_names': [
                'Megamorph',
                'Gate Guardian',
                'Turtle Tiger',
                'Niwatori',
                'Firegrass',
            ],
            'field': None,
            'max_fusion_length': 3,
            'exp_result_name': 'Gate Guardian',
            'exp_ordering': [0, 1],
            'exp_equip_stage': 2,
            'exp_result_max_stat': 3_750
        },
        {  # No equip due to 2-card & 3-card combos comparison
            'board_card': None,
            'hand_names': [
                'Megamorph',
                'Mavelus',
                'Turtle Tiger',
                'Niwatori',
                'Firegrass',
            ],
            'field': None,
            'max_fusion_length': 3,
            'exp_result_name': 'Crimson Sunbird',
            'exp_ordering': [1, 3],
            'exp_equip_stage': 0,
            'exp_result_max_stat': 2_300
        },
        {  # Equip thanks to field
            'board_card': None,
            'hand_names': [
                'Cosmo Queen',
                'B. Skull Dragon',
                'Megamorph',
                'Megamorph',
                'Zoa',
            ],
            'field': 'Yami',
            'max_fusion_length': 3,
            'exp_result_name': 'Cosmo Queen',
            'exp_ordering': [0, 2],
            'exp_equip_stage': 2,
            'exp_result_max_stat': 3_400
        },
        {  # Equip from field combo
            'board_card': None,
            'hand_names': [
                'Zoa',
                'Yami',
                'Skull Knight',
                'Twin-headed Thunder Dragon',
                'Yami',
            ],
            'field': None,
            'max_fusion_length': 3,
            'exp_result_name': 'Twin-headed Thunder Dragon',
            'exp_ordering': [1, 4, 3],
            'exp_equip_stage': 1,
            'exp_result_max_stat': 2_800
        },
        {  # Equip from field combo and field
            'board_card': None,
            'hand_names': [
                'Twin-headed Thunder Dragon',
                'Skull Knight',
                'Zoa',
                'Yami',
                'Yami',
            ],
            'field': 'Yami',
            'max_fusion_length': 3,
            'exp_result_name': 'Skull Knight',
            'exp_ordering': [3, 4, 1],
            'exp_equip_stage': 1,
            'exp_result_max_stat': 3_150
        },
        {  # Different equip from field combo
            'board_card': None,
            'hand_names': [
                'Twin-headed Thunder Dragon',
                'Skull Knight',
                'Zoa',
                'Yami',
                'Yami',
            ],
            'field': None,
            'max_fusion_length': 3,
            'exp_result_name': 'Twin-headed Thunder Dragon',
            'exp_ordering': [0],
            'exp_equip_stage': 0,
            'exp_result_max_stat': 2_800
        },

        {  # Board fusion with no ambiguity
            'board_card': {'name': 'Skull Red Bird', 'pos': 0, 'equip_stage': 0},
            'hand_names': [
                'Armed Ninja',
                'Petit Dragon',
                'Vermillion Sparrow',
                'Tripwire Beast',
                'Ameba',
            ],
            'field': None,
            'max_fusion_length': 2,
            'exp_result_name': 'Crimson Sunbird',
            'exp_ordering': [encode_frontrow_pos(0), 2],
            'exp_equip_stage': 0,
            'exp_result_max_stat': 2_300
        },
        {  # Board fusion with 3-card hand combo ambiguity
            'board_card': {'name': 'Skull Red Bird', 'pos': 0, 'equip_stage': 0},
            'hand_names': [
                'Armed Ninja',
                'Petit Dragon',
                'Vermillion Sparrow',
                'Tripwire Beast',
                'Ameba',
            ],
            'field': None,
            'max_fusion_length': 3,
            'exp_result_name': 'Crimson Sunbird',
            'exp_ordering': [encode_frontrow_pos(0), 2],
            'exp_equip_stage': 0,
            'exp_result_max_stat': 2_300
        },

        {  # Keep board card as is
            'board_card': {'name': 'Blue-eyes White Dragon', 'pos': 0, 'equip_stage': 0},
            'hand_names': [
                'Armed Ninja',
                'Bright Castle',
                'Vermillion Sparrow',
                'Tripwire Beast',
                'Ameba',
            ],
            'field': None,
            'max_fusion_length': 3,
            'exp_result_name': 'Blue-eyes White Dragon',
            'exp_ordering': [encode_frontrow_pos(0)],
            'exp_equip_stage': 0,
            'exp_result_max_stat': 3_000
        },
        {  # Improve board card
            'board_card': {'name': 'Blue-eyes White Dragon', 'pos': 0, 'equip_stage': -1},
            'hand_names': [
                'Armed Ninja',
                'Bright Castle',
                'Vermillion Sparrow',
                'Tripwire Beast',
                'Ameba',
            ],
            'field': None,
            'max_fusion_length': 2,
            'exp_result_name': 'Blue-eyes White Dragon',
            'exp_ordering': [encode_frontrow_pos(0), 1],
            'exp_equip_stage': 0,
            'exp_result_max_stat': 3_000
        },

        {  # No combo due to hand and board cards having the same position
            'board_card': {'name': 'Blue-eyes White Dragon', 'pos': 0, 'equip_stage': -1},
            'hand_names': [
                'Bright Castle',
                'Armed Ninja',
                'Vermillion Sparrow',
                'Tripwire Beast',
                'Ameba',
            ],
            'field': None,
            'max_fusion_length': 2,
            'exp_result_name': 'Blue-eyes White Dragon',
            'exp_ordering': [encode_frontrow_pos(0)],
            'exp_equip_stage': -1,
            'exp_result_max_stat': 2_500
        },

        {  # Classic DarkNite hand
            'board_card': None,
            'hand_names': [
                'Forest', 'Crush Card', 'Umi', 'Crush Card', 'Sogen',
                'Yami', 'Cosmo Queen', 'King of Yamimakai', 'Nekogal #2', 'Forest',
                'Forest', 'Umi', 'Swords of Revealing Light', 'Shadow Spell', 'Tremendous Fire',
                'Wasteland', 'Umi', 'Stop Defense', 'Nekogal #2', 'Yami'
            ],
            'field': None,
            'max_fusion_length': 3,
            'exp_result_name': 'Cosmo Queen',
            'exp_ordering': [6],
            'exp_equip_stage': 0,
            'exp_result_max_stat': 2_900
        },
        {  # Classic DarkNite hand
            'board_card': None,
            'hand_names': [
                'Forest', 'Crush Card', 'Umi', 'Crush Card', 'Sogen',
                'Yami', 'Cosmo Queen', 'King of Yamimakai', 'Nekogal #2', 'Forest',
                'Forest', 'Umi', 'Swords of Revealing Light', 'Shadow Spell', 'Tremendous Fire',
                'Wasteland', 'Umi', 'Stop Defense', 'Nekogal #2', 'Megamorph'
            ],
            'field': 'Yami',
            'max_fusion_length': 3,
            'exp_result_name': 'Cosmo Queen',
            'exp_ordering': [6, 19],
            'exp_equip_stage': 2,
            'exp_result_max_stat': 3_400
        },
        {  # Classic Pegasus hand
            'board_card': None,
            'hand_names': [
                'Rude Kaiser', 'Koumori Dragon', 'Bright Castle', 'Dragon Capture Jar', 'Dragon Capture Jar',
                'Monster Tamer', 'Yamadron', 'Yamadron', 'Raigeki', 'Crow Goblin',
                'Crow Goblin', 'Crow Goblin', 'Meteor Dragon', 'Battle Ox', 'Solitude',
                'Koumori Dragon'
            ],
            'field': None,
            'max_fusion_length': 4,
            'exp_result_name': 'Crimson Sunbird',
            'exp_ordering': [6, 9],
            'exp_equip_stage': 0,
            'exp_result_max_stat': 2_300
        }

    ]
    test_find_best_combo_in_ai_hand(cur, tests_find_best_combo_in_ai_hand)

    tests_find_best_combo_in_ai_hand_and_board = [
        {  # Classic DarkNite hand
            'monster_board': None,
            'hand_names': [
                'Forest', 'Crush Card', 'Umi', 'Crush Card', 'Sogen',
                'Yami', 'Cosmo Queen', 'King of Yamimakai', 'Nekogal #2', 'Forest',
                'Forest', 'Umi', 'Swords of Revealing Light', 'Shadow Spell', 'Tremendous Fire',
                'Wasteland', 'Umi', 'Stop Defense', 'Nekogal #2', 'Yami'
            ],
            'field': None,
            'max_fusion_length': 3,
            'exp_result_name': 'Cosmo Queen',
            'exp_ordering': [6],
            'exp_equip_stage': 0,
            'exp_result_max_stat': 2_900
        },
        {  # Classic Heishin 1
            'monster_board': [
                {
                    'name': 'Twin-headed Thunder Dragon',
                    'pos': 0,
                    'equip_stage': 0
                }
            ],
            'hand_names': [
                'Stone D.', 'Gaia the Dragon Champion', 'Dark Magician', 'Skull Knight', 'Great Moth',
                'Thousand Dragon', 'Launcher Spider', 'Megamorph', 'Launcher Spider', 'Skull Guardian',
                'Raigeki', 'Twin-headed Thunder Dragon', 'Sengenjin', 'Sanga of the Thunder', 'Tremendous Fire',
                'Stone D.', 'Zoa', 'Garma Sword', "Harpie's Feather Duster", 'Twin-headed Thunder Dragon'
            ],
            'field': 'Yami',
            'max_fusion_length': ai_stats['Heishin'].max_fusion_length,
            'exp_result_name': 'Skull Knight',
            'exp_ordering': [3, 7],
            'exp_equip_stage': 2,
            'exp_result_max_stat': 3_150
        },
        {  # Board equip
            'monster_board': [
                {
                    'name': 'Skull Knight',
                    'pos': 0,
                    'equip_stage': -1
                }
            ],
            'hand_names': [
                'Stone D.', 'Gaia the Dragon Champion', 'Dark Magician', 'Skull Knight', 'Great Moth',
                'Thousand Dragon', 'Launcher Spider', 'Zoa', 'Launcher Spider', 'Skull Guardian',
                'Raigeki', 'Garma Sword', 'Sengenjin', 'Sanga of the Thunder', 'Tremendous Fire',
                'Stone D.', 'Zoa', 'Garma Sword', "Harpie's Feather Duster", 'Megamorph'
            ],
            'field': 'Yami',
            'max_fusion_length': ai_stats['Heishin'].max_fusion_length,
            'exp_result_name': 'Skull Knight',
            'exp_ordering': [encode_frontrow_pos(0), 19],
            'exp_equip_stage': 1,
            'exp_result_max_stat': 3_150
        }
    ]
    test_find_best_combo_in_ai_hand_and_board(cur, tests_find_best_combo_in_ai_hand_and_board)

    tests_improve_monster_from_ai_hand = [
        {  # Classic Mai Valentine
            'board_card': {
                'name': 'Fairy of the Fountain',
                'pos': 3,
                'equip_stage': 0
            },
            'hand_names': [
                'Tyhone', 'Tyhone', 'Faith Bird', 'Harpie Lady', 'Celtic Guardian',
                'Malevolent Nuzzler', 'Fiend Kraken', 'Faith Bird', 'Koumori Dragon', 'Blue-winged Crown'
            ],
            'field': None,
            'max_improve_length': ai_stats['Heishin'].max_improve_length,
            'exp_result_name': "Harpie's Pet Dragon",
            'exp_ordering': [encode_frontrow_pos(3), 8, 3],
            'exp_equip_stage': 0,
            'exp_result_max_stat': 2_500
        },
        {  # Classic Isis
            'board_card': {
                'name': 'Yamadron',
                'pos': 2,
                'equip_stage': 0
            },
            'hand_names': [
                'Petit Dragon', 'Umi', 'Spellbinding Circle', 'Catapult Turtle', 'Kanikabuto',
                'Swords of Revealing Light', "Harpie's Feather Duster", 'Umi', 'Root Water', 'The Furious Sea King',
                'High Tide Gyojin', 'White Dolphin', 'Ice Water', 'Psychic Kappa', 'Catapult Turtle',
                'Fire Kraken'
            ],
            'field': None,
            'max_improve_length': ai_stats['Isis'].max_improve_length,
            'exp_result_name': "Sea King Dragon",
            'exp_ordering': [encode_frontrow_pos(2), 3, 14],
            'exp_equip_stage': 0,
            'exp_result_max_stat': 2_000
        },
    ]
    test_improve_monster_from_ai_hand(cur, tests_improve_monster_from_ai_hand)

    tests_improve_monster_from_ai_hand_and_board = [
        {  # Classic Heishin 2 no improvement
            'monster_board': [
                {
                    'name': 'Gate Guardian',
                    'pos': 0,
                    'equip_stage': 0
                },
                {
                    'name': 'Meteor B. Dragon',
                    'pos': 1,
                    'equip_stage': 0
                },
            ],
            'hand_names': [
                'Mystical Sand', 'Bracchio-raidus', 'Labyrinth Wall', 'Raigeki', 'Raigeki',
                'Right Arm of the Forbidden One', "Cosmo Queen's Prayer", 'Spirit of the Mountain',
                "Cosmo Queen's Prayer", 'Thousand Dragon',
                'Blue-eyes White Dragon', 'Right Leg of the Forbidden One', 'B. Skull Dragon', 'Bickuribox',
                'Megamorph',
                'Megamorph', 'Labyrinth Wall', "Harpie's Feather Duster", 'Metalzoa', 'Gate Guardian'
            ],
            'field': 'Yami',
            'max_improve_length': ai_stats['Heishin 2nd'].max_improve_length,
            # 'exp_result_name': None,
            # 'exp_result_name': 'Skull Knight',
            'exp_ordering': None
            # 'exp_equip_stage': 2,
            # 'exp_result_max_stat': 3_150
        },
        {  # Kaiba lower combo due to considering board cards from lowest to highest true max stat
            'monster_board': [
                {
                    'name': 'Thousand Dragon',
                    'pos': 0,
                    'equip_stage': 0
                },
                {
                    'name': 'Parrot Dragon',
                    'pos': 1,
                    'equip_stage': 0
                },
            ],
            'hand_names': [
                'Saggi the Dark Clown', 'Battle Steer', 'Peacock', 'Zanki', 'Ocubeam',
                'Megasonic Eye', 'Ultimate Dragon', 'Crush Card', 'Guardian of the Throne Room', 'Crawling Dragon',
                'Doma The Angel of Silence', 'Gatekeeper', 'Queen of Autumn Leaves', 'Ocubeam', 'Misairuzame',
                'Kaminari Attack'],
            'field': None,
            'max_improve_length': ai_stats['Kaiba'].max_improve_length,
            'exp_result_name': 'Twin-headed Thunder Dragon',
            'exp_ordering': [encode_frontrow_pos(1), 15],
            'exp_equip_stage': 0,
            'exp_result_max_stat': 2_800
        },
        {  # Kaiba same result, order doesn't matter
            'monster_board': [
                {
                    'name': 'Thousand Dragon',
                    'pos': 1,
                    'equip_stage': 0
                },
                {
                    'name': 'Parrot Dragon',
                    'pos': 0,
                    'equip_stage': 0
                },
            ],
            'hand_names': [
                'Saggi the Dark Clown', 'Battle Steer', 'Peacock', 'Zanki', 'Ocubeam',
                'Megasonic Eye', 'Ultimate Dragon', 'Crush Card', 'Guardian of the Throne Room', 'Crawling Dragon',
                'Doma The Angel of Silence', 'Gatekeeper', 'Queen of Autumn Leaves', 'Ocubeam', 'Misairuzame',
                'Kaminari Attack'
            ],
            'field': None,
            'max_improve_length': ai_stats['Kaiba'].max_improve_length,
            'exp_result_name': 'Twin-headed Thunder Dragon',
            'exp_ordering': [encode_frontrow_pos(0), 15],
            'exp_equip_stage': 0,
            'exp_result_max_stat': 2_800
        },

        {  # Shadi lower improve due to improving the least powerful card first
            'monster_board': [
                {
                    'name': 'Yamatano Dragon Scroll',
                    'pos': 0,
                    'equip_stage': 0
                },
                {
                    'name': 'Tomozaurus',
                    'pos': 1,
                    'equip_stage': 0
                },
            ],
            'hand_names': [
                'Star Boy', "Hiro's Shadow Scout", 'Boo Koo', 'Hinotama Soul', 'Wretched Ghost of the Attic',
                'Tentacle Plant', 'Weather Control', 'Air Marmot of Nefariousness', 'Mechanical Spider',
                'Air Marmot of Nefariousness',
                'LaLa Li-oon', 'Muka Muka'
            ],
            'field': None,
            'max_improve_length': ai_stats['Shadi'].max_improve_length,
            'exp_result_name': 'Cyber Saurus',
            'exp_ordering': [encode_frontrow_pos(1), 8],
            'exp_equip_stage': 0,
            'exp_result_max_stat': 1_800
        },

    ]
    test_improve_monster_from_ai_hand_and_board(cur, tests_improve_monster_from_ai_hand_and_board)
