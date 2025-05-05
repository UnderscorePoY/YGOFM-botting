import itertools

import ai
import ai_board
import ai_hand
from ai_hand import *
from utils import *


# Hand AI main function

FRONTROW, BACKROW = 0, 1


tests_hand_ai = [
        # 1. Direct kill
        {
            'description': 'Direct kill > Sparks',
            'player': {
                'backrow': [None] * 5,
                'LP': 50,
            },
            'ai_player': {
                'name': 'DarkNite',
                'hand_names': ['Sparks', 'Hinotama', 'Final Flame', 'Ookazi', 'Tremendous Fire'],
            },
            'expected_combo': [
                Action([(0, FACE_UP)])
            ]
        },
        {
            'description': 'Direct kill > Hinotama',
            'player': {
                'backrow': [None]*5,
                'LP': 100,
            },
            'ai_player': {
                'name': 'DarkNite',
                'hand_names': ['Sparks', 'Final Flame', 'Ookazi', 'Tremendous Fire', 'Hinotama'],
            },
            'expected_combo': [
                Action([(4, FACE_UP)])
            ]
        },
        {
            'description': 'Direct kill > Final Flame',
            'player': {
                'backrow': [None]*5,
                'LP': 180,
            },
            'ai_player': {
                'name': 'DarkNite',
                'hand_names': ['Sparks', 'Final Flame', 'Ookazi', 'Tremendous Fire', 'Hinotama'],
            },
            'expected_combo': [
                Action([(1, FACE_UP)])
            ]
        },
        {
            'description': 'Direct kill > Ookazi',
            'player': {
                'backrow': [None]*5,
                'LP': 300,
            },
            'ai_player': {
                'name': 'DarkNite',
                'hand_names': ['Tremendous Fire', 'Ookazi', 'Sparks', 'Final Flame', 'Hinotama'],
            },
            'expected_combo': [
                Action([(1, FACE_UP)])
            ]
        },
        {
            'description': 'Direct kill > Tremendous Fire',
            'player': {
                'backrow': [None]*5,
                'LP': 700,
            },
            'ai_player': {
                'name': 'DarkNite',
                'hand_names': ['Ookazi', 'Sparks', 'Final Flame', 'Tremendous Fire', 'Hinotama'],
            },
            'expected_combo': [
                Action([(3, FACE_UP)])
            ]
        },
        {
            'description': 'Direct kill > No direct damage due to player backrow',
            'player': {
                'frontrow': [{'name': 'Twin-headed Thunder Dragon'}, None, None, None, None],
                'backrow': [{'name': 'Raigeki'}, None, None, None, None],
                'LP': 700,
            },
            'ai_player': {
                'name': 'DarkNite',
                'frontrow': [None, None, None, None, None],
                'hand_names': ['Ookazi', 'Sparks', 'Final Flame', 'Tremendous Fire', 'Hinotama', 'Doron'],
            },
            'expected_combo': [
                Action([(5, FACE_DOWN)])
            ]
        },

        # 2. Force fields
        {
            'description': 'Force fields > Ocean Mage',
            'ai_player': {
                'name': 'Ocean Mage',
                'hand_names': ['Sea King Dragon', 'Umi'],
            },
            'field': None,
            'expected_combo': [
                Action([(1, FACE_UP)])
            ]
        },
        {
            'description': 'Force fields > Mountain Mage',
            'ai_player': {
                'name': 'Mountain Mage',
                'hand_names': ['Mountain', 'Punished Eagle'],
            },
            'field': None,
            'expected_combo': [
                Action([(0, FACE_UP)])
            ]
        },
        {
            'description': 'Force fields > Desert Mage',
            'ai_player': {
                'name': 'Desert Mage',
                'hand_names': ['Wasteland', 'Crawling Dragon #2'],
            },
            'field': None,
            'expected_combo': [
                Action([(0, FACE_UP)])
            ]
        },
        {
            'description': 'Force fields > Meadow Mage',
            'ai_player': {
                'name': 'Meadow Mage',
                'hand_names': ['Sogen', 'Empress Judge'],
            },
            'field': None,
            'expected_combo': [
                Action([(0, FACE_UP)])
            ]
        },
        {
            'description': 'Force fields > Forest Mage',
            'ai_player': {
                'name': 'Forest Mage',
                'hand_names': ['Forest', 'Hercules Beetle'],
            },
            'field': None,
            'expected_combo': [
                Action([(0, FACE_UP)])
            ]
        },
        {
            'description': 'Force fields > Guardian Neku',
            'ai_player': {
                'name': 'Guardian Neku',
                'hand_names': ['Yami', 'Skull Knight'],
            },
            'field': 'Umi',
            'expected_combo': [
                Action([(0, FACE_UP)])
            ]
        },

        # 3a1. Regain control with a single monster
        {
            'description': 'Regain control with a single monster > Empty AI frontrow',
            'player': {
                'frontrow': [{'name': 'Mystical Sand'}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Pegasus',
                'frontrow': [None] * 5,
                'hand_names': ['Parrot Dragon', 'Flame Swordsman'],
            },
            'expected_combo': [
                Action([(0, FACE_DOWN)])
            ]
        },
        {
            'description': 'Regain control with a single monster > Best monster in hand beats best player monster',
            'player': {
                'frontrow': [{'name': 'Mystical Sand'}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Pegasus',
                'frontrow': [{'name': 'Parrot Dragon'}, None, None, None, None],
                'hand_names': ['Parrot Dragon', 'Bickuribox'],
            },
            'expected_combo': [
                Action([(1, FACE_DOWN)])
            ]
        },

        # 3a2. Regain control with magic/trap
        {
            'description': 'Regain control with magic/trap > Counter player type',
            'player': {
                'frontrow': [{'name': 'B. Dragon Jungle King'}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Pegasus',
                'frontrow': [{'name': 'Parrot Dragon'}, None, None, None, None],
                'hand_names': ['Parrot Dragon', 'Dragon Capture Jar'],
            },
            'current_ai_turn': 4,
            'expected_combo': [
                Action([(1, FACE_UP)])
            ]
        },
        {
            'description': 'Regain control with magic/trap > Decrease stats (Spellbinding Circle)',
            'player': {
                'frontrow': [{'name': 'B. Dragon Jungle King', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Yami Bakura',
                'frontrow': [{'name': 'Aqua Madoor'}, None, None, None, None],
                'hand_names': ['Aqua Madoor', 'Aqua Madoor', 'Spellbinding Circle'],
            },
            'current_ai_turn': 4,
            'expected_combo': [
                Action([(2, FACE_UP)])
            ]
        },
        {
            'description': 'Regain control with magic/trap > Decrease stats (Shadow Spell)',
            'player': {
                'frontrow': [{'name': 'B. Dragon Jungle King', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Kaiba',
                'frontrow': [{'name': 'Aqua Madoor'}, None, None, None, None],
                'hand_names': ['Queen Bird', 'Shadow Spell'],
            },
            'current_ai_turn': 4,
            'expected_combo': [
                Action([(1, FACE_UP)])
            ]
        },
        {
            'description': 'Regain control with magic/trap > Destroy monsters (Crush Card)',
            'player': {
                'frontrow': [{'name': 'B. Dragon Jungle King', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Kaiba',
                'frontrow': [{'name': 'Aqua Madoor'}, None, None, None, None],
                'hand_names': ['Reaper of the Cards', 'Crush Card'],
            },
            'current_ai_turn': 4,
            'expected_combo': [
                Action([(1, FACE_UP)])
            ]
        },
        {
            'description': 'Regain control with magic/trap > Destroy monsters (Raigeki)',
            'player': {
                'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'High Mage Secmeton',
                'frontrow': [{'name': 'Aqua Dragon'}, None, None, None, None],
                'hand_names': ['Aqua Dragon', 'Raigeki'],
            },
            'current_ai_turn': 4,
            'expected_combo': [
                Action([(1, FACE_UP)])
            ]
        },
        {
            'description': 'Regain control with magic/trap > Traps (Widespread Ruins)',
            'player': {
                'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [{'name': 'Aqua Dragon'}, None, None, None, None],
                'hand_names': ['Aqua Dragon', 'Fake Trap',
                               'House of Adhesive Tape', 'Eatgaboon', 'Bear Trap',
                               'Invisible Wire', 'Acid Trap Hole', 'Widespread Ruin'],
            },
            'current_ai_turn': 4,
            'expected_combo': [
                Action([(7, FACE_DOWN)])
            ]
        },
        {
            'description': 'Regain control with magic/trap > Swords of Revealing Light',
            'player': {
                'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'High Mage Secmeton',
                'frontrow': [{'name': 'Aqua Dragon'}, None, None, None, None],
                'hand_names': ['Aqua Dragon', 'Swords of Revealing Light'],
            },
            'current_ai_turn': 4,
            'expected_combo': [
                Action([(1, FACE_UP)])
            ]
        },
        {
            'description': 'Regain control with magic/trap > Dark Hole',
            'player': {
                'frontrow': [
                    {'name': 'Twin-headed Thunder Dragon', 'face': FACE_UP},
                    {'name': 'Twin-headed Thunder Dragon', 'face': FACE_UP},
                    None,
                    None,
                    None
                ],
            },
            'ai_player': {
                'name': 'Mai Valentine',
                'frontrow': [{'name': "Harpie's Pet Dragon"}, None, None, None, None],
                'hand_names': ['Harpie Lady Sisters', 'Dark Hole'],
            },
            'current_ai_turn': 4,
            'expected_combo': [
                Action([(1, FACE_UP)])
            ]
        },

        # 3a3.Regain control with a combo
        {
            'description': 'Regain control with a combo > Only cards from hand',
            'player': {
                'frontrow': [{'name': 'B. Dragon Jungle King'}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Pegasus',
                'frontrow': [{'name': "Parrot Dragon"}, None, None, None, None],
                'hand_names': ['Vermillion Sparrow', 'Crow Goblin'],
            },
            'expected_combo': [
                Action([(0, FACE_UP), (1, FACE_UP)])
            ]
        },
        {
            'description': 'Regain control with a combo > Monster + magic bug',
            'player': {
                'frontrow': [{'name': 'B. Dragon Jungle King', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Meadow Mage',
                'frontrow': [{'name': "Zanki"}, None, None, None, None],
                'hand_names': ['Warrior Elimination', 'Flame Swordsman'],
            },
            'field': 'Wasteland',
            'expected_combo': [
                Action([(0, FACE_UP)])
            ]
        },
        {
            'description': 'Regain control with a combo > No combo play (SET_MAGIC trap) / '
                           'No Dragon Capture Jar due to turn < 4',
            'player': {
                'frontrow': [{'name': 'B. Dragon Jungle King'}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Pegasus',
                'frontrow': [None] * 5,
                'backrow': [None] * 5,
                'hand_names': ['Dragon Capture Jar', 'Bright Castle', 'Invisible Wire'],
            },
            'current_ai_turn': 3,
            'expected_combo': [
                Action([(2, FACE_DOWN)])
            ]
        },
        {
            'description': 'Regain control with a combo > No combo play (SET_MAGIC equip) / '
                           'No Dragon Capture Jar due to turn < 4',
            'player': {
                'frontrow': [{'name': 'B. Dragon Jungle King'}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Pegasus',
                'frontrow': [None] * 5,
                'backrow': [None] * 5,
                'hand_names': ['Dragon Capture Jar', 'Bright Castle'],
            },
            'expected_combo': [
                Action([(1, FACE_DOWN)])
            ]
        },
        {
            'description': 'Regain control with a combo > No combo play (SET_MAGIC magic)',
            'player': {
                'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Desert Mage',
                'frontrow': [None] * 5,
                'backrow': [None] * 5,
                'hand_names': ['Revival of Skeleton Rider', 'Eternal Rest'],
            },
            'expected_combo': [
                Action([(1, FACE_DOWN)])
            ]
        },
        {
            'description': 'Regain control with a combo > Doing nothing to a monster from the board '
                           '-> compatible field',
            'player': {
                'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'High Mage Kepura',
                'frontrow': [{'name': 'Gaia the Fierce Knight'}, None, None, None, None],
                'hand_names': ['Judge Man', 'Sogen'],
            },
            'field': None,
            'expected_combo': [
                Action([(1, FACE_UP)])
            ]
        },
        {
            'description': 'Regain control with a combo > Fallback : best max stat in hand',
            'player': {
                'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'High Mage Kepura',
                'frontrow': [{'name': 'Gaia the Fierce Knight'}, None, None, None, None],
                'hand_names': ['Flame Swordsman', 'Judge Man'],
            },
            'expected_combo': [
                Action([(1, FACE_DOWN)])
            ]
        },
        {
            'description': 'Regain control with a combo > Fallback² : no monsters',
            'player': {
                'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'High Mage Kepura',
                'frontrow': [{'name': 'Gaia the Fierce Knight'}, None, None, None, None],
                'backrow': [None] * 5,
                'hand_names': ['Zera Ritual', 'Bear Trap', 'Gate Guardian Ritual',
                               'Eternal Draught', 'Winged Trumpeter'],
            },
            'expected_combo': [
                Action([(0, FACE_DOWN)], odds=(1, 5)),
                Action([(1, FACE_DOWN)], odds=(1, 5)),
                Action([(2, FACE_DOWN)], odds=(1, 5)),
                Action([(3, FACE_DOWN)], odds=(1, 5)),
                Action([(4, FACE_DOWN)], odds=(1, 5))
            ]
        },

        # 3b. The AI thinks it has field control
        # 3b1. Clear player's backrow
        {
            'description': "AI thinks it has field control > Clear player's backrow "
                           "TOTAL_DOMINATION (40/30/30)",
            'player': {
                'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': FACE_UP}, None, None, None, None],
                'backrow': [{'name': 'Widespread Ruin', 'face': FACE_DOWN}, None, None, None, None],
            },
            'ai_player': {
                'name': 'High Mage Kepura',
                'frontrow': [{'name': 'Gate Guardian'}, None, None, None, None],
                'backrow': [None, None, None, None, None],
                'hand_names': ['Flame Swordsman', 'Judge Man', "Harpie's Feather Duster",
                               'Sword of Dark Destruction', 'Sogen'],
                'LP': 8_000
            },
            'field': None,
            'expected_combo': [
                Action([(2, FACE_UP)], odds=(50, 100)),
                Action(odds=(50, 100), _next=[
                    Action([(4, FACE_UP)], odds=(40, 100)),  # IMPROVE_MONSTER
                    Action([(4, FACE_UP)], odds=(30, 100)),  # FIND_BEST_COMBO
                    Action([(3, FACE_DOWN)], odds=(30, 100))  # SET_MAGIC
                ])
            ]
        },
        {
            'description': "AI thinks it has field control > Clear player's backrow "
                           'LACKS_TOTAL_DOMINATION (20/60/20)',
            'player': {
                'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': FACE_UP}, None, None, None, None],
                'backrow': [{'name': 'Widespread Ruin', 'face': FACE_DOWN}, None, None, None, None],
            },
            'ai_player': {
                'name': 'High Mage Kepura',
                'frontrow': [
                    {'name': 'Gate Guardian'},
                    {'name': 'Gaia the Dragon Champion'},
                    None,
                    None,
                    None
                ],
                'backrow': [None]*5,
                'hand_names': ['Flame Swordsman', 'Judge Man', "Harpie's Feather Duster",
                               'Sword of Dark Destruction', 'Sogen'],
                'LP': 8_000,
            },
            'field': None,
            'expected_combo': [
                Action([(2, FACE_UP)], odds=(50, 100)),
                Action(odds=(50, 100), _next=[
                    Action([(4, FACE_UP)], (20, 100)),  # IMPROVE_MONSTER
                    Action([(4, FACE_UP)], (60, 100)),  # FIND_BEST_COMBO
                    Action([(3, FACE_DOWN)], (20, 100))  # SET_MAGIC
                ])
            ]
        },

        # 3b2. Improve monster if low enough LP
        {
            'description': 'AI thinks it has field control > Improve monster if low enough LP',
            'player': {
                'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': FACE_UP}, None, None, None, None],
                'backrow': [{'name': 'Widespread Ruin', 'face': FACE_DOWN}, None, None, None, None],
                'hand_names': [],
                'remaining_deck_names': [],
                'LP': 8_000,
            },
            'ai_player': {
                'name': 'High Mage Kepura',
                'frontrow': [{'name': 'Gate Guardian'}, None, None, None, None],
                'backrow': [None] * 5,
                'hand_names': ['Flame Swordsman', 'Judge Man', "Gaia the Dragon Champion",
                               'Sword of Dark Destruction', 'Sogen'],
                'remaining_deck_names': [],
                'LP': 2_000,
            },
            'field': None,
            'expected_combo': [
                Action([(4, FACE_UP)])  # IMPROVE_MONSTER
            ]
        }
    ]


def test_hand_ai(cur, tests):
    results = []
    combos = []
    DEFAULT_CURRENT_AI_TURN = 1
    for index, test in enumerate(tests):
        player = test.get('player')
        ai_player = test['ai_player']
        field = test.get('field')
        current_ai_turn = test.get('current_ai_turn', DEFAULT_CURRENT_AI_TURN)

        # Translates card names on the board into their respective card id (monsters & backrow, both player and AI)
        for cards, row_type in itertools.chain.from_iterable([
            [
                (pl.get('frontrow'), FRONTROW),
                (pl.get('backrow'), BACKROW),
                (pl.get('hand_names'), None),
                (pl.get('remaining_deck_names'), None)
            ] if pl is not None else []
            for pl in [player, ai_player]
        ]):
            if cards is None or len(cards) == 0:
                continue
            for pos, card in enumerate(cards):
                if card is None:
                    continue
                board_card_name = card if row_type is None else card['name']
                board_card_id = get_card_id_from_name(cur, board_card_name)
                if board_card_name is not None and board_card_id is None:
                    raise ValueError(f"{index}. Couldn't find id of board card name '{board_card_name}'.")
                card = {} if not isinstance(card, dict) else card
                card['name'] = board_card_name
                card['id'] = board_card_id
                card['pos'] = encode_frontrow_pos(pos) if row_type == FRONTROW \
                              else encode_backrow_pos(pos) if row_type == BACKROW \
                              else pos
                if 'equip_stage' not in card and row_type == FRONTROW:
                    card['equip_stage'] = 0
                cards[pos] = card

        expected_combo = test['expected_combo']
        expected_combo_detailled = test.get('expected_combo_detailled')

        # Translates card names in hands into their respective card id (monsters & backrow, both player and AI)
        for pl in [player, ai_player]:
            if pl is None:
                continue
            pl['hand'] = pl.get('hand_names')
            pl['remaining_deck'] = pl.get('remaining_deck_names')

        is_passed = True
        try:
            combo = ai_hand.hand_ai(cur, player, ai_player, current_ai_turn, field=field)
        except Exception as e:
            print(test['description'])
            is_passed = False
            raise e
        else:
            combos.append(combo)

            actual_tests = [x for x in [expected_combo] if x is not None]

            for actual_test in actual_tests:
                if actual_test == expected_combo:
                    is_passed &= combo.actions == expected_combo
        finally:
            results.append(is_passed)

    print(f"Successes: {len(list(filter(None, results)))} / {len(results)} :Total")
    if any([not x for x in results]):
        print(f"Differences :", end=' ')
        print(
            *[{'index': index, 'description': test['description'], 'found': best_combo, 'expected': test['expected_combo']}
              for index, result, best_combo, test
              in zip(range(0, len(tests)), results, combos, tests)
              if not result],
            sep='\n'
        )


tests_board_ai = [
        {
            'description': 'End of turn',
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [None, None, None, None, None],
                'backrow': [None, None, None, None, None],
            },
            'expected_combo': None
        },

        # Backrow
        {
            'description': "No Harpie's due to player not having anything in backrow",
            'player': {
                'backrow': [None, None, None, None, None],
            },
            'ai_player': {
                'name': 'Pegasus',
                'backrow': [{'name': "Harpie's Feather Duster", 'is_active': True}, None, None, None, None],
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), DARKEN)]),
            ]
        },
        {
            'description': "Harpie's",
            'player': {
                'backrow': [{'name': 'Umi'}, None, None, None, None],
                'LP': 8_000,
            },
            'ai_player': {
                'name': 'Pegasus',
                'backrow': [{'name': "Harpie's Feather Duster", 'is_active': True}, None, None, None, None],
                'LP': 8_000,
            },
            'field': None,
            'expected_combo': [
                Action([(encode_backrow_pos(0), FACE_UP)], odds=(75, 100)),
                Action([(encode_backrow_pos(0), DARKEN)], odds=(25, 100))
            ]
        },
        {
            'description': 'No direct damage due to enemy_LP >= player_LP',
            'player': {
                'LP': 4_000,
            },
            'ai_player': {
                'name': 'Jono',
                'backrow': [
                    {'name': 'Tremendous Fire', 'is_active': True},
                    {'name': 'Ookazi', 'is_active': True},
                    {'name': 'Final Flame', 'is_active': True},
                    {'name': 'Hinotama', 'is_active': True},
                    {'name': 'Sparks', 'is_active': True}],
                'LP': 4_500,
            },
            'expected_combo': [
                Action([(encode_backrow_pos(4), DARKEN)]),
            ]
        },
        {
            'description': '100% direct damage due to low_LP <= enemy_LP < player_LP',
            'player': {
                'backrow': [None, None, None, None, None],
                'LP': 4_000,
            },
            'ai_player': {
                'name': 'Jono',
                'backrow': [
                    {'name': 'Tremendous Fire', 'is_active': True},
                    {'name': 'Ookazi', 'is_active': True},
                    {'name': 'Final Flame', 'is_active': True},
                    {'name': 'Hinotama', 'is_active': True},
                    {'name': 'Sparks', 'is_active': True}],
                'LP': 1_000,
            },
            'expected_combo': [
                Action([(encode_backrow_pos(4), FACE_UP)]),
            ]
        },
        {
            'description': 'Partial direct damage due to enemy_LP < low_LP and player backrow is not empty',
            'player': {
                'backrow': [{'name': 'Umi'}, None, None, None, None],
                'LP': 4_000,
            },
            'ai_player': {
                'name': 'Jono',
                'backrow': [
                    {'name': 'Tremendous Fire', 'is_active': True},
                    {'name': 'Ookazi', 'is_active': True},
                    {'name': 'Final Flame', 'is_active': True},
                    {'name': 'Hinotama', 'is_active': True},
                    {'name': 'Sparks', 'is_active': True}],
                'LP': 980,
            },
            'expected_combo': [
                Action([(encode_backrow_pos(4), FACE_UP)], odds=(75, 100)),
                Action([(encode_backrow_pos(4), DARKEN)], odds=(25, 100)),
            ]
        },
        {
            'description': 'Equip',
            'ai_player': {
                'name': 'Heishin',
                'frontrow': [None, {'name': 'B. Skull Dragon'}, {'name': 'Meteor B. Dragon'}, None, None],
                'backrow': [{'name': 'Megamorph', 'is_active': True}, None, None, None, None],
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), FACE_UP), (encode_frontrow_pos(1), FACE_UP)]),
            ]
        },
        {
            'description': 'Equip on first compatible monster',
            'ai_player': {
                'name': 'High Mage Kepura',
                'frontrow': [
                    {'name': 'Gate Guardian'},
                    {'name': 'Gaia the Fierce Knight'},
                    {'name': 'Gaia the Fierce Knight'},
                    None,
                    None],
                'backrow': [{'name': 'Legendary Sword', 'is_active': True}, None, None, None, None],
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), FACE_UP), (encode_frontrow_pos(1), FACE_UP)]),
            ]
        },
        {
            'description': 'No equip due to no compatibility',
            'ai_player': {
                'name': 'High Mage Kepura',
                'frontrow': [{'name': 'Gate Guardian'}, None, None, None, None],
                'backrow': [{'name': 'Legendary Sword', 'is_active': True}, None, None, None, None],
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), DARKEN)]),
            ]
        },
        {
            'description': 'Succesful ritual',
            'ai_player': {
                'name': 'Seto 3rd',
                'frontrow': [
                    {'name': 'Beaver Warrior'},
                    {'name': 'Gaia the Fierce Knight'},
                    {'name': 'Kuriboh'},
                    None,
                    None],
                'backrow': [{'name': 'Black Luster Ritual', 'is_active': True}, None, None, None, None],
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), FACE_UP)]),
            ]
        },
        {
            'description': 'Failed ritual',
            'ai_player': {
                'name': 'Seto 3rd',
                'frontrow': [
                    {'name': 'Beaver Warrior'},
                    {'name': 'Gaia the Fierce Knight'},
                    None,
                    None,
                    None],
                'backrow': [{'name': 'Black Luster Ritual', 'is_active': True}, None, None, None, None],
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), DARKEN)]),
            ]
        },
        {
            'description': 'Dark-Piercing Light',
            'player': {
                'frontrow': [
                    {'name': 'Nemuriko', 'face': FACE_DOWN},
                    {'name': 'Nemuriko', 'face': FACE_DOWN},
                    None,
                    None,
                    None],
            },
            'ai_player': {
                'name': 'Villager1',
                'frontrow': [{'name': 'Skull Servant'}, None, None, None, None],
                'backrow': [{'name': 'Dark-piercing Light', 'is_active': True}, None, None, None, None],
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), FACE_UP)]),
            ]
        },
        {
            'description': 'Failed Dark-Piercing Light because at least one monster is face-up',
            'player': {
                'frontrow': [
                    {'name': 'Nemuriko', 'face': FACE_DOWN},
                    {'name': 'Nemuriko', 'face': FACE_UP},
                    None,
                    None,
                    None],
            },
            'ai_player': {
                'name': 'Villager1',
                'frontrow': [{'name': 'Skull Servant'}, None, None, None, None],
                'backrow': [{'name': 'Dark-piercing Light', 'is_active': True}, None, None, None, None],
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), DARKEN)]),
            ]
        },
        {
            'description': 'Failed Dark-Piercing Light because player_monsters <= ai_monsters',
            'player': {
                'frontrow': [{'name': 'Nemuriko', 'face': FACE_DOWN}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Villager1',
                'frontrow': [{'name': 'Skull Servant'}, None, None, None, None],
                'backrow': [{'name': 'Dark-piercing Light', 'is_active': True}, None, None, None, None],
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), DARKEN)]),
            ]
        },
        {
            'description': 'Swords of Revealing Light',
            'player': {
                'frontrow': [{'name': 'Nemuriko', 'face': FACE_UP}, None, None, None, None],
                'remaining_turns_under_swords': 0
            },
            'ai_player': {
                'name': 'Meadow Mage',
                'frontrow': [None, None, None, None, None],
                'backrow': [{'name': 'Swords of Revealing Light', 'is_active': True}, None, None, None, None],
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), FACE_UP)]),
            ]
        },
        {
            'description': 'Swords of Revealing Light #2',
            'player': {
                'frontrow': [{'name': 'Thousand Dragon', 'face': FACE_UP}, None, None, None, None],
                'remaining_turns_under_swords': 0
            },
            'ai_player': {
                'name': 'Meadow Mage',
                'frontrow': [{'name': 'Judge Man'}, None, None, None, None],
                'backrow': [{'name': 'Swords of Revealing Light', 'is_active': True}, None, None, None, None],
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), FACE_UP)]),
            ]
        },
        {
            'description': 'No Swords of Revealing Light due to player already being under its effect',
            'player': {
                'frontrow': [{'name': 'Thousand Dragon', 'face': FACE_UP}, None, None, None, None],
                'remaining_turns_under_swords': 1
            },
            'ai_player': {
                'name': 'Meadow Mage',
                'frontrow': [{'name': 'Judge Man'}, None, None, None, None],
                'backrow': [{'name': 'Swords of Revealing Light', 'is_active': True}, None, None, None, None],
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), DARKEN)]),
            ]
        },
        {
            'description': 'No Swords of Revealing Light due to AI having control',
            'player': {
                'frontrow': [{'name': 'Thousand Dragon', 'face': FACE_UP}, None, None, None, None],
                'remaining_turns_under_swords': 1
            },
            'ai_player': {
                'name': 'Meadow Mage',
                'frontrow': [{'name': 'Judge Man'}, None, None, None, None],
                'backrow': [{'name': 'Swords of Revealing Light', 'is_active': True}, None, None, None, None],
            },
            'field': 'Sogen',
            'expected_combo': [
                Action([(encode_backrow_pos(0), DARKEN)]),
            ]
        },
        {
            'description': 'Stop Defense due to lethal',
            'player': {
                'frontrow': [
                    {'name': 'Thousand Dragon', 'face': FACE_UP, 'equip_stage': 0},
                    {'name': 'Twin-headed Thunder Dragon', 'face': FACE_UP, 'equip_stage': 0},
                    None,
                    None,
                    None
                ],
                'LP': 200
            },
            'ai_player': {
                'name': 'Bandit Keith',
                'frontrow': [{'name': 'Zoa', 'equip_stage': 0}, None, None, None, None],
                'backrow': [{'name': 'Stop Defense', 'is_active': True}, None, None, None, None],
                'remaining_turns_under_swords': 0,
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), FACE_UP)]),
            ]
        },
        {
            'description': "Stop Defense due to AI being able to clear player's visible board",
            'player': {
                'frontrow': [
                    {'name': 'Thousand Dragon', 'face': FACE_UP},
                    {'name': 'Twin-headed Thunder Dragon', 'face': FACE_DOWN},
                    {'name': 'B. Dragon Jungle King', 'face': FACE_UP},
                    None,
                    None
                ],
                'LP': 8_000
            },
            'ai_player': {
                'name': 'Bandit Keith',
                'frontrow': [
                    {'name': 'Zoa', 'face': FACE_UP, 'equip_stage': 0},
                    {'name': 'Zoa', 'face': FACE_DOWN, 'equip_stage': 0},
                    None,
                    None,
                    None
                ],
                'backrow': [{'name': 'Stop Defense', 'is_active': True}, None, None, None, None],
                'remaining_turns_under_swords': 0,
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), FACE_UP)]),
            ]
        },
        {
            'description': 'No Stop Defense due to AI being under Swords',
            'player': {
                'frontrow': [
                    {'name': 'Thousand Dragon', 'face': FACE_UP},
                    {'name': 'Twin-headed Thunder Dragon', 'face': FACE_DOWN},
                    {'name': 'B. Dragon Jungle King', 'face': FACE_UP},
                    None,
                    None
                ],
            },
            'ai_player': {
                'name': 'Bandit Keith',
                'frontrow': [
                    {'name': 'Zoa', 'face': FACE_UP, 'equip_stage': 0},
                    {'name': 'Zoa', 'face': FACE_DOWN, 'equip_stage': 0},
                    None,
                    None,
                    None
                ],
                'backrow': [{'name': 'Stop Defense', 'is_active': True}, None, None, None, None],
                'remaining_turns_under_swords': 1
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), DARKEN)]),
            ]
        },
        {
            'description': 'No Stop Defense due to AI having no monster',
            'player': {
                'frontrow': [
                    {'name': 'Thousand Dragon', 'face': FACE_UP},
                    {'name': 'Twin-headed Thunder Dragon', 'face': FACE_DOWN},
                    {'name': 'B. Dragon Jungle King', 'face': FACE_UP},
                    None,
                    None
                ],
            },
            'ai_player': {
                'name': 'Bandit Keith',
                'frontrow': [None, None, None, None, None],
                'backrow': [{'name': 'Stop Defense', 'is_active': True}, None, None, None, None],
                'remaining_turns_under_swords': 0
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), DARKEN)]),
            ]
        },
        {
            'description': 'No Stop Defense because no lethal and no visible board clear',
            'player': {
                'frontrow': [
                    {'name': 'B. Dragon Jungle King', 'face': FACE_UP},
                    {'name': 'Twin-headed Thunder Dragon', 'face': FACE_UP},
                    None,
                    None,
                    None
                ],
                'LP': 8_000
            },
            'ai_player': {
                'name': 'Bandit Keith',
                'frontrow': [
                    {'name': 'Zoa', 'face': FACE_UP, 'equip_stage': 0},
                    {'name': 'Zoa', 'face': FACE_DOWN, 'equip_stage': 0},
                    None,
                    None,
                    None
                ],
                'backrow': [{'name': 'Stop Defense', 'is_active': True}, None, None, None, None],
                'remaining_turns_under_swords': 0
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), DARKEN)]),
            ]
        },
        {
            'description': 'Destroy type (Dragon)',
            'player': {
                'frontrow': [{'name': 'Meteor B. Dragon', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Mountain Mage',
                'frontrow': [None, None, None, None, None],
                'backrow': [{'name': 'Dragon Capture Jar', 'is_active': True}, None, None, None, None],
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), FACE_UP)]),
            ]
        },
        {
            'description': 'Destroy type (Warrior)',
            'player': {
                'frontrow': [{'name': 'Gaia the Fierce Knight', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Meadow Mage',
                'frontrow': [None, None, None, None, None],
                'backrow': [{'name': 'Warrior Elimination', 'is_active': True}, None, None, None, None],
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), FACE_UP)]),
            ]
        },
        {
            'description': 'Destroy type (Zombie)',
            'player': {
                'frontrow': [{'name': 'Dragon Zombie', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Desert Mage',
                'frontrow': [None, None, None, None, None],
                'backrow': [{'name': 'Eternal Rest', 'is_active': True}, None, None, None, None],
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), FACE_UP)]),
            ]
        },
        {
            'description': 'Destroy type (Machine)',
            'player': {
                'frontrow': [{'name': 'Metalzoa', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Labyrinth Mage',
                'frontrow': [None, None, None, None, None],
                'backrow': [{'name': 'Stain Storm', 'is_active': True}, None, None, None, None],
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), FACE_UP)]),
            ]
        },
        {
            'description': 'Destroy type (Insect)',
            'player': {
                'frontrow': [{'name': 'Kwagar Hercules', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Forest Mage',
                'frontrow': [None, None, None, None, None],
                'backrow': [{'name': 'Eradicating Aerosol', 'is_active': True}, None, None, None, None],
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), FACE_UP)]),
            ]
        },
        {
            'description': 'Destroy type (Rock)',
            'player': {
                'frontrow': [{'name': 'Stone D.', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Desert Mage',
                'frontrow': [None, None, None, None, None],
                'backrow': [{'name': 'Breath of Light', 'is_active': True}, None, None, None, None],
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), FACE_UP)]),
            ]
        },
        {
            'description': 'Destroy type (Fish)',
            'player': {
                'frontrow': [{'name': '7 Colored Fish', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Desert Mage',
                'frontrow': [None, None, None, None, None],
                'backrow': [{'name': 'Eternal Draught', 'is_active': True}, None, None, None, None],
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), FACE_UP)]),
            ]
        },
        {
            'description': 'No Destroy type due to AI having control',
            'player': {
                'frontrow': [{'name': '7 Colored Fish', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Desert Mage',
                'frontrow': [{'name': 'Stone D.'}, None, None, None, None],
                'backrow': [{'name': 'Eternal Draught', 'is_active': True}, None, None, None, None],
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), DARKEN)]),
            ]
        },
        {
            'description': "No Destroy type due to non matching player's best card type",
            'player': {
                'frontrow': [
                    {'name': '7 Colored Fish', 'face': FACE_UP},
                    {'name': 'Stone D.', 'face': FACE_UP},
                    None,
                    None,
                    None
                ],
            },
            'ai_player': {
                'name': 'Desert Mage',
                'frontrow': [{'name': 'Stone D.'}, None, None, None, None],
                'backrow': [{'name': 'Eternal Draught', 'is_active': True}, None, None, None, None],
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), DARKEN)]),
            ]
        },
        {
            'description': 'Lower stats (Spellbinding Circle)',
            'player': {
                'frontrow': [{'name': 'Stone D.', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Isis',
                'frontrow': [{'name': 'Aqua Dragon'}, None, None, None, None],
                'backrow': [{'name': 'Spellbinding Circle', 'is_active': True}, None, None, None, None],
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), FACE_UP)]),
            ]
        },
        {
            'description': 'Lower stats (Shadow Spell)',
            'player': {
                'frontrow': [{'name': 'Stone D.', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Kaiba',
                'frontrow': [{'name': 'Parrot Dragon'}, None, None, None, None],
                'backrow': [{'name': 'Shadow Spell', 'is_active': True}, None, None, None, None],
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), FACE_UP)]),
            ]
        },
        {
            'description': 'No Lower stats due to AI having control',
            'player': {
                'frontrow': [{'name': 'Kaminari Attack', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Kaiba',
                'frontrow': [{'name': 'Parrot Dragon'}, None, None, None, None],
                'backrow': [{'name': 'Shadow Spell', 'is_active': True}, None, None, None, None],
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), DARKEN)]),
            ]
        },
        {
            'description': 'Crush Card',
            'player': {
                'frontrow': [{'name': 'Stone D.', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Kaiba',
                'frontrow': [{'name': 'Parrot Dragon'}, None, None, None, None],
                'backrow': [{'name': 'Crush Card', 'is_active': True}, None, None, None, None],
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), FACE_UP)]),
            ]
        },
        {
            'description': 'No Crush Card due to AI having control',
            'player': {
                'frontrow': [{'name': 'Kaminari Attack', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Kaiba',
                'frontrow': [{'name': 'Parrot Dragon'}, None, None, None, None],
                'backrow': [{'name': 'Crush Card', 'is_active': True}, None, None, None, None],
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), DARKEN)]),
            ]
        },
        {
            'description': 'No Crush Card due to player having too low Attack',
            'player': {
                'frontrow': [{'name': 'Hibikime', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Kaiba',
                'frontrow': [None, None, None, None, None],
                'backrow': [{'name': 'Crush Card', 'is_active': True}, None, None, None, None],
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), DARKEN)]),
            ]
        },
        {
            'description': 'Raigeki',
            'player': {
                'frontrow': [{'name': 'Meteor B. Dragon'}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Seto 3rd',
                'frontrow': [{'name': 'B. Skull Dragon'}, None, None, None, None],
                'backrow': [{'name': 'Raigeki', 'is_active': True}, None, None, None, None],
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), FACE_UP)]),
            ]
        },
        {
            'description': 'No Raigeki due to player having stricly fewer visible monsters than the AI',
            'player': {
                'frontrow': [
                    {'name': 'Meteor B. Dragon', 'face': FACE_DOWN},
                    {'name': 'Twin-headed Thunder Dragon', 'face': FACE_UP},
                    None,
                    None,
                    None
                ],
            },
            'ai_player': {
                'name': 'High Mage Atenza',
                'frontrow': [
                    {'name': 'Gaia the Dragon Champion'},
                    {'name': 'Sanga of the Thunder'},
                    None,
                    None,
                    None
                ],
                'backrow': [{'name': 'Raigeki', 'is_active': True}, None, None, None, None],
            },
            'expected_combo': [
                Action([(encode_backrow_pos(0), DARKEN)]),
            ]
        },
        {
            'description': "Field (player's best card is not boosted)",
            'player': {
                'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Meadow Mage',
                'frontrow': [{'name': 'Judge Man'}, None, None, None, None],
                'backrow': [{'name': 'Sogen', 'is_active': True}, None, None, None, None],
            },
            'field': 'Umi',
            'expected_combo': [
                Action([(encode_backrow_pos(0), FACE_UP)]),
            ]
        },
        {
            'description': "Field (AI's best card is boosted)",
            'player': {
                'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Ocean Mage',
                'frontrow': [{'name': 'Aqua Dragon'}, None, None, None, None],
                'backrow': [{'name': 'Umi', 'is_active': True}, None, None, None, None],
            },
            'field': 'Mountain',
            'expected_combo': [
                Action([(encode_backrow_pos(0), FACE_UP)]),
            ]
        },
        {
            'description': 'Field due to default type being Dragon when the AI has no monster on the board',
            'player': {
                'frontrow': [{'name': 'Kairyu-shin', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Mountain Mage',
                'frontrow': [None, None, None, None, None],
                'backrow': [{'name': 'Mountain', 'is_active': True}, None, None, None, None],
            },
            'field': None,
            'expected_combo': [
                Action([(encode_backrow_pos(0), FACE_UP)]),
            ]
        },
        {
            'description': 'No field due to AI having field control',
            'player': {
                'frontrow': [{'name': 'Curse of Dragon', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Ocean Mage',
                'frontrow': [{'name': 'Aqua Dragon'}, None, None, None, None],
                'backrow': [{'name': 'Umi', 'is_active': True}, None, None, None, None],
            },
            'field': None,
            'expected_combo': [
                Action([(encode_backrow_pos(0), DARKEN)]),
            ]
        },
        {
            'description': 'No field due to field already being of the would-be new type',
            'player': {
                'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Ocean Mage',
                'frontrow': [{'name': 'Aqua Dragon'}, None, None, None, None],
                'backrow': [{'name': 'Umi', 'is_active': True}, None, None, None, None],
            },
            'field': 'Umi',
            'expected_combo': [
                Action([(encode_backrow_pos(0), DARKEN)]),
            ]
        },
        {
            'description': "No field due to field boosting the player's best card",
            'player': {
                'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Ocean Mage',
                'frontrow': [{'name': 'Aqua Dragon'}, None, None, None, None],
                'backrow': [{'name': 'Umi', 'is_active': True}, None, None, None, None],
            },
            'field': None,
            'expected_combo': [
                Action([(encode_backrow_pos(0), DARKEN)]),
            ]
        },
        {
            'description': 'No field due to field not weakening player and not boosting AI',
            'player': {
                'frontrow': [{'name': 'Thousand Dragon', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Ocean Mage',
                'frontrow': [{'name': 'Parrot Dragon'}, None, None, None, None],
                'backrow': [{'name': 'Umi', 'is_active': True}, None, None, None, None],
            },
            'field': None,
            'expected_combo': [
                Action([(encode_backrow_pos(0), DARKEN)]),
            ]
        },
        {
            'description': 'No field due to default AI type being Dragon when no monster is on the board',
            'player': {
                'frontrow': [{'name': 'Thousand Dragon', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Ocean Mage',
                'frontrow': [None, None, None, None, None],
                'backrow': [{'name': 'Umi', 'is_active': True}, None, None, None, None],
            },
            'field': None,
            'expected_combo': [
                Action([(encode_backrow_pos(0), DARKEN)]),
            ]
        },
        {
            'description': 'Dark Hole',
            'player': {
                'frontrow': [
                    {'name': 'Thousand Dragon', 'face': FACE_UP},
                    {'name': 'B. Dragon Jungle King', 'face': FACE_DOWN},
                    None,
                    None,
                    None
                ],
            },
            'ai_player': {
                'name': 'Yami Bakura',
                'frontrow': [{'name': 'Aqua Madoor'}, None, None, None, None],
                'backrow': [{'name': 'Dark Hole', 'is_active': True}, None, None, None, None],
            },
            'field': None,
            'expected_combo': [
                Action([(encode_backrow_pos(0), FACE_UP)]),
            ]
        },
        {
            'description': 'No Dark Hole due to AI having field control',
            'player': {
                'frontrow': [{'name': 'Queen of Autumn Leaves', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Yami Bakura',
                'frontrow': [{'name': 'Aqua Madoor'}, None, None, None, None],
                'backrow': [{'name': 'Dark Hole', 'is_active': True}, None, None, None, None],
            },
            'field': None,
            'expected_combo': [
                Action([(encode_backrow_pos(0), DARKEN)]),
            ]
        },
        {
            'description': 'No Dark Hole due to #player monsters <= #ai monsters',
            'player': {
                'frontrow': [{'name': 'Thousand Dragon', 'face': FACE_UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Yami Bakura',
                'frontrow': [{'name': 'Aqua Madoor'}, None, None, None, None],
                'backrow': [{'name': 'Dark Hole', 'is_active': True}, None, None, None, None],
            },
            'field': None,
            'expected_combo': [
                Action([(encode_backrow_pos(0), DARKEN)]),
            ]
        },

        # Frontrow
        {
            'description': 'Defend > Cocoon of Evolution',
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Millennium Shield', 'is_active': True},
                    {'name': 'Cocoon of Evolution', 'is_active': True},
                    None, None, None
                ],
                'backrow': [None]*5,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(1), DEFENSE)]),
            ]
        },
        {
            'description': 'Defend > Millennium Shield',
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Labyrinth Wall', 'is_active': True},
                    {'name': 'Millennium Shield', 'is_active': True},
                    None, None, None
                ],
                'backrow': [None]*5,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(1), DEFENSE)]),
            ]
        },
        {
            'description': 'Defend > Labyrinth Wall',
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Mystical Elf', 'is_active': True},
                    {'name': 'Labyrinth Wall', 'is_active': True},
                    None, None, None
                ],
                'backrow': [None]*5,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(1), DEFENSE)]),
            ]
        },
        {
            'description': 'Defend > Mystical Elf',
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Dragon Piper', 'is_active': True},
                    {'name': 'Mystical Elf', 'is_active': True},
                    None, None, None
                ],
                'backrow': [None]*5,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(1), DEFENSE)]),
            ]
        },
        {
            'description': 'Defend > Dragon Piper',
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Castle of Dark Illusions', 'is_active': True},
                    {'name': 'Dragon Piper', 'is_active': True},
                    None, None, None
                ],
                'backrow': [None]*5,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(1), DEFENSE)]),
            ]
        },
        {
            'description': 'Defend > Castle of Dark Illusions',
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Metal Guardian', 'is_active': True},
                    {'name': 'Castle of Dark Illusions', 'is_active': True},
                    None, None, None
                ],
                'backrow': [None]*5,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(1), DEFENSE)]),
            ]
        },
        {
            'description': 'Defend > Metal Guardian',
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Sleeping Lion', 'is_active': True},
                    {'name': 'Metal Guardian', 'is_active': True},
                    None, None, None
                ],
                'backrow': [None]*5,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(1), DEFENSE)]),
            ]
        },
        {
            'description': 'Defend > Sleeping Lion',
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Hard Armor', 'is_active': True},
                    {'name': 'Sleeping Lion', 'is_active': True},
                    None, None, None
                ],
                'backrow': [None]*5,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(1), DEFENSE)]),
            ]
        },
        {
            'description': 'Defend > Hard Armor',
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Spirit of the Harp', 'is_active': True},
                    {'name': 'Hard Armor', 'is_active': True},
                    None, None, None
                ],
                'backrow': [None]*5,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(1), DEFENSE)]),
            ]
        },
        {
            'description': 'Defend > Spirit of the Harp',
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Prevent Rat', 'is_active': True},
                    {'name': 'Spirit of the Harp', 'is_active': True},
                    None, None, None
                ],
                'backrow': [None]*5,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(1), DEFENSE)]),
            ]
        },
        {
            'description': 'Defend > Prevent Rat',
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Green Phantom King', 'is_active': True},
                    {'name': 'Prevent Rat', 'is_active': True},
                    None, None, None
                ],
                'backrow': [None]*5,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(1), DEFENSE)]),
            ]
        },
        {
            'description': 'Defend > Green Phantom King',
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Gorgon Egg', 'is_active': True},
                    {'name': 'Green Phantom King', 'is_active': True},
                    None, None, None
                ],
                'backrow': [None]*5,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(1), DEFENSE)]),
            ]
        },
        {
            'description': 'Defend > Gorgon Egg',
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Wall Shadow', 'is_active': True},
                    {'name': 'Gorgon Egg', 'is_active': True},
                    None, None, None
                ],
                'backrow': [None]*5,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(1), DEFENSE)]),
            ]
        },
        {
            'description': 'Defend > Wall Shadow',
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Blocker', 'is_active': True},
                    {'name': 'Wall Shadow', 'is_active': True},
                    None, None, None
                ],
                'backrow': [None]*5,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(1), DEFENSE)]),
            ]
        },
        {
            'description': 'Defend > Blocker',
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Golgoil', 'is_active': True},
                    {'name': 'Blocker', 'is_active': True},
                    None, None, None
                ],
                'backrow': [None]*5,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(1), DEFENSE)]),
            ]
        },
        {
            'description': 'Defend > Golgoil',
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': '30,000-Year White Turtle', 'is_active': True},
                    {'name': 'Golgoil', 'is_active': True},
                    None, None, None
                ],
                'backrow': [None]*5,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(1), DEFENSE)]),
            ]
        },
        {
            'description': 'Defend > 30,000-Year White Turtle',
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Queen Bird', 'is_active': True},
                    {'name': '30,000-Year White Turtle', 'is_active': True},
                    None, None, None
                ],
                'backrow': [None]*5,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(1), DEFENSE)]),
            ]
        },
        {
            'description': 'Defend > Queen Bird',
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Yado Karu', 'is_active': True},
                    {'name': 'Queen Bird', 'is_active': True},
                    None, None, None
                ],
                'backrow': [None]*5,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(1), DEFENSE)]),
            ]
        },
        {
            'description': 'Defend > Yado Karu',
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Boulder Tortoise', 'is_active': True},
                    {'name': 'Yado Karu', 'is_active': True},
                    None, None, None
                ],
                'backrow': [None]*5,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(1), DEFENSE)]),
            ]
        },
        {
            'description': 'Defend > Boulder Tortoise',
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Doron', 'is_active': True},
                    {'name': 'Boulder Tortoise', 'is_active': True},
                    None, None, None
                ],
                'backrow': [None]*5,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(1), DEFENSE)]),
            ]
        },
        {
            'description': 'Defend > check next active card in Defend list',
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Cocoon of Evolution', 'is_active': False},
                    {'name': 'Queen Bird', 'is_active': True},
                    {'name': 'Spirit of the Harp', 'is_active': True},
                    {'name': 'Wall Shadow', 'is_active': False},
                    {'name': 'Castle of Dark Illusions', 'is_active': False},
                ],
                'backrow': [None]*5,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(2), DEFENSE)]),
            ]
        },
        {
            'description': 'Swords > All in Defend due to Swords being active on the AI side',
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Doron', 'is_active': True},
                    {'name': 'Boulder Tortoise', 'is_active': False},
                    None, None, None
                ],
                'backrow': [None]*5,
                'remaining_turns_under_swords': 1,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(0), DEFENSE)]),
            ]
        },
        {
            'description': 'Swords > Descending true attack',
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Twin-headed Thunder Dragon', 'is_active': True},
                    {'name': 'Twin-headed Thunder Dragon', 'is_active': True, 'equip_stage': 2},
                    {'name': 'Boulder Tortoise', 'is_active': False},
                    None, None, None
                ],
                'backrow': [None]*5,
                'remaining_turns_under_swords': 1,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(1), DEFENSE)]),
            ]
        },
        {
            'description': 'Swords > No defend for monsters in forced attack list',
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Meteor B. Dragon', 'is_active': True},
                    {'name': 'Boulder Tortoise', 'is_active': False},
                    None, None, None
                ],
                'backrow': [None]*5,
                'remaining_turns_under_swords': 1,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(0), ATTACK)]),
            ]
        },

        # Next battle
        {
            'description': 'Next battle > Direct attack',
            'player': {
                'frontrow': [None, None, None, None, None],
                'backrow': [{'name': 'Widespread Ruin'}, None, None, None, None],
                'LP': 8_000
            },
            'ai_player': {
                'name': 'Seto 3rd',
                'frontrow': [
                    {'name': 'Blue-eyes Ultimate Dragon', 'is_active': True},
                    None, None, None, None
                ],
                'backrow': [None]*5,
                'remaining_turns_under_swords': 0,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(0), ATTACK, encode_frontrow_pos(2))]),
            ]
        },
        {
            'description': 'Next battle > lethal',
            'player': {
                'frontrow': [
                    {'name': 'Doron', 'face': FACE_UP, 'battle_mode': ATTACK},
                    {'name': 'Skull Servant', 'face': FACE_UP, 'battle_mode': ATTACK},
                    None, None, None
                ],
                'LP': 1_000
            },
            'ai_player': {
                'name': 'Bandit Keith',
                'frontrow': [
                    {'name': 'Doron', 'is_active': True},
                    {'name': 'Mechanicalchacer', 'is_active': True},
                    None, None, None
                ],
                'backrow': [None]*5,
                'remaining_turns_under_swords': 0,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(1), ATTACK, encode_frontrow_pos(1))]),
            ]
        },
        {
            'description': 'Next battle > Suicide glitch',
            'player': {
                'frontrow': [
                    {'name': 'Twin-headed Thunder Dragon', 'battle_mode': ATTACK, 'equip_stage': 4},
                    None, None, None, None
                ],
                'LP': 300
            },
            'ai_player': {
                'name': 'Seto 3rd',
                'frontrow': [
                    {'name': 'Blue-eyes Ultimate Dragon', 'is_active': True},
                    None, None, None, None
                ],
                'backrow': [None]*5,
                'remaining_turns_under_swords': 0,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(0), ATTACK, encode_frontrow_pos(0))]),
            ]
        },
        {
            'description': 'Next battle > Attack visible monsters in attack mode thanks to star',
            'player': {
                'frontrow': [
                    {'name': 'Twin-headed Thunder Dragon', 'battle_mode': ATTACK, 'star': 'Pluto'},
                    {'name': 'Curse of Dragon', 'battle_mode': ATTACK, 'star': 'Saturn'},
                    {'name': 'B. Dragon Jungle King', 'battle_mode': ATTACK, 'star': 'Jupiter'},
                    None, None
                ],
                'LP': 8_000
            },
            'ai_player': {
                'name': 'Pegasus',
                'frontrow': [
                    {'name': 'Bickuribox', 'is_active': True, 'star': 'Moon'},
                    {'name': 'Vermillion Sparrow', 'is_active': True, 'star': 'Mars'},
                    None, None, None
                ],
                'backrow': [None]*5,
                'remaining_turns_under_swords': 0,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(1), ATTACK, encode_frontrow_pos(2))]),
            ]
        },
        {
            'description': 'Next battle > Attack visible monsters in attack mode',
            'player': {
                'frontrow': [
                    {'name': 'Twin-headed Thunder Dragon', 'battle_mode': ATTACK, 'star': 'Pluto'},
                    {'name': 'Curse of Dragon', 'battle_mode': ATTACK, 'star': 'Saturn'},
                    {'name': 'B. Dragon Jungle King', 'battle_mode': ATTACK, 'star': 'Jupiter'},
                    None, None
                ],
                'LP': 8_000
            },
            'ai_player': {
                'name': 'Pegasus',
                'frontrow': [
                    {'name': 'Meteor Dragon', 'is_active': True, 'star': 'Uranus'},
                    {'name': 'Bickuribox', 'is_active': True, 'star': 'Moon'},
                    None, None, None
                ],
                'backrow': [None]*5,
                'remaining_turns_under_swords': 0,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(1), ATTACK, encode_frontrow_pos(2))]),
            ]
        },
        {
            'description': 'Next battle > Attack visible monsters in attack mode before defense mode',
            'player': {
                'frontrow': [
                    {'name': 'Twin-headed Thunder Dragon', 'battle_mode': ATTACK, 'star': 'Pluto'},
                    {'name': 'Curse of Dragon', 'battle_mode': ATTACK, 'star': 'Saturn'},
                    {'name': 'B. Dragon Jungle King', 'battle_mode': DEFENSE, 'star': 'Jupiter'},
                    None, None
                ],
                'LP': 8_000
            },
            'ai_player': {
                'name': 'Pegasus',
                'frontrow': [
                    {'name': 'Meteor Dragon', 'is_active': True, 'star': 'Uranus'},
                    {'name': 'Bickuribox', 'is_active': True, 'star': 'Moon'},
                    None, None, None
                ],
                'backrow': [None]*5,
                'remaining_turns_under_swords': 0,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(1), ATTACK, encode_frontrow_pos(1))]),
            ]
        },
        {
            'description': 'Next battle > Attack visible monsters in defense mode',
            'player': {
                'frontrow': [
                    {'name': 'Twin-headed Thunder Dragon', 'battle_mode': ATTACK, 'star': 'Pluto'},
                    {'name': 'Thousand Dragon', 'battle_mode': DEFENSE, 'star': 'Mars'},
                    {'name': '30,000-Year White Turtle', 'battle_mode': DEFENSE, 'star': 'Neptune'},
                    None, None
                ],
                'LP': 8_000
            },
            'ai_player': {
                'name': 'Pegasus',
                'frontrow': [
                    {'name': 'Meteor Dragon', 'is_active': True, 'star': 'Uranus'},
                    {'name': 'Bickuribox', 'is_active': True, 'star': 'Moon'},
                    None, None, None
                ],
                'backrow': [None]*5,
                'remaining_turns_under_swords': 0,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(1), ATTACK, encode_frontrow_pos(2))]),
            ]
        },
        {
            'description': 'Next battle > Attack facedown monsters',
            'player': {
                'frontrow': [
                    {'name': 'Doron', 'battle_mode': DEFENSE, 'face': FACE_DOWN, 'star': 'Neptune'},
                    {'name': 'Doron', 'battle_mode': DEFENSE, 'face': FACE_DOWN, 'star': 'Neptune'},
                    None, None, None
                ],
                'LP': 8_000
            },
            'ai_player': {
                'name': 'Weevil Underwood',
                'frontrow': [
                    {'name': 'Jirai Gumo', 'is_active': True, 'star': 'Jupiter'},
                    None, None, None, None
                ],
                'backrow': [None]*5,
                'remaining_turns_under_swords': 0,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(0), ATTACK, encode_frontrow_pos(0))], odds=(50, 100), level=1),
                Action([], odds=(50, 100), _next=Actions([
                    Action([(encode_frontrow_pos(0), ATTACK, encode_frontrow_pos(1))], odds=(50, 100)),
                    Action([(encode_frontrow_pos(0), DEFENSE)], odds=(50, 100)),
                ], level=2)),
            ]
        },
        {
            'description': 'Next battle > Attack with remaining monsters',
            'player': {
                'frontrow': [None]*5,
                'LP': 8_000
            },
            'ai_player': {
                'name': 'Rex Raptor',
                'frontrow': [
                    {'name': 'Uraby', 'is_active': False, 'star': 'Jupiter'},
                    {'name': 'Clown Zombie', 'is_active': True, 'star': 'Moon'},
                    {'name': 'Clown Zombie', 'is_active': True, 'star': 'Moon'},
                    None, None
                ],
                'backrow': [None]*5,
                'remaining_turns_under_swords': 0,
            },
            'expected_combo': [
                Action([(encode_frontrow_pos(1), ATTACK, encode_frontrow_pos(2))]),
                Action([(encode_frontrow_pos(2), ATTACK, encode_frontrow_pos(2))])
            ]
        },
    ]


def test_board_ai(cur, tests):
    results = []
    combos = []
    # DEFAULT_CURRENT_AI_TURN = 1
    for index, test in enumerate(tests):
        player = test.get('player')
        ai_player = test['ai_player']
        field = test.get('field')
        # current_ai_turn = test.get('current_ai_turn', DEFAULT_CURRENT_AI_TURN)

        # Translates card names on the board into their respective card id (monsters & backrow, both player and AI)
        for cards, row_type in itertools.chain.from_iterable([
            [
                (pl.get('frontrow'), FRONTROW),
                (pl.get('backrow'), BACKROW),
                (pl.get('hand_names'), None),
                (pl.get('remaining_deck_names'), None)
            ] if pl is not None else []
            for pl in [player, ai_player]
        ]):
            if cards is None or len(cards) == 0:
                continue
            for pos, card in enumerate(cards):
                if card is None:
                    continue
                board_card_name = card if row_type is None else card['name']
                board_card_id = get_card_id_from_name(cur, board_card_name)
                if board_card_name is not None and board_card_id is None:
                    raise ValueError(f"{index}. Couldn't find id of board card name '{board_card_name}'.")
                card = card if isinstance(card, dict) else {}
                card['name'] = board_card_name
                card['id'] = board_card_id
                card['pos'] = encode_frontrow_pos(pos) if row_type == FRONTROW \
                              else encode_backrow_pos(pos) if row_type == BACKROW \
                              else pos
                if 'equip_stage' not in card and row_type == FRONTROW:
                    card['equip_stage'] = 0
                cards[pos] = card

        expected_combo = test['expected_combo']
        # expected_combo_detailled = test.get('expected_combo_detailled')

        # Translates card names in hands into their respective card id (monsters & backrow, both player and AI)
        for pl in [player, ai_player]:
            if pl is None:
                continue
            if 'hand_names' in pl:
                pl['hand'] = pl['hand_names']
            if 'remaining_deck_names' in pl:
                pl['remaining_deck'] = pl['remaining_deck_names']

        is_passed = True
        try:
            combo = next(ai_board.board_ai(cur, player, ai_player, field=field))
        except Exception as e:
            print(test['description'])
            is_passed = False
            raise e
        else:
            combos.append(combo)

            actual_tests = [expected_combo]  # [x for x in [expected_combo] if x is not None]

            for actual_test in actual_tests:
                if actual_test == expected_combo:
                    is_passed &= (combo.actions == expected_combo if combo is not None else combo == expected_combo)
        finally:
            results.append(is_passed)

    print(f"Successes: {len(list(filter(None, results)))} / {len(results)} :Total")
    if any([not x for x in results]):
        print(f"Differences :", end=' ')
        print(
            *[{'index': index, 'description': test['description'], 'found': best_combo, 'expected': test['expected_combo']}
              for index, result, best_combo, test
              in zip(range(0, len(tests)), results, combos, tests)
              if not result],
            sep='\n'
        )


if __name__ == '__main__':
    ai_stats = ai.get_all_ai_stats()
    con, cur = db.connect_to_YFM_database()

    print('Tests Hand AI')
    test_hand_ai(cur, tests_hand_ai)

    print('Tests Board AI')
    test_board_ai(cur, tests_board_ai)

    con.close()
