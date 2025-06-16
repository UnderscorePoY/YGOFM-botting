from pprint import pprint

import ai
import ai_board
import ai_hand
from actions_handler import play_from_hand, play_from_board, EndOfTurn
from ai_hand import *
from types_ import IsActive, Star
from utils import *


tests_hand_ai = [
    # 1. Direct kill
    {
        'description': 'Direct kill > Sparks',
        'player': {
            'backrow': [None] * 5,
            'lp': 50,
        },
        'ai_player': {
            'name': 'DarkNite',
            'hand_names': ['Sparks', 'Hinotama', 'Final Flame', 'Ookazi', 'Tremendous Fire'],
        },

        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.HAND), Face.UP)])
        ],

        'expected_outcome': {
            'player': {
                'frontrow': [None]*5,
                'lp': 0
            },
            'ai_player': {
                'name': 'DarkNite',
                'hand_names': [None, 'Hinotama', 'Final Flame', 'Ookazi', 'Tremendous Fire'],
            }
        },
    },
    {
        'description': 'Direct kill > Hinotama',
        'player': {
            'backrow': [None] * 5,
            'lp': 100,
        },
        'ai_player': {
            'name': 'DarkNite',
            'hand_names': ['Sparks', 'Final Flame', 'Ookazi', 'Tremendous Fire', 'Hinotama'],
        },
        'expected_combo': [
            Action([Action.Description(Position(4, Position.Mode.HAND), Face.UP)])
        ],

        'expected_outcome': {
            'player': {
                'backrow': [None] * 5,
                'lp': 0,
            },
            'ai_player': {
                'name': 'DarkNite',
                'hand_names': ['Sparks', 'Final Flame', 'Ookazi', 'Tremendous Fire', None],
            },
        }
    },
    {
        'description': 'Direct kill > Final Flame',
        'player': {
            'backrow': [None] * 5,
            'lp': 180,
        },
        'ai_player': {
            'name': 'DarkNite',
            'hand_names': ['Sparks', 'Final Flame', 'Ookazi', 'Tremendous Fire', 'Hinotama'],
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.HAND), Face.UP)])
        ],

        'expected_outcome': {
            'player': {
                'backrow': [None] * 5,
                'lp': 0,
            },
            'ai_player': {
                'name': 'DarkNite',
                'hand_names': ['Sparks', None, 'Ookazi', 'Tremendous Fire', 'Hinotama'],
            },
        }
    },
    {
        'description': 'Direct kill > Ookazi',
        'player': {
            'backrow': [None] * 5,
            'lp': 300,
        },
        'ai_player': {
            'name': 'DarkNite',
            'hand_names': ['Tremendous Fire', 'Ookazi', 'Sparks', 'Final Flame', 'Hinotama'],
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.HAND), Face.UP)])
        ],

        'expected_outcome': {
            'player': {
                'backrow': [None] * 5,
                'lp': 0,
            },
            'ai_player': {
                'name': 'DarkNite',
                'hand_names': ['Tremendous Fire', None, 'Sparks', 'Final Flame', 'Hinotama'],
            },
        }
    },
    {
        'description': 'Direct kill > Tremendous Fire',
        'player': {
            'backrow': [None] * 5,
            'lp': 700,
        },
        'ai_player': {
            'name': 'DarkNite',
            'hand_names': ['Ookazi', 'Sparks', 'Final Flame', 'Tremendous Fire', 'Hinotama'],
        },
        'expected_combo': [
            Action([Action.Description(Position(3, Position.Mode.HAND), Face.UP)])
        ],

        'expected_outcome': {
            'player': {
                'backrow': [None] * 5,
                'lp': 0,
            },
            'ai_player': {
                'name': 'DarkNite',
                'hand_names': ['Ookazi', 'Sparks', 'Final Flame', None, 'Hinotama'],
            },
        }
    },
    {
        'description': 'Direct kill > No direct damage due to player backrow',
        'player': {
            'frontrow': [{'name': 'Twin-headed Thunder Dragon'}, None, None, None, None],
            'backrow': [{'name': 'Raigeki', 'face': Face.DOWN}, None, None, None, None],
            'lp': 700,
        },
        'ai_player': {
            'name': 'DarkNite',
            'frontrow': [None, None, None, None, None],
            'hand_names': ['Ookazi', 'Sparks', 'Final Flame', 'Tremendous Fire', 'Hinotama', 'Doron'],
        },
        'expected_combo': [
            Action([Action.Description(Position(5, Position.Mode.HAND), Face.DOWN)])
        ],

        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'Twin-headed Thunder Dragon'}, None, None, None, None],
                'backrow': [{'name': 'Raigeki', 'face': Face.DOWN}, None, None, None, None],
                'lp': 700,
            },
            'ai_player': {
                'name': 'DarkNite',
                'frontrow': [{'name': 'Doron', 'face': Face.DOWN}, None, None, None, None],
                'hand_names': ['Ookazi', 'Sparks', 'Final Flame', 'Tremendous Fire', 'Hinotama', None],
            },
        }
    },

    # 2. Force fields
    {
        'description': 'Force fields > Ocean Mage',
        'ai_player': {
            'name': 'Ocean Mage',
            'hand_names': ['Sea King Dragon', 'Umi'],
        },
        'field': 'None',
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.HAND), Face.UP)])
        ],

        'expected_outcome': {
            'ai_player': {
                'name': 'Ocean Mage',
                'hand_names': ['Sea King Dragon', None],
            },
            'field': 'Umi',
        }
    },
    {
        'description': 'Force fields > Mountain Mage',
        'ai_player': {
            'name': 'Mountain Mage',
            'hand_names': ['Mountain', 'Punished Eagle'],
        },
        'field': 'None',
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.HAND), Face.UP)])
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Mountain Mage',
                'hand_names': [None, 'Punished Eagle'],
            },
            'field': 'Mountain',
        }
    },
    {
        'description': 'Force fields > Desert Mage',
        'ai_player': {
            'name': 'Desert Mage',
            'hand_names': ['Wasteland', 'Crawling Dragon #2'],
        },
        'field': 'None',
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.HAND), Face.UP)])
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Desert Mage',
                'hand_names': [None, 'Crawling Dragon #2'],
            },
            'field': 'Wasteland',
        }
    },
    {
        'description': 'Force fields > Meadow Mage',
        'ai_player': {
            'name': 'Meadow Mage',
            'hand_names': ['Sogen', 'Empress Judge'],
        },
        'field': 'None',
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.HAND), Face.UP)])
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Meadow Mage',
                'hand_names': [None, 'Empress Judge'],
            },
            'field': 'Sogen',
        }
    },
    {
        'description': 'Force fields > Forest Mage',
        'ai_player': {
            'name': 'Forest Mage',
            'hand_names': ['Forest', 'Hercules Beetle'],
        },
        'field': 'None',
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.HAND), Face.UP)])
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Forest Mage',
                'hand_names': [None, 'Hercules Beetle'],
            },
            'field': 'Forest',
        }
    },
    {
        'description': 'Force fields > Guardian Neku',
        'ai_player': {
            'name': 'Guardian Neku',
            'hand_names': ['Yami', 'Skull Knight'],
        },
        'field': 'Umi',
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.HAND), Face.UP)])
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Guardian Neku',
                'hand_names': [None, 'Skull Knight'],
            },
            'field': 'Yami',
        }
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
            Action([Action.Description(Position(0, Position.Mode.HAND), Face.DOWN)])
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'Mystical Sand'}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Pegasus',
                'frontrow': [{'name': 'Parrot Dragon', 'face': Face.DOWN}, None, None, None, None],
                'hand_names': [None, 'Flame Swordsman'],
            },
        }
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
            Action([Action.Description(Position(1, Position.Mode.HAND), Face.DOWN)])
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'Mystical Sand'}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Pegasus',
                'frontrow': [{'name': 'Parrot Dragon'}, {'name': 'Bickuribox', 'face': Face.DOWN}, None, None, None],
                'hand_names': ['Parrot Dragon', None],
            }
        }
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
            'current_turn': 4,
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.HAND), Face.UP)])
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [None, None, None, None, None],
            },
            'ai_player': {
                'name': 'Pegasus',
                'frontrow': [{'name': 'Parrot Dragon'}, None, None, None, None],
                'hand_names': ['Parrot Dragon', None],
                'current_turn': 4,
            },
        }
    },
    {
        'description': 'Regain control with magic/trap > Decrease stats (Spellbinding Circle)',
        'player': {
            'frontrow': [{'name': 'B. Dragon Jungle King', 'face': Face.UP},
                         None, None, None, None],
        },
        'ai_player': {
            'name': 'Yami Bakura',
            'frontrow': [{'name': 'Aqua Madoor'}, None, None, None, None],
            'hand_names': ['Aqua Madoor', 'Aqua Madoor', 'Spellbinding Circle'],
            'current_turn': 4,
        },
        'expected_combo': [
            Action([Action.Description(Position(2, Position.Mode.HAND), Face.UP)])
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'B. Dragon Jungle King', 'face': Face.UP, 'equip_stage': -1},
                             None, None, None, None],
            },
            'ai_player': {
                'name': 'Yami Bakura',
                'frontrow': [{'name': 'Aqua Madoor'}, None, None, None, None],
                'hand_names': ['Aqua Madoor', 'Aqua Madoor', None],
                'current_turn': 4,
            },
        }
    },
    {
        'description': 'Regain control with magic/trap > Decrease stats (Shadow Spell)',
        'player': {
            'frontrow': [{'name': 'B. Dragon Jungle King', 'face': Face.UP},
                         None, None, None, None],
        },
        'ai_player': {
            'name': 'Kaiba',
            'frontrow': [{'name': 'Aqua Madoor'}, None, None, None, None],
            'hand_names': ['Queen Bird', 'Shadow Spell'],
            'current_turn': 4,
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.HAND), Face.UP)])
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'B. Dragon Jungle King', 'face': Face.UP, 'equip_stage': -2},
                             None, None, None, None],
            },
            'ai_player': {
                'name': 'Kaiba',
                'frontrow': [{'name': 'Aqua Madoor'}, None, None, None, None],
                'hand_names': ['Queen Bird', None],
                'current_turn': 4,
            },
        }
    },
    {
        'description': 'Regain control with magic/trap > Destroy monsters (Crush Card)',
        'player': {
            'frontrow': [{'name': 'B. Dragon Jungle King', 'face': Face.UP}, None, None, None, None],
        },
        'ai_player': {
            'name': 'Kaiba',
            'frontrow': [{'name': 'Aqua Madoor'}, None, None, None, None],
            'hand_names': ['Reaper of the Cards', 'Crush Card'],
            'current_turn': 4,
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.HAND), Face.UP)])
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [None, None, None, None, None],
            },
            'ai_player': {
                'name': 'Kaiba',
                'frontrow': [{'name': 'Aqua Madoor'}, None, None, None, None],
                'hand_names': ['Reaper of the Cards', None],
                'current_turn': 4,
            },
        }
    },
    {
        'description': 'Regain control with magic/trap > Destroy monsters (Raigeki)',
        'player': {
            'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': Face.UP}, None, None, None, None],
        },
        'ai_player': {
            'name': 'High Mage Secmeton',
            'frontrow': [{'name': 'Aqua Dragon'}, None, None, None, None],
            'hand_names': ['Aqua Dragon', 'Raigeki'],
            'current_turn': 4,
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.HAND), Face.UP)])
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [None, None, None, None, None],
            },
            'ai_player': {
                'name': 'High Mage Secmeton',
                'frontrow': [{'name': 'Aqua Dragon'}, None, None, None, None],
                'hand_names': ['Aqua Dragon', None],
                'current_turn': 4,
            },
        }
    },
    {
        'description': 'Regain control with magic/trap > Traps (Widespread Ruin)',
        'player': {
            'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': Face.UP}, None, None, None, None],
        },
        'ai_player': {
            'name': 'Simon Muran',
            'frontrow': [{'name': 'Aqua Dragon'}, None, None, None, None],
            'hand_names': ['Aqua Dragon', 'Fake Trap',
                           'House of Adhesive Tape', 'Eatgaboon', 'Bear Trap',
                           'Invisible Wire', 'Acid Trap Hole', 'Widespread Ruin'],
            'current_turn': 4,
        },
        'expected_combo': [
            Action([Action.Description(Position(7, Position.Mode.HAND), Face.DOWN)])
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': Face.UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [{'name': 'Aqua Dragon'}, None, None, None, None],
                'backrow': [{'name': 'Widespread Ruin', 'face': Face.DOWN}, None, None, None, None],
                'hand_names': ['Aqua Dragon', 'Fake Trap',
                               'House of Adhesive Tape', 'Eatgaboon', 'Bear Trap',
                               'Invisible Wire', 'Acid Trap Hole', None],
                'current_turn': 4,
            }
        }
    },
    {
        'description': 'Regain control with magic/trap > Swords of Revealing Light',
        'player': {
            'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': Face.UP}, None, None, None, None],
        },
        'ai_player': {
            'name': 'High Mage Secmeton',
            'frontrow': [{'name': 'Aqua Dragon'}, None, None, None, None],
            'hand_names': ['Aqua Dragon', 'Swords of Revealing Light'],
            'current_turn': 4,
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.HAND), Face.UP)])
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': Face.UP}, None, None, None, None],
                'remaining_turns_under_swords': 5
            },
            'ai_player': {
                'name': 'High Mage Secmeton',
                'frontrow': [{'name': 'Aqua Dragon'}, None, None, None, None],
                'hand_names': ['Aqua Dragon', None],
                'current_turn': 4,
            },
        }
    },
    {
        'description': 'Regain control with magic/trap > Dark Hole',
        'player': {
            'frontrow': [
                {'name': 'Twin-headed Thunder Dragon', 'face': Face.UP},
                {'name': 'Twin-headed Thunder Dragon', 'face': Face.UP},
                None,
                None,
                None
            ],
        },
        'ai_player': {
            'name': 'Mai Valentine',
            'frontrow': [{'name': "Harpie's Pet Dragon"}, None, None, None, None],
            'hand_names': ['Harpie Lady Sisters', 'Dark Hole'],
            'current_turn': 4,
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.HAND), Face.UP)])
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [None]*5,
            },
            'ai_player': {
                'name': 'Mai Valentine',
                'frontrow': [None]*5,
                'hand_names': ['Harpie Lady Sisters', None],
                'current_turn': 4,
            },
        }
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
            Action([
                Action.Description(Position(0, Position.Mode.HAND), Face.UP),
                Action.Description(Position(1, Position.Mode.HAND), Face.UP)
            ])
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'B. Dragon Jungle King'}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Pegasus',
                'frontrow': [{'name': "Parrot Dragon"}, {'name': 'Crimson Sunbird', 'face': Face.UP},
                             None, None, None],
                'hand_names': [None, None],
            },
        }
    },
    {
        'description': 'Regain control with a combo > Monster + magic bug',
        'player': {
            'frontrow': [{'name': 'B. Dragon Jungle King', 'face': Face.UP}, None, None, None, None],
        },
        'ai_player': {
            'name': 'Meadow Mage',
            'frontrow': [{'name': "Zanki"}, None, None, None, None],
            'hand_names': ['Lava Battleguard', 'Flame Swordsman', 'Warrior Elimination'],
        },
        'field': 'Wasteland',
        'expected_combo': [
            Action([Action.Description(Position(2, Position.Mode.HAND), Face.UP)])
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'B. Dragon Jungle King', 'face': Face.UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Meadow Mage',
                'frontrow': [{'name': "Zanki"}, None, None, None, None],
                'hand_names': ['Lava Battleguard', 'Flame Swordsman', None],
            },
            'field': 'Wasteland',
        }
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
            'current_turn': 3,
        },
        'expected_combo': [
            Action([Action.Description(Position(2, Position.Mode.HAND), Face.DOWN)])
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'B. Dragon Jungle King'}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Pegasus',
                'frontrow': [None] * 5,
                'backrow': [{'name': 'Invisible Wire', 'face': Face.DOWN}, None, None, None, None],
                'hand_names': ['Dragon Capture Jar', 'Bright Castle', None],
                'current_turn': 3,
            },
        }
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
            Action([Action.Description(Position(1, Position.Mode.HAND), Face.DOWN)])
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'B. Dragon Jungle King'}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Pegasus',
                'frontrow': [None] * 5,
                'backrow': [{'name': 'Bright Castle', 'face': Face.DOWN}, None, None, None, None],
                'hand_names': ['Dragon Capture Jar', None],
            },
        }
    },
    {
        'description': 'Regain control with a combo > No combo play (SET_MAGIC magic)',
        'player': {
            'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': Face.UP}, None, None, None, None],
        },
        'ai_player': {
            'name': 'Desert Mage',
            'frontrow': [None] * 5,
            'backrow': [None] * 5,
            'hand_names': ['Revival of Skeleton Rider', 'Eternal Rest'],
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.HAND), Face.DOWN)])
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': Face.UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Desert Mage',
                'frontrow': [None] * 5,
                'backrow': [{'name': 'Eternal Rest', 'face': Face.DOWN}, None, None, None, None],
                'hand_names': ['Revival of Skeleton Rider', None],
            },
        }
    },
    {
        'description': 'Regain control with a combo > Doing nothing to a monster from the board '
                       '-> compatible field',
        'player': {
            'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': Face.UP}, None, None, None, None],
        },
        'ai_player': {
            'name': 'High Mage Kepura',
            'frontrow': [{'name': 'Gaia the Fierce Knight'}, None, None, None, None],
            'hand_names': ['Judge Man', 'Sogen'],
        },
        'field': 'None',
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.HAND), Face.UP)])
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': Face.UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'High Mage Kepura',
                'frontrow': [{'name': 'Gaia the Fierce Knight'}, None, None, None, None],
                'hand_names': ['Judge Man', None],
            },
            'field': 'Sogen',
        }
    },
    {
        'description': 'Regain control with a combo > Fallback : best max stat in hand',
        'player': {
            'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': Face.UP}, None, None, None, None],
        },
        'ai_player': {
            'name': 'High Mage Kepura',
            'frontrow': [{'name': 'Gaia the Fierce Knight'}, None, None, None, None],
            'hand_names': ['Flame Swordsman', 'Judge Man'],
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.HAND), Face.DOWN)])
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': Face.UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'High Mage Kepura',
                'frontrow': [{'name': 'Gaia the Fierce Knight'}, {'name': 'Judge Man', 'face': Face.DOWN}, None, None, None],
                'hand_names': ['Flame Swordsman', None],
            },
        }
    },
    {
        'description': 'Regain control with a combo > Fallback² : no monsters',
        'player': {
            'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': Face.UP}, None, None, None, None],
        },
        'ai_player': {
            'name': 'High Mage Kepura',
            'frontrow': [{'name': 'Gaia the Fierce Knight'}, None, None, None, None],
            'backrow': [None] * 5,
            'hand_names': ['Zera Ritual', 'Bear Trap', 'Gate Guardian Ritual',
                           'Eternal Draught', 'Winged Trumpeter'],
        },
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.HAND), Face.DOWN)], odds=(1, 5)),
            Action([Action.Description(Position(1, Position.Mode.HAND), Face.DOWN)], odds=(1, 5)),
            Action([Action.Description(Position(2, Position.Mode.HAND), Face.DOWN)], odds=(1, 5)),
            Action([Action.Description(Position(3, Position.Mode.HAND), Face.DOWN)], odds=(1, 5)),
            Action([Action.Description(Position(4, Position.Mode.HAND), Face.DOWN)], odds=(1, 5))
        ]
    },

    # 3b. The AI thinks it has field control
    # 3b1. Clear player's backrow
    {
        'description': "AI thinks it has field control > Clear player's backrow "
                       "TOTAL_DOMINATION (40/30/30)",
        'player': {
            'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': Face.UP}, None, None, None, None],
            'backrow': [{'name': 'Widespread Ruin', 'face': Face.DOWN}, None, None, None, None],
        },
        'ai_player': {
            'name': 'High Mage Kepura',
            'frontrow': [{'name': 'Gate Guardian'}, None, None, None, None],
            'backrow': [None, None, None, None, None],
            'hand_names': ['Flame Swordsman', 'Judge Man', "Harpie's Feather Duster",
                           'Sword of Dark Destruction', 'Sogen'],
            'lp': 8_000
        },
        'field': 'None',
        'expected_combo': [
            Action([Action.Description(Position(2, Position.Mode.HAND), Face.UP)], odds=(50, 100)),
            Action(odds=(50, 100), next_=[
                Action([Action.Description(Position(4, Position.Mode.HAND), Face.UP)], odds=(40, 100)),
                # IMPROVE_MONSTER
                Action([Action.Description(Position(4, Position.Mode.HAND), Face.UP)], odds=(30, 100)),
                # FIND_BEST_COMBO
                Action([Action.Description(Position(3, Position.Mode.HAND), Face.DOWN)], odds=(30, 100))  # SET_MAGIC
            ])
        ]
    },
    {
        'description': "AI thinks it has field control > Clear player's backrow "
                       'LACKS_TOTAL_DOMINATION (20/60/20)',
        'player': {
            'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': Face.UP}, None, None, None, None],
            'backrow': [{'name': 'Widespread Ruin', 'face': Face.DOWN}, None, None, None, None],
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
            'backrow': [None] * 5,
            'hand_names': ['Flame Swordsman', 'Judge Man', "Harpie's Feather Duster",
                           'Sword of Dark Destruction', 'Sogen'],
            'lp': 8_000,
        },
        'field': 'None',
        'expected_combo': [
            Action([Action.Description(Position(2, Position.Mode.HAND), Face.UP)], odds=(50, 100)),
            Action(odds=(50, 100), next_=[
                Action([Action.Description(Position(4, Position.Mode.HAND), Face.UP)], (20, 100)),  # IMPROVE_MONSTER
                Action([Action.Description(Position(4, Position.Mode.HAND), Face.UP)], (60, 100)),  # FIND_BEST_COMBO
                Action([Action.Description(Position(3, Position.Mode.HAND), Face.DOWN)], (20, 100))  # SET_MAGIC
            ])
        ]
    },

    # 3b2. Improve monster if low enough LP
    {
        'description': 'AI thinks it has field control > Improve monster if low enough LP',
        'player': {
            'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': Face.UP}, None, None, None, None],
            'backrow': [{'name': 'Widespread Ruin', 'face': Face.DOWN}, None, None, None, None],
            'hand_names': [],
            'remaining_deck_names': [],
            'lp': 8_000,
        },
        'ai_player': {
            'name': 'High Mage Kepura',
            'frontrow': [{'name': 'Gate Guardian'}, None, None, None, None],
            'backrow': [None] * 5,
            'hand_names': ['Flame Swordsman', 'Judge Man', "Gaia the Dragon Champion",
                           'Sword of Dark Destruction', 'Sogen'],
            'remaining_deck_names': [],
            'lp': 2_000,
        },
        'field': 'None',
        'expected_combo': [
            Action([Action.Description(Position(4, Position.Mode.HAND), Face.UP)])  # IMPROVE_MONSTER
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': Face.UP}, None, None, None, None],
                'backrow': [{'name': 'Widespread Ruin', 'face': Face.DOWN}, None, None, None, None],
                'hand_names': [],
                'remaining_deck_names': [],
                'lp': 8_000,
            },
            'ai_player': {
                'name': 'High Mage Kepura',
                'frontrow': [{'name': 'Gate Guardian'}, None, None, None, None],
                'backrow': [None] * 5,
                'hand_names': ['Flame Swordsman', 'Judge Man', "Gaia the Dragon Champion",
                               'Sword of Dark Destruction', None],
                'remaining_deck_names': [],
                'lp': 2_000,
            },
            'field': 'Sogen',
        }
    }
]

tests_board_ai = [
    {
        'description': 'End of turn',
        'ai_player': {
            'name': 'Simon Muran',
            'frontrow': [None, None, None, None, None],
            'backrow': [None, None, None, None, None],
        },
        'expected_combo': [
            Action([Action.Description(None, EndOfTurn)])
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [None, None, None, None, None],
                'backrow': [None, None, None, None, None],
            },
        }
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
            Action([Action.Description(Position(0, Position.Mode.BACKROW), IsActive.DARKEN)]),
        ],
        'expected_outcome': {
            'player': {
                'backrow': [None, None, None, None, None],
            },
            'ai_player': {
                'name': 'Pegasus',
                'backrow': [{'name': "Harpie's Feather Duster", 'is_active': False}, None, None, None, None],
            },
        }
    },
    {
        'description': "Harpie's",
        'player': {
            'backrow': [{'name': 'Umi'}, None, None, None, None],
            'lp': 8_000,
        },
        'ai_player': {
            'name': 'Pegasus',
            'backrow': [{'name': "Harpie's Feather Duster", 'is_active': True}, None, None, None, None],
            'lp': 8_000,
        },
        'field': 'None',
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), Face.UP)], odds=(75, 100)),
            Action([Action.Description(Position(0, Position.Mode.BACKROW), IsActive.DARKEN)], odds=(25, 100))
        ]
    },
    {
        'description': 'No direct damage due to enemy_LP >= player_LP',
        'player': {
            'lp': 4_000,
        },
        'ai_player': {
            'name': 'Jono',
            'backrow': [
                {'name': 'Tremendous Fire', 'is_active': True},
                {'name': 'Ookazi', 'is_active': True},
                {'name': 'Final Flame', 'is_active': True},
                {'name': 'Hinotama', 'is_active': True},
                {'name': 'Sparks', 'is_active': True}],
            'lp': 4_500,
        },
        'expected_combo': [
            Action([Action.Description(Position(4, Position.Mode.BACKROW), IsActive.DARKEN)]),
        ],
        'expected_outcome': {
            'player': {
                'lp': 4_000,
            },
            'ai_player': {
                'name': 'Jono',
                'backrow': [
                    {'name': 'Tremendous Fire', 'is_active': True},
                    {'name': 'Ookazi', 'is_active': True},
                    {'name': 'Final Flame', 'is_active': True},
                    {'name': 'Hinotama', 'is_active': True},
                    {'name': 'Sparks', 'is_active': False}],
                'lp': 4_500,
            },
        }
    },
    {
        'description': '100% direct damage due to low_LP <= enemy_LP < player_LP',
        'player': {
            'backrow': [None, None, None, None, None],
            'lp': 4_000,
        },
        'ai_player': {
            'name': 'Jono',
            'backrow': [
                {'name': 'Tremendous Fire', 'face': Face.DOWN, 'is_active': True},
                {'name': 'Ookazi', 'face': Face.DOWN, 'is_active': True},
                {'name': 'Final Flame', 'face': Face.DOWN, 'is_active': True},
                {'name': 'Hinotama', 'face': Face.DOWN, 'is_active': True},
                {'name': 'Sparks', 'face': Face.DOWN, 'is_active': True}],
            'lp': 1_000,
        },
        'expected_combo': [
            Action([Action.Description(Position(4, Position.Mode.BACKROW), Face.UP)]),
        ],
        'expected_outcome': {
            'player': {
                'backrow': [None, None, None, None, None],
                'lp': 3_950,
            },
            'ai_player': {
                'name': 'Jono',
                'backrow': [
                    {'name': 'Tremendous Fire', 'face': Face.DOWN, 'is_active': True},
                    {'name': 'Ookazi', 'face': Face.DOWN, 'is_active': True},
                    {'name': 'Final Flame', 'face': Face.DOWN, 'is_active': True},
                    {'name': 'Hinotama', 'face': Face.DOWN, 'is_active': True},
                    None],
                'lp': 1_000,
            },
        }
    },
    {
        'description': 'Partial direct damage due to enemy_LP < low_LP and player backrow is not empty',
        'player': {
            'backrow': [{'name': 'Umi'}, None, None, None, None],
            'lp': 4_000,
        },
        'ai_player': {
            'name': 'Jono',
            'backrow': [
                {'name': 'Tremendous Fire', 'is_active': True},
                {'name': 'Ookazi', 'is_active': True},
                {'name': 'Final Flame', 'is_active': True},
                {'name': 'Hinotama', 'is_active': True},
                {'name': 'Sparks', 'is_active': True}],
            'lp': 980,
        },
        'expected_combo': [
            Action([Action.Description(Position(4, Position.Mode.BACKROW), Face.UP)], odds=(75, 100)),
            Action([Action.Description(Position(4, Position.Mode.BACKROW), IsActive.DARKEN)], odds=(25, 100)),
        ]
    },
    {
        'description': 'Equip',
        'ai_player': {
            'name': 'Heishin',
            'frontrow': [
                None,
                {'name': 'B. Skull Dragon'},
                {'name': 'Meteor B. Dragon'},
                None,
                None
            ],
            'backrow': [{'name': 'Megamorph', 'is_active': True}, None, None, None, None],
        },
        'expected_combo': [
            Action([Action.Description(
                Position(0, Position.Mode.BACKROW),
                Face.UP,
                Position(1, Position.Mode.FRONTROW)
            )]),
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Heishin',
                'frontrow': [
                    None,
                    {'name': 'B. Skull Dragon', 'equip_stage': 2},
                    {'name': 'Meteor B. Dragon'},
                    None,
                    None
                ],
                'backrow': [None, None, None, None, None],
            },
        }
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
            Action([Action.Description(
                Position(0, Position.Mode.BACKROW),
                Face.UP,
                Position(1, Position.Mode.FRONTROW)
            )]),
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'High Mage Kepura',
                'frontrow': [
                    {'name': 'Gate Guardian'},
                    {'name': 'Gaia the Fierce Knight', 'equip_stage': 1},
                    {'name': 'Gaia the Fierce Knight'},
                    None,
                    None],
                'backrow': [None, None, None, None, None],
            },
        }
    },
    {
        'description': 'No equip due to no compatibility',
        'ai_player': {
            'name': 'High Mage Kepura',
            'frontrow': [{'name': 'Gate Guardian'}, None, None, None, None],
            'backrow': [{'name': 'Legendary Sword', 'is_active': True}, None, None, None, None],
        },
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), IsActive.DARKEN)]),
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'High Mage Kepura',
                'frontrow': [{'name': 'Gate Guardian'}, None, None, None, None],
                'backrow': [{'name': 'Legendary Sword', 'is_active': False}, None, None, None, None],
            },
        }
    },
    {
        'description': 'Successful ritual',
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
            Action([Action.Description(Position(0, Position.Mode.BACKROW), Face.UP)]),
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Seto 3rd',
                'frontrow': [
                    None,
                    {'name': 'Black Luster Soldier', 'face': Face.UP},
                    None,
                    None,
                    None],
                'backrow': [None, None, None, None, None],
            },
        }
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
            Action([Action.Description(Position(0, Position.Mode.BACKROW), IsActive.DARKEN)]),
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Seto 3rd',
                'frontrow': [
                    {'name': 'Beaver Warrior'},
                    {'name': 'Gaia the Fierce Knight'},
                    None,
                    None,
                    None],
                'backrow': [{'name': 'Black Luster Ritual', 'is_active': False}, None, None, None, None],
            },
        }
    },
    {
        'description': 'Dark-Piercing Light',
        'player': {
            'frontrow': [
                {'name': 'Nemuriko', 'battle_mode': BattleMode.ATTACK, 'face': Face.DOWN},
                {'name': 'Nemuriko', 'battle_mode': BattleMode.DEFENSE, 'face': Face.DOWN},
                None,
                None,
                None
            ],
            'backrow': [{'name': 'Invigoration', 'face': Face.DOWN}, None, None, None, None]
        },
        'ai_player': {
            'name': 'Villager1',
            'frontrow': [{'name': 'Skull Servant'}, None, None, None, None],
            'backrow': [{'name': 'Dark-piercing Light', 'is_active': True}, None, None, None, None],
        },
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), Face.UP)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [
                    {'name': 'Nemuriko', 'battle_mode': BattleMode.ATTACK, 'face': Face.UP},
                    {'name': 'Nemuriko', 'battle_mode': BattleMode.DEFENSE, 'face': Face.UP},
                    None,
                    None,
                    None
                ],
                'backrow': [{'name': 'Invigoration', 'face': Face.DOWN}, None, None, None, None]
            },
            'ai_player': {
                'name': 'Villager1',
                'frontrow': [{'name': 'Skull Servant'}, None, None, None, None],
                'backrow': [None, None, None, None, None],
            },
        }
    },
    {
        'description': 'Failed Dark-Piercing Light because at least one monster is face-up',
        'player': {
            'frontrow': [
                {'name': 'Nemuriko', 'face': Face.DOWN},
                {'name': 'Nemuriko', 'face': Face.UP},
                None,
                None,
                None
            ],
        },
        'ai_player': {
            'name': 'Villager1',
            'frontrow': [{'name': 'Skull Servant'}, None, None, None, None],
            'backrow': [{'name': 'Dark-piercing Light', 'is_active': True}, None, None, None, None],
        },
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), IsActive.DARKEN)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [
                    {'name': 'Nemuriko', 'face': Face.DOWN},
                    {'name': 'Nemuriko', 'face': Face.UP},
                    None,
                    None,
                    None
                ],
            },
            'ai_player': {
                'name': 'Villager1',
                'frontrow': [{'name': 'Skull Servant'}, None, None, None, None],
                'backrow': [{'name': 'Dark-piercing Light', 'is_active': False}, None, None, None, None],
            },
        }
    },
    {
        'description': 'Failed Dark-Piercing Light because player_monsters <= ai_monsters',
        'player': {
            'frontrow': [{'name': 'Nemuriko', 'face': Face.DOWN}, None, None, None, None],
        },
        'ai_player': {
            'name': 'Villager1',
            'frontrow': [{'name': 'Skull Servant'}, None, None, None, None],
            'backrow': [{'name': 'Dark-piercing Light', 'is_active': True}, None, None, None, None],
        },
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), IsActive.DARKEN)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'Nemuriko', 'face': Face.DOWN}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Villager1',
                'frontrow': [{'name': 'Skull Servant'}, None, None, None, None],
                'backrow': [{'name': 'Dark-piercing Light', 'is_active': False}, None, None, None, None],
            },
        }
    },
    {
        'description': 'Swords of Revealing Light',
        'player': {
            'frontrow': [
                {'name': 'Nemuriko', 'battle_mode': BattleMode.ATTACK, 'face': Face.UP},
                {'name': 'Nemuriko', 'battle_mode': BattleMode.DEFENSE, 'face': Face.DOWN},
                None,
                None,
                None
            ],
            'remaining_turns_under_swords': 0
        },
        'ai_player': {
            'name': 'Meadow Mage',
            'frontrow': [None, None, None, None, None],
            'backrow': [{'name': 'Swords of Revealing Light', 'is_active': True}, None, None, None, None],
        },
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), Face.UP)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [
                    {'name': 'Nemuriko', 'battle_mode': BattleMode.ATTACK, 'face': Face.UP},
                    {'name': 'Nemuriko', 'battle_mode': BattleMode.DEFENSE, 'face': Face.UP},
                    None,
                    None,
                    None
                ],
                'remaining_turns_under_swords': 5
            },
            'ai_player': {
                'name': 'Meadow Mage',
                'frontrow': [None, None, None, None, None],
                'backrow': [None, None, None, None, None],
            },
        }
    },
    {
        'description': 'Swords of Revealing Light #2',
        'player': {
            'frontrow': [{'name': 'Thousand Dragon', 'face': Face.UP}, None, None, None, None],
            'remaining_turns_under_swords': 0
        },
        'ai_player': {
            'name': 'Meadow Mage',
            'frontrow': [{'name': 'Judge Man'}, None, None, None, None],
            'backrow': [{'name': 'Swords of Revealing Light', 'is_active': True}, None, None, None, None],
        },
        'field': 'None',
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), Face.UP)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'Thousand Dragon', 'face': Face.UP}, None, None, None, None],
                'remaining_turns_under_swords': 5
            },
            'ai_player': {
                'name': 'Meadow Mage',
                'frontrow': [{'name': 'Judge Man'}, None, None, None, None],
                'backrow': [None, None, None, None, None],
            },
            'field': 'None',
        }
    },
    {
        'description': 'No Swords of Revealing Light due to player already being under its effect',
        'player': {
            'frontrow': [{'name': 'Thousand Dragon', 'face': Face.UP}, None, None, None, None],
            'remaining_turns_under_swords': 1
        },
        'ai_player': {
            'name': 'Meadow Mage',
            'frontrow': [{'name': 'Judge Man'}, None, None, None, None],
            'backrow': [{'name': 'Swords of Revealing Light', 'is_active': True}, None, None, None, None],
        },
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), IsActive.DARKEN)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'Thousand Dragon', 'face': Face.UP}, None, None, None, None],
                'remaining_turns_under_swords': 1
            },
            'ai_player': {
                'name': 'Meadow Mage',
                'frontrow': [{'name': 'Judge Man'}, None, None, None, None],
                'backrow': [{'name': 'Swords of Revealing Light', 'is_active': False}, None, None, None, None],
            },
        }
    },
    {
        'description': 'No Swords of Revealing Light due to AI having control',
        'player': {
            'frontrow': [{'name': 'Thousand Dragon', 'face': Face.UP}, None, None, None, None],
            'remaining_turns_under_swords': 1
        },
        'ai_player': {
            'name': 'Meadow Mage',
            'frontrow': [{'name': 'Judge Man'}, None, None, None, None],
            'backrow': [{'name': 'Swords of Revealing Light', 'is_active': True}, None, None, None, None],
        },
        'field': 'Sogen',
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), IsActive.DARKEN)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'Thousand Dragon', 'face': Face.UP}, None, None, None, None],
                'remaining_turns_under_swords': 1
            },
            'ai_player': {
                'name': 'Meadow Mage',
                'frontrow': [{'name': 'Judge Man'}, None, None, None, None],
                'backrow': [{'name': 'Swords of Revealing Light', 'is_active': False}, None, None, None, None],
            },
            'field': 'Sogen',
        }
    },
    {
        'description': 'Stop Defense due to lethal',
        'player': {
            'frontrow': [
                {'name': 'Thousand Dragon', 'battle_mode': BattleMode.DEFENSE, 'face': Face.UP, 'equip_stage': 0},
                {'name': 'Twin-headed Thunder Dragon', 'face': Face.UP, 'equip_stage': 0},
                None,
                None,
                None
            ],
            'lp': 200
        },
        'ai_player': {
            'name': 'Bandit Keith',
            'frontrow': [{'name': 'Zoa', 'equip_stage': 0}, None, None, None, None],
            'backrow': [{'name': 'Stop Defense', 'is_active': True}, None, None, None, None],
            'remaining_turns_under_swords': 0,
        },
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), Face.UP)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [
                    {'name': 'Thousand Dragon', 'battle_mode': BattleMode.ATTACK, 'face': Face.UP, 'equip_stage': 0},
                    {'name': 'Twin-headed Thunder Dragon', 'face': Face.UP, 'equip_stage': 0},
                    None,
                    None,
                    None
                ],
                'lp': 200
            },
            'ai_player': {
                'name': 'Bandit Keith',
                'frontrow': [{'name': 'Zoa', 'equip_stage': 0}, None, None, None, None],
                'backrow': [None, None, None, None, None],
                'remaining_turns_under_swords': 0,
            },
        }
    },
    {
        'description': "Stop Defense due to AI being able to clear player's visible board",
        'player': {
            'frontrow': [
                {'name': 'Thousand Dragon', 'battle_mode': BattleMode.DEFENSE, 'face': Face.UP},
                {'name': 'Twin-headed Thunder Dragon', 'battle_mode': BattleMode.DEFENSE, 'face': Face.DOWN},
                {'name': 'B. Dragon Jungle King', 'battle_mode': BattleMode.DEFENSE, 'face': Face.UP},
                None,
                None
            ],
            'lp': 8_000
        },
        'ai_player': {
            'name': 'Bandit Keith',
            'frontrow': [
                {'name': 'Zoa', 'face': Face.UP, 'equip_stage': 0},
                {'name': 'Zoa', 'face': Face.DOWN, 'equip_stage': 0},
                None,
                None,
                None
            ],
            'backrow': [{'name': 'Stop Defense', 'is_active': True}, None, None, None, None],
            'remaining_turns_under_swords': 0,
        },
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), Face.UP)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [
                    {'name': 'Thousand Dragon', 'battle_mode': BattleMode.ATTACK, 'face': Face.UP},
                    {'name': 'Twin-headed Thunder Dragon', 'battle_mode': BattleMode.ATTACK, 'face': Face.DOWN},
                    {'name': 'B. Dragon Jungle King', 'battle_mode': BattleMode.ATTACK, 'face': Face.UP},
                    None,
                    None
                ],
                'lp': 8_000
            },
            'ai_player': {
                'name': 'Bandit Keith',
                'frontrow': [
                    {'name': 'Zoa', 'face': Face.UP, 'equip_stage': 0},
                    {'name': 'Zoa', 'face': Face.DOWN, 'equip_stage': 0},
                    None,
                    None,
                    None
                ],
                'backrow': [None, None, None, None, None],
                'remaining_turns_under_swords': 0,
            },
        }
    },
    {
        'description': 'No Stop Defense due to AI being under Swords',
        'player': {
            'frontrow': [
                {'name': 'Thousand Dragon', 'face': Face.UP},
                {'name': 'Twin-headed Thunder Dragon', 'face': Face.DOWN},
                {'name': 'B. Dragon Jungle King', 'face': Face.UP},
                None,
                None
            ],
        },
        'ai_player': {
            'name': 'Bandit Keith',
            'frontrow': [
                {'name': 'Zoa', 'face': Face.UP, 'equip_stage': 0},
                {'name': 'Zoa', 'face': Face.DOWN, 'equip_stage': 0},
                None,
                None,
                None
            ],
            'backrow': [{'name': 'Stop Defense', 'is_active': True}, None, None, None, None],
            'remaining_turns_under_swords': 1
        },
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), IsActive.DARKEN)]),
        ],
        'expected_outcome': {

            'player': {
                'frontrow': [
                    {'name': 'Thousand Dragon', 'face': Face.UP},
                    {'name': 'Twin-headed Thunder Dragon', 'face': Face.DOWN},
                    {'name': 'B. Dragon Jungle King', 'face': Face.UP},
                    None,
                    None
                ],
            },
            'ai_player': {
                'name': 'Bandit Keith',
                'frontrow': [
                    {'name': 'Zoa', 'face': Face.UP, 'equip_stage': 0},
                    {'name': 'Zoa', 'face': Face.DOWN, 'equip_stage': 0},
                    None,
                    None,
                    None
                ],
                'backrow': [{'name': 'Stop Defense', 'is_active': False}, None, None, None, None],
                'remaining_turns_under_swords': 1
            },
        }
    },
    {
        'description': 'No Stop Defense due to AI having no monster',
        'player': {
            'frontrow': [
                {'name': 'Thousand Dragon', 'face': Face.UP},
                {'name': 'Twin-headed Thunder Dragon', 'face': Face.DOWN},
                {'name': 'B. Dragon Jungle King', 'face': Face.UP},
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
            Action([Action.Description(Position(0, Position.Mode.BACKROW), IsActive.DARKEN)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [
                    {'name': 'Thousand Dragon', 'face': Face.UP},
                    {'name': 'Twin-headed Thunder Dragon', 'face': Face.DOWN},
                    {'name': 'B. Dragon Jungle King', 'face': Face.UP},
                    None,
                    None
                ],
            },
            'ai_player': {
                'name': 'Bandit Keith',
                'frontrow': [None, None, None, None, None],
                'backrow': [{'name': 'Stop Defense', 'is_active': False}, None, None, None, None],
                'remaining_turns_under_swords': 0
            },
        }
    },
    {
        'description': 'No Stop Defense because no lethal and no visible board clear',
        'player': {
            'frontrow': [
                {'name': 'B. Dragon Jungle King', 'face': Face.UP},
                {'name': 'Twin-headed Thunder Dragon', 'face': Face.UP},
                None,
                None,
                None
            ],
            'lp': 8_000
        },
        'ai_player': {
            'name': 'Bandit Keith',
            'frontrow': [
                {'name': 'Zoa', 'face': Face.UP, 'equip_stage': 0},
                {'name': 'Zoa', 'face': Face.DOWN, 'equip_stage': 0},
                None,
                None,
                None
            ],
            'backrow': [{'name': 'Stop Defense', 'is_active': True}, None, None, None, None],
            'remaining_turns_under_swords': 0
        },
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), IsActive.DARKEN)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [
                    {'name': 'B. Dragon Jungle King', 'face': Face.UP},
                    {'name': 'Twin-headed Thunder Dragon', 'face': Face.UP},
                    None,
                    None,
                    None
                ],
                'lp': 8_000
            },
            'ai_player': {
                'name': 'Bandit Keith',
                'frontrow': [
                    {'name': 'Zoa', 'face': Face.UP, 'equip_stage': 0},
                    {'name': 'Zoa', 'face': Face.DOWN, 'equip_stage': 0},
                    None,
                    None,
                    None
                ],
                'backrow': [{'name': 'Stop Defense', 'is_active': False}, None, None, None, None],
                'remaining_turns_under_swords': 0
            },
        }
    },
    {
        'description': 'Destroy type (Dragon)',
        'player': {
            'frontrow': [
                {'name': 'Meteor B. Dragon', 'face': Face.UP},
                {'name': 'Doron'},
                {'name': 'Blue-eyes White Dragon', 'face': Face.DOWN},
                None,
                None
            ],
        },
        'ai_player': {
            'name': 'Mountain Mage',
            'frontrow': [None, None, None, None, None],
            'backrow': [{'name': 'Dragon Capture Jar', 'is_active': True}, None, None, None, None],
        },
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), Face.UP)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [
                    None,
                    {'name': 'Doron'},
                    None,
                    None,
                    None
                ],
            },
            'ai_player': {
                'name': 'Mountain Mage',
                'frontrow': [None, None, None, None, None],
                'backrow': [None, None, None, None, None],
            },
        }
    },
    {
        'description': 'Destroy type (Warrior)',
        'player': {
            'frontrow': [
                {'name': 'Gaia the Fierce Knight', 'face': Face.UP},
                {'name': 'Ameba'},
                None,
                None,
                None
            ],
        },
        'ai_player': {
            'name': 'Meadow Mage',
            'frontrow': [None, None, None, None, None],
            'backrow': [{'name': 'Warrior Elimination', 'is_active': True}, None, None, None, None],
        },
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), Face.UP)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [
                    None,
                    {'name': 'Ameba'},
                    None,
                    None,
                    None
                ],
            },
            'ai_player': {
                'name': 'Meadow Mage',
                'frontrow': [None, None, None, None, None],
                'backrow': [None, None, None, None, None],
            },
        }
    },
    {
        'description': 'Destroy type (Zombie)',
        'player': {
            'frontrow': [
                {'name': 'Dragon Zombie', 'face': Face.UP},
                {'name': 'Ameba'},
                None,
                None,
                None
            ],
        },
        'ai_player': {
            'name': 'Desert Mage',
            'frontrow': [None, None, None, None, None],
            'backrow': [{'name': 'Eternal Rest', 'is_active': True}, None, None, None, None],
        },
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), Face.UP)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [
                    None,
                    {'name': 'Ameba'},
                    None,
                    None,
                    None
                ],
            },
            'ai_player': {
                'name': 'Desert Mage',
                'frontrow': [None, None, None, None, None],
                'backrow': [None, None, None, None, None],
            },
        }
    },
    {
        'description': 'Destroy type (Machine)',
        'player': {
            'frontrow': [
                {'name': 'Metalzoa', 'face': Face.UP},
                {'name': 'Ameba'},
                None,
                None,
                None
            ],
        },
        'ai_player': {
            'name': 'Labyrinth Mage',
            'frontrow': [None, None, None, None, None],
            'backrow': [{'name': 'Stain Storm', 'is_active': True}, None, None, None, None],
        },
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), Face.UP)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [
                    None,
                    {'name': 'Ameba'},
                    None,
                    None,
                    None
                ],
            },
            'ai_player': {
                'name': 'Labyrinth Mage',
                'frontrow': [None, None, None, None, None],
                'backrow': [None, None, None, None, None],
            },
        }
    },
    {
        'description': 'Destroy type (Insect)',
        'player': {
            'frontrow': [
                {'name': 'Kwagar Hercules', 'face': Face.UP},
                {'name': 'Ameba'},
                None,
                None,
                None
            ],
        },
        'ai_player': {
            'name': 'Forest Mage',
            'frontrow': [None, None, None, None, None],
            'backrow': [{'name': 'Eradicating Aerosol', 'is_active': True}, None, None, None, None],
        },
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), Face.UP)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [
                    None,
                    {'name': 'Ameba'},
                    None,
                    None,
                    None
                ],
            },
            'ai_player': {
                'name': 'Forest Mage',
                'frontrow': [None, None, None, None, None],
                'backrow': [None, None, None, None, None],
            },
        }
    },
    {
        'description': 'Destroy type (Rock)',
        'player': {
            'frontrow': [
                {'name': 'Stone D.', 'face': Face.UP},
                {'name': 'Ameba'},
                None,
                None,
                None
            ],
        },
        'ai_player': {
            'name': 'Desert Mage',
            'frontrow': [None, None, None, None, None],
            'backrow': [{'name': 'Breath of Light', 'is_active': True}, None, None, None, None],
        },
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), Face.UP)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [
                    None,
                    {'name': 'Ameba'},
                    None,
                    None,
                    None
                ],
            },
            'ai_player': {
                'name': 'Desert Mage',
                'frontrow': [None, None, None, None, None],
                'backrow': [None, None, None, None, None],
            },
        }
    },
    {
        'description': 'Destroy type (Fish)',
        'player': {
            'frontrow': [
                {'name': '7 Colored Fish', 'face': Face.UP},
                {'name': 'Ameba'},
                None,
                None,
                None
            ],
        },
        'ai_player': {
            'name': 'Desert Mage',
            'frontrow': [None, None, None, None, None],
            'backrow': [{'name': 'Eternal Draught', 'is_active': True}, None, None, None, None],
        },
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), Face.UP)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [
                    None,
                    {'name': 'Ameba'},
                    None,
                    None,
                    None
                ],
            },
            'ai_player': {
                'name': 'Desert Mage',
                'frontrow': [None, None, None, None, None],
                'backrow': [None, None, None, None, None],
            },
        }
    },
    {
        'description': 'No Destroy type due to AI having control',
        'player': {
            'frontrow': [{'name': '7 Colored Fish', 'face': Face.UP}, None, None, None, None],
        },
        'ai_player': {
            'name': 'Desert Mage',
            'frontrow': [{'name': 'Stone D.'}, None, None, None, None],
            'backrow': [{'name': 'Eternal Draught', 'is_active': True}, None, None, None, None],
        },
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), IsActive.DARKEN)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': '7 Colored Fish', 'face': Face.UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Desert Mage',
                'frontrow': [{'name': 'Stone D.'}, None, None, None, None],
                'backrow': [{'name': 'Eternal Draught', 'is_active': False}, None, None, None, None],
            },
        }
    },
    {
        'description': "No Destroy type due to non matching player's best card type",
        'player': {
            'frontrow': [
                {'name': '7 Colored Fish', 'face': Face.UP},
                {'name': 'Stone D.', 'face': Face.UP},
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
            Action([Action.Description(Position(0, Position.Mode.BACKROW), IsActive.DARKEN)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [
                    {'name': '7 Colored Fish', 'face': Face.UP},
                    {'name': 'Stone D.', 'face': Face.UP},
                    None,
                    None,
                    None
                ],
            },
            'ai_player': {
                'name': 'Desert Mage',
                'frontrow': [{'name': 'Stone D.'}, None, None, None, None],
                'backrow': [{'name': 'Eternal Draught', 'is_active': False}, None, None, None, None],
            },
        }
    },
    {
        'description': 'Lower stats (Spellbinding Circle)',
        'player': {
            'frontrow': [{'name': 'Stone D.', 'face': Face.UP}, None, None, None, None],
        },
        'ai_player': {
            'name': 'Isis',
            'frontrow': [{'name': 'Aqua Dragon'}, None, None, None, None],
            'backrow': [{'name': 'Spellbinding Circle', 'is_active': True}, None, None, None, None],
        },
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), Face.UP)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'Stone D.', 'face': Face.UP, 'equip_stage': -1}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Isis',
                'frontrow': [{'name': 'Aqua Dragon'}, None, None, None, None],
                'backrow': [None, None, None, None, None],
            },
        }
    },
    {
        'description': 'Lower stats (Shadow Spell)',
        'player': {
            'frontrow': [{'name': 'Stone D.', 'face': Face.UP}, None, None, None, None],
        },
        'ai_player': {
            'name': 'Kaiba',
            'frontrow': [{'name': 'Parrot Dragon'}, None, None, None, None],
            'backrow': [{'name': 'Shadow Spell', 'is_active': True}, None, None, None, None],
        },
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), Face.UP)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'Stone D.', 'face': Face.UP, 'equip_stage': -2}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Kaiba',
                'frontrow': [{'name': 'Parrot Dragon'}, None, None, None, None],
                'backrow': [None, None, None, None, None],
            },
        }
    },
    {
        'description': 'No Lower stats due to AI having control',
        'player': {
            'frontrow': [{'name': 'Kaminari Attack', 'face': Face.UP}, None, None, None, None],
        },
        'ai_player': {
            'name': 'Kaiba',
            'frontrow': [{'name': 'Parrot Dragon'}, None, None, None, None],
            'backrow': [{'name': 'Shadow Spell', 'is_active': True}, None, None, None, None],
        },
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), IsActive.DARKEN)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'Kaminari Attack', 'face': Face.UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Kaiba',
                'frontrow': [{'name': 'Parrot Dragon'}, None, None, None, None],
                'backrow': [{'name': 'Shadow Spell', 'is_active': False}, None, None, None, None],
            },
        }
    },
    {
        'description': 'Crush Card',
        'player': {
            'frontrow': [
                {'name': 'Stone D.', 'face': Face.UP},
                {'name': 'Doron'},
                None,
                None,
                None
            ],
        },
        'ai_player': {
            'name': 'Kaiba',
            'frontrow': [{'name': 'Parrot Dragon'}, None, None, None, None],
            'backrow': [{'name': 'Crush Card', 'is_active': True}, None, None, None, None],
        },
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), Face.UP)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [
                    None,
                    {'name': 'Doron'},
                    None,
                    None,
                    None
                ],
            },
            'ai_player': {
                'name': 'Kaiba',
                'frontrow': [{'name': 'Parrot Dragon'}, None, None, None, None],
                'backrow': [None, None, None, None, None],
            },
        }
    },
    {
        'description': 'No Crush Card due to AI having control',
        'player': {
            'frontrow': [{'name': 'Kaminari Attack', 'face': Face.UP}, None, None, None, None],
        },
        'ai_player': {
            'name': 'Kaiba',
            'frontrow': [{'name': 'Parrot Dragon'}, None, None, None, None],
            'backrow': [{'name': 'Crush Card', 'is_active': True}, None, None, None, None],
        },
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), IsActive.DARKEN)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'Kaminari Attack', 'face': Face.UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Kaiba',
                'frontrow': [{'name': 'Parrot Dragon'}, None, None, None, None],
                'backrow': [{'name': 'Crush Card', 'is_active': False}, None, None, None, None],
            },
        }
    },
    {
        'description': 'No Crush Card due to player having too low Attack',
        'player': {
            'frontrow': [{'name': 'Hibikime', 'face': Face.UP}, None, None, None, None],
        },
        'ai_player': {
            'name': 'Kaiba',
            'frontrow': [None, None, None, None, None],
            'backrow': [{'name': 'Crush Card', 'is_active': True}, None, None, None, None],
        },
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), IsActive.DARKEN)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'Hibikime', 'face': Face.UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Kaiba',
                'frontrow': [None, None, None, None, None],
                'backrow': [{'name': 'Crush Card', 'is_active': False}, None, None, None, None],
            },
        }
    },
    {
        'description': 'Raigeki',
        'player': {
            'frontrow': [{'name': 'Meteor B. Dragon'}, {'name': 'Twin-headed Thunder Dragon'}, None, None, None],
        },
        'ai_player': {
            'name': 'Seto 3rd',
            'frontrow': [{'name': 'B. Skull Dragon'}, None, None, None, None],
            'backrow': [{'name': 'Raigeki', 'is_active': True}, None, None, None, None],
        },
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), Face.UP)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [None, None, None, None, None],
            },
            'ai_player': {
                'name': 'Seto 3rd',
                'frontrow': [{'name': 'B. Skull Dragon'}, None, None, None, None],
                'backrow': [None, None, None, None, None],
            },
        }
    },
    {
        'description': 'No Raigeki due to player having stricly fewer visible monsters than the AI',
        'player': {
            'frontrow': [
                {'name': 'Meteor B. Dragon', 'face': Face.DOWN},
                {'name': 'Twin-headed Thunder Dragon', 'face': Face.UP},
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
            Action([Action.Description(Position(0, Position.Mode.BACKROW), IsActive.DARKEN)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [
                    {'name': 'Meteor B. Dragon', 'face': Face.DOWN},
                    {'name': 'Twin-headed Thunder Dragon', 'face': Face.UP},
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
                'backrow': [{'name': 'Raigeki', 'is_active': False}, None, None, None, None],
            },
        }
    },
    {
        'description': "Field (player's best card is not boosted)",
        'player': {
            'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': Face.UP}, None, None, None, None],
        },
        'ai_player': {
            'name': 'Meadow Mage',
            'frontrow': [{'name': 'Judge Man'}, None, None, None, None],
            'backrow': [{'name': 'Sogen', 'is_active': True}, None, None, None, None],
        },
        'field': 'Umi',
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), Face.UP)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': Face.UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Meadow Mage',
                'frontrow': [{'name': 'Judge Man'}, None, None, None, None],
                'backrow': [None, None, None, None, None],
            },
            'field': 'Sogen',
        }
    },
    {
        'description': "Field (AI's best card is boosted)",
        'player': {
            'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': Face.UP}, None, None, None, None],
        },
        'ai_player': {
            'name': 'Ocean Mage',
            'frontrow': [{'name': 'Aqua Dragon'}, None, None, None, None],
            'backrow': [{'name': 'Umi', 'is_active': True}, None, None, None, None],
        },
        'field': 'Mountain',
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), Face.UP)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': Face.UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Ocean Mage',
                'frontrow': [{'name': 'Aqua Dragon'}, None, None, None, None],
                'backrow': [None, None, None, None, None],
            },
            'field': 'Umi',
        }
    },
    {
        'description': 'Field due to default type being Dragon when the AI has no monster on the board',
        'player': {
            'frontrow': [{'name': 'Kairyu-shin', 'face': Face.UP}, None, None, None, None],
        },
        'ai_player': {
            'name': 'Mountain Mage',
            'frontrow': [None, None, None, None, None],
            'backrow': [{'name': 'Mountain', 'is_active': True}, None, None, None, None],
        },
        'field': 'None',
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), Face.UP)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'Kairyu-shin', 'face': Face.UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Mountain Mage',
                'frontrow': [None, None, None, None, None],
                'backrow': [None, None, None, None, None],
            },
            'field': 'Mountain',
        }
    },
    {
        'description': 'No field due to AI having field control',
        'player': {
            'frontrow': [{'name': 'Curse of Dragon', 'face': Face.UP}, None, None, None, None],
        },
        'ai_player': {
            'name': 'Ocean Mage',
            'frontrow': [{'name': 'Aqua Dragon'}, None, None, None, None],
            'backrow': [{'name': 'Umi', 'is_active': True}, None, None, None, None],
        },
        'field': 'None',
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), IsActive.DARKEN)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'Curse of Dragon', 'face': Face.UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Ocean Mage',
                'frontrow': [{'name': 'Aqua Dragon'}, None, None, None, None],
                'backrow': [{'name': 'Umi', 'is_active': False}, None, None, None, None],
            },
            'field': 'None',
        }
    },
    {
        'description': 'No field due to field already being of the would-be new type',
        'player': {
            'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': Face.UP}, None, None, None, None],
        },
        'ai_player': {
            'name': 'Ocean Mage',
            'frontrow': [{'name': 'Aqua Dragon'}, None, None, None, None],
            'backrow': [{'name': 'Umi', 'is_active': True}, None, None, None, None],
        },
        'field': 'Umi',
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), IsActive.DARKEN)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': Face.UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Ocean Mage',
                'frontrow': [{'name': 'Aqua Dragon'}, None, None, None, None],
                'backrow': [{'name': 'Umi', 'is_active': False}, None, None, None, None],
            },
            'field': 'Umi',
        }
    },
    {
        'description': "No field due to field boosting the player's best card",
        'player': {
            'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': Face.UP}, None, None, None, None],
        },
        'ai_player': {
            'name': 'Ocean Mage',
            'frontrow': [{'name': 'Aqua Dragon'}, None, None, None, None],
            'backrow': [{'name': 'Umi', 'is_active': True}, None, None, None, None],
        },
        'field': 'None',
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), IsActive.DARKEN)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'Twin-headed Thunder Dragon', 'face': Face.UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Ocean Mage',
                'frontrow': [{'name': 'Aqua Dragon'}, None, None, None, None],
                'backrow': [{'name': 'Umi', 'is_active': False}, None, None, None, None],
            },
            'field': 'None',
        }
    },
    {
        'description': 'No field due to field not weakening player and not boosting AI',
        'player': {
            'frontrow': [{'name': 'Thousand Dragon', 'face': Face.UP}, None, None, None, None],
        },
        'ai_player': {
            'name': 'Ocean Mage',
            'frontrow': [{'name': 'Parrot Dragon'}, None, None, None, None],
            'backrow': [{'name': 'Umi', 'is_active': True}, None, None, None, None],
        },
        'field': 'None',
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), IsActive.DARKEN)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'Thousand Dragon', 'face': Face.UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Ocean Mage',
                'frontrow': [{'name': 'Parrot Dragon'}, None, None, None, None],
                'backrow': [{'name': 'Umi', 'is_active': False}, None, None, None, None],
            },
            'field': 'None',
        }
    },
    {
        'description': 'No field due to default AI type being Dragon when no monster is on the board',
        'player': {
            'frontrow': [{'name': 'Thousand Dragon', 'face': Face.UP}, None, None, None, None],
        },
        'ai_player': {
            'name': 'Ocean Mage',
            'frontrow': [None, None, None, None, None],
            'backrow': [{'name': 'Umi', 'is_active': True}, None, None, None, None],
        },
        'field': 'None',
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), IsActive.DARKEN)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'Thousand Dragon', 'face': Face.UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Ocean Mage',
                'frontrow': [None, None, None, None, None],
                'backrow': [{'name': 'Umi', 'is_active': False}, None, None, None, None],
            },
            'field': 'None',
        }
    },
    {
        'description': 'Dark Hole',
        'player': {
            'frontrow': [
                {'name': 'Thousand Dragon', 'face': Face.UP},
                {'name': 'B. Dragon Jungle King', 'face': Face.DOWN},
                None,
                None,
                None
            ],
            'backrow': [{'name': 'Widespread Ruin'}, None, None, None, None]
        },
        'ai_player': {
            'name': 'Yami Bakura',
            'frontrow': [{'name': 'Aqua Madoor'}, None, None, None, None],
            'backrow': [{'name': 'Dark Hole', 'is_active': True}, None, None, None, None],
        },
        'field': 'None',
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), Face.UP)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [
                    None,
                    None,
                    None,
                    None,
                    None
                ],
                'backrow': [None, None, None, None, None]
            },
            'ai_player': {
                'name': 'Yami Bakura',
                'frontrow': [None, None, None, None, None],
                'backrow': [None, None, None, None, None],
            },
            'field': 'None',
        }
    },
    {
        'description': 'No Dark Hole due to AI having field control',
        'player': {
            'frontrow': [{'name': 'Queen of Autumn Leaves', 'face': Face.UP}, None, None, None, None],
        },
        'ai_player': {
            'name': 'Yami Bakura',
            'frontrow': [{'name': 'Aqua Madoor'}, None, None, None, None],
            'backrow': [{'name': 'Dark Hole', 'is_active': True}, None, None, None, None],
        },
        'field': 'None',
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), IsActive.DARKEN)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'Queen of Autumn Leaves', 'face': Face.UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Yami Bakura',
                'frontrow': [{'name': 'Aqua Madoor'}, None, None, None, None],
                'backrow': [{'name': 'Dark Hole', 'is_active': False}, None, None, None, None],
            },
            'field': 'None',
        }
    },
    {
        'description': 'No Dark Hole due to #player monsters <= #ai monsters',
        'player': {
            'frontrow': [{'name': 'Thousand Dragon', 'face': Face.UP}, None, None, None, None],
        },
        'ai_player': {
            'name': 'Yami Bakura',
            'frontrow': [{'name': 'Aqua Madoor'}, None, None, None, None],
            'backrow': [{'name': 'Dark Hole', 'is_active': True}, None, None, None, None],
        },
        'field': 'None',
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.BACKROW), IsActive.DARKEN)]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [{'name': 'Thousand Dragon', 'face': Face.UP}, None, None, None, None],
            },
            'ai_player': {
                'name': 'Yami Bakura',
                'frontrow': [{'name': 'Aqua Madoor'}, None, None, None, None],
                'backrow': [{'name': 'Dark Hole', 'is_active': False}, None, None, None, None],
            },
            'field': 'None',
        }
    },

    # Frontrow
    {
        'description': 'Defend > Cocoon of Evolution',
        'ai_player': {
            'name': 'Simon Muran',
            'frontrow': [
                {'name': 'Millennium Shield', 'is_active': True},
                {'name': 'Cocoon of Evolution', 'battle_mode': BattleMode.ATTACK, 'is_active': True},
                None, None, None
            ],
            'backrow': [None] * 5,
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.FRONTROW), BattleMode.DEFENSE)]),
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Millennium Shield', 'is_active': True},
                    {'name': 'Cocoon of Evolution', 'battle_mode': BattleMode.DEFENSE, 'is_active': False},
                    None, None, None
                ],
                'backrow': [None] * 5,
            }
        }
    },
    {
        'description': 'Defend > Millennium Shield',
        'ai_player': {
            'name': 'Simon Muran',
            'frontrow': [
                {'name': 'Labyrinth Wall', 'is_active': True},
                {'name': 'Millennium Shield', 'battle_mode': BattleMode.ATTACK, 'is_active': True},
                None, None, None
            ],
            'backrow': [None] * 5,
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.FRONTROW), BattleMode.DEFENSE)]),
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Labyrinth Wall', 'is_active': True},
                    {'name': 'Millennium Shield', 'battle_mode': BattleMode.DEFENSE, 'is_active': False},
                    None, None, None
                ],
                'backrow': [None] * 5,
            },
        }
    },
    {
        'description': 'Defend > Labyrinth Wall',
        'ai_player': {
            'name': 'Simon Muran',
            'frontrow': [
                {'name': 'Mystical Elf', 'is_active': True},
                {'name': 'Labyrinth Wall', 'battle_mode': BattleMode.ATTACK, 'is_active': True},
                None, None, None
            ],
            'backrow': [None] * 5,
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.FRONTROW), BattleMode.DEFENSE)]),
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Mystical Elf', 'is_active': True},
                    {'name': 'Labyrinth Wall', 'battle_mode': BattleMode.DEFENSE, 'is_active': False},
                    None, None, None
                ],
                'backrow': [None] * 5,
            },
        }
    },
    {
        'description': 'Defend > Mystical Elf',
        'ai_player': {
            'name': 'Simon Muran',
            'frontrow': [
                {'name': 'Dragon Piper', 'is_active': True},
                {'name': 'Mystical Elf', 'battle_mode': BattleMode.ATTACK, 'is_active': True},
                None, None, None
            ],
            'backrow': [None] * 5,
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.FRONTROW), BattleMode.DEFENSE)]),
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Dragon Piper', 'is_active': True},
                    {'name': 'Mystical Elf', 'battle_mode': BattleMode.DEFENSE, 'is_active': False},
                    None, None, None
                ],
                'backrow': [None] * 5,
            },
        }
    },
    {
        'description': 'Defend > Dragon Piper',
        'ai_player': {
            'name': 'Simon Muran',
            'frontrow': [
                {'name': 'Castle of Dark Illusions', 'is_active': True},
                {'name': 'Dragon Piper', 'battle_mode': BattleMode.ATTACK, 'is_active': True},
                None, None, None
            ],
            'backrow': [None] * 5,
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.FRONTROW), BattleMode.DEFENSE)]),
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Castle of Dark Illusions', 'is_active': True},
                    {'name': 'Dragon Piper', 'battle_mode': BattleMode.DEFENSE, 'is_active': False},
                    None, None, None
                ],
                'backrow': [None] * 5,
            },
        }
    },
    {
        'description': 'Defend > Castle of Dark Illusions',
        'ai_player': {
            'name': 'Simon Muran',
            'frontrow': [
                {'name': 'Metal Guardian', 'is_active': True},
                {'name': 'Castle of Dark Illusions', 'battle_mode': BattleMode.ATTACK, 'is_active': True},
                None, None, None
            ],
            'backrow': [None] * 5,
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.FRONTROW), BattleMode.DEFENSE)]),
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Metal Guardian', 'is_active': True},
                    {'name': 'Castle of Dark Illusions', 'battle_mode': BattleMode.DEFENSE, 'is_active': False},
                    None, None, None
                ],
                'backrow': [None] * 5,
            },
        }
    },
    {
        'description': 'Defend > Metal Guardian',
        'ai_player': {
            'name': 'Simon Muran',
            'frontrow': [
                {'name': 'Sleeping Lion', 'is_active': True},
                {'name': 'Metal Guardian', 'battle_mode': BattleMode.ATTACK, 'is_active': True},
                None, None, None
            ],
            'backrow': [None] * 5,
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.FRONTROW), BattleMode.DEFENSE)]),
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Sleeping Lion', 'is_active': True},
                    {'name': 'Metal Guardian', 'battle_mode': BattleMode.DEFENSE, 'is_active': False},
                    None, None, None
                ],
                'backrow': [None] * 5,
            },
        }
    },
    {
        'description': 'Defend > Sleeping Lion',
        'ai_player': {
            'name': 'Simon Muran',
            'frontrow': [
                {'name': 'Hard Armor', 'is_active': True},
                {'name': 'Sleeping Lion', 'battle_mode': BattleMode.ATTACK, 'is_active': True},
                None, None, None
            ],
            'backrow': [None] * 5,
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.FRONTROW), BattleMode.DEFENSE)]),
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Hard Armor', 'is_active': True},
                    {'name': 'Sleeping Lion', 'battle_mode': BattleMode.DEFENSE, 'is_active': False},
                    None, None, None
                ],
                'backrow': [None] * 5,
            },
        }
    },
    {
        'description': 'Defend > Hard Armor',
        'ai_player': {
            'name': 'Simon Muran',
            'frontrow': [
                {'name': 'Spirit of the Harp', 'is_active': True},
                {'name': 'Hard Armor', 'battle_mode': BattleMode.ATTACK, 'is_active': True},
                None, None, None
            ],
            'backrow': [None] * 5,
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.FRONTROW), BattleMode.DEFENSE)]),
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Spirit of the Harp', 'is_active': True},
                    {'name': 'Hard Armor', 'battle_mode': BattleMode.DEFENSE, 'is_active': False},
                    None, None, None
                ],
                'backrow': [None] * 5,
            },
        }
    },
    {
        'description': 'Defend > Spirit of the Harp',
        'ai_player': {
            'name': 'Simon Muran',
            'frontrow': [
                {'name': 'Prevent Rat', 'is_active': True},
                {'name': 'Spirit of the Harp', 'battle_mode': BattleMode.ATTACK, 'is_active': True},
                None, None, None
            ],
            'backrow': [None] * 5,
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.FRONTROW), BattleMode.DEFENSE)]),
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Prevent Rat', 'is_active': True},
                    {'name': 'Spirit of the Harp', 'battle_mode': BattleMode.DEFENSE, 'is_active': False},
                    None, None, None
                ],
                'backrow': [None] * 5,
            },
        }
    },
    {
        'description': 'Defend > Prevent Rat',
        'ai_player': {
            'name': 'Simon Muran',
            'frontrow': [
                {'name': 'Green Phantom King', 'is_active': True},
                {'name': 'Prevent Rat', 'battle_mode': BattleMode.ATTACK, 'is_active': True},
                None, None, None
            ],
            'backrow': [None] * 5,
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.FRONTROW), BattleMode.DEFENSE)]),
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Green Phantom King', 'is_active': True},
                    {'name': 'Prevent Rat', 'battle_mode': BattleMode.DEFENSE, 'is_active': False},
                    None, None, None
                ],
                'backrow': [None] * 5,
            },
        }
    },
    {
        'description': 'Defend > Green Phantom King',
        'ai_player': {
            'name': 'Simon Muran',
            'frontrow': [
                {'name': 'Gorgon Egg', 'is_active': True},
                {'name': 'Green Phantom King', 'battle_mode': BattleMode.ATTACK, 'is_active': True},
                None, None, None
            ],
            'backrow': [None] * 5,
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.FRONTROW), BattleMode.DEFENSE)]),
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Gorgon Egg', 'is_active': True},
                    {'name': 'Green Phantom King', 'battle_mode': BattleMode.DEFENSE, 'is_active': False},
                    None, None, None
                ],
                'backrow': [None] * 5,
            },
        }
    },
    {
        'description': 'Defend > Gorgon Egg',
        'ai_player': {
            'name': 'Simon Muran',
            'frontrow': [
                {'name': 'Wall Shadow', 'is_active': True},
                {'name': 'Gorgon Egg', 'battle_mode': BattleMode.ATTACK, 'is_active': True},
                None, None, None
            ],
            'backrow': [None] * 5,
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.FRONTROW), BattleMode.DEFENSE)]),
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Wall Shadow', 'is_active': True},
                    {'name': 'Gorgon Egg', 'battle_mode': BattleMode.DEFENSE, 'is_active': False},
                    None, None, None
                ],
                'backrow': [None] * 5,
            },
        }
    },
    {
        'description': 'Defend > Wall Shadow',
        'ai_player': {
            'name': 'Simon Muran',
            'frontrow': [
                {'name': 'Blocker', 'is_active': True},
                {'name': 'Wall Shadow', 'battle_mode': BattleMode.ATTACK, 'is_active': True},
                None, None, None
            ],
            'backrow': [None] * 5,
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.FRONTROW), BattleMode.DEFENSE)]),
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Blocker', 'is_active': True},
                    {'name': 'Wall Shadow', 'battle_mode': BattleMode.DEFENSE, 'is_active': False},
                    None, None, None
                ],
                'backrow': [None] * 5,
            },
        }
    },
    {
        'description': 'Defend > Blocker',
        'ai_player': {
            'name': 'Simon Muran',
            'frontrow': [
                {'name': 'Golgoil', 'is_active': True},
                {'name': 'Blocker', 'battle_mode': BattleMode.ATTACK, 'is_active': True},
                None, None, None
            ],
            'backrow': [None] * 5,
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.FRONTROW), BattleMode.DEFENSE)]),
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Golgoil', 'is_active': True},
                    {'name': 'Blocker', 'battle_mode': BattleMode.DEFENSE, 'is_active': False},
                    None, None, None
                ],
                'backrow': [None] * 5,
            },
        }
    },
    {
        'description': 'Defend > Golgoil',
        'ai_player': {
            'name': 'Simon Muran',
            'frontrow': [
                {'name': '30,000-Year White Turtle', 'is_active': True},
                {'name': 'Golgoil', 'battle_mode': BattleMode.ATTACK, 'is_active': True},
                None, None, None
            ],
            'backrow': [None] * 5,
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.FRONTROW), BattleMode.DEFENSE)]),
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': '30,000-Year White Turtle', 'is_active': True},
                    {'name': 'Golgoil', 'battle_mode': BattleMode.DEFENSE, 'is_active': False},
                    None, None, None
                ],
                'backrow': [None] * 5,
            },
        }
    },
    {
        'description': 'Defend > 30,000-Year White Turtle',
        'ai_player': {
            'name': 'Simon Muran',
            'frontrow': [
                {'name': 'Queen Bird', 'is_active': True},
                {'name': '30,000-Year White Turtle', 'battle_mode': BattleMode.ATTACK, 'is_active': True},
                None, None, None
            ],
            'backrow': [None] * 5,
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.FRONTROW), BattleMode.DEFENSE)]),
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Queen Bird', 'is_active': True},
                    {'name': '30,000-Year White Turtle', 'battle_mode': BattleMode.DEFENSE, 'is_active': False},
                    None, None, None
                ],
                'backrow': [None] * 5,
            },
        }
    },
    {
        'description': 'Defend > Queen Bird',
        'ai_player': {
            'name': 'Simon Muran',
            'frontrow': [
                {'name': 'Yado Karu', 'is_active': True},
                {'name': 'Queen Bird', 'battle_mode': BattleMode.ATTACK, 'is_active': True},
                None, None, None
            ],
            'backrow': [None] * 5,
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.FRONTROW), BattleMode.DEFENSE)]),
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Yado Karu', 'is_active': True},
                    {'name': 'Queen Bird', 'battle_mode': BattleMode.DEFENSE, 'is_active': False},
                    None, None, None
                ],
                'backrow': [None] * 5,
            },
        }
    },
    {
        'description': 'Defend > Yado Karu',
        'ai_player': {
            'name': 'Simon Muran',
            'frontrow': [
                {'name': 'Boulder Tortoise', 'is_active': True},
                {'name': 'Yado Karu', 'battle_mode': BattleMode.ATTACK, 'is_active': True},
                None, None, None
            ],
            'backrow': [None] * 5,
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.FRONTROW), BattleMode.DEFENSE)]),
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Boulder Tortoise', 'is_active': True},
                    {'name': 'Yado Karu', 'battle_mode': BattleMode.DEFENSE, 'is_active': False},
                    None, None, None
                ],
                'backrow': [None] * 5,
            },
        }
    },
    {
        'description': 'Defend > Boulder Tortoise',
        'ai_player': {
            'name': 'Simon Muran',
            'frontrow': [
                {'name': 'Doron', 'is_active': True},
                {'name': 'Boulder Tortoise', 'battle_mode': BattleMode.ATTACK, 'is_active': True},
                None, None, None
            ],
            'backrow': [None] * 5,
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.FRONTROW), BattleMode.DEFENSE)]),
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Doron', 'is_active': True},
                    {'name': 'Boulder Tortoise', 'battle_mode': BattleMode.DEFENSE, 'is_active': False},
                    None, None, None
                ],
                'backrow': [None] * 5,
            },
        }
    },
    {
        'description': 'Defend > check next active card in Defend list',
        'ai_player': {
            'name': 'Simon Muran',
            'frontrow': [
                {'name': 'Cocoon of Evolution', 'is_active': False},
                {'name': 'Queen Bird', 'is_active': True},
                {'name': 'Spirit of the Harp', 'battle_mode': BattleMode.ATTACK, 'is_active': True},
                {'name': 'Wall Shadow', 'is_active': False},
                {'name': 'Castle of Dark Illusions', 'is_active': False},
            ],
            'backrow': [None] * 5,
        },
        'expected_combo': [
            Action([Action.Description(Position(2, Position.Mode.FRONTROW), BattleMode.DEFENSE)]),
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Cocoon of Evolution', 'is_active': False},
                    {'name': 'Queen Bird', 'is_active': True},
                    {'name': 'Spirit of the Harp', 'battle_mode': BattleMode.DEFENSE, 'is_active': False},
                    {'name': 'Wall Shadow', 'is_active': False},
                    {'name': 'Castle of Dark Illusions', 'is_active': False},
                ],
                'backrow': [None] * 5,
            },
        }
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
            'backrow': [None] * 5,
            'remaining_turns_under_swords': 1,
        },
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.FRONTROW), BattleMode.DEFENSE)]),
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Doron', 'battle_mode': BattleMode.DEFENSE, 'is_active': False},
                    {'name': 'Boulder Tortoise', 'is_active': False},
                    None, None, None
                ],
                'backrow': [None] * 5,
                'remaining_turns_under_swords': 1,
            },
        }
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
            'backrow': [None] * 5,
            'remaining_turns_under_swords': 1,
        },
        'expected_combo': [
            Action([Action.Description(Position(1, Position.Mode.FRONTROW), BattleMode.DEFENSE)]),
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Twin-headed Thunder Dragon', 'is_active': True},
                    {'name': 'Twin-headed Thunder Dragon', 'battle_mode': BattleMode.DEFENSE, 'is_active': False,
                     'equip_stage': 2},
                    {'name': 'Boulder Tortoise', 'is_active': False},
                    None, None, None
                ],
                'backrow': [None] * 5,
                'remaining_turns_under_swords': 1,
            },
        }
    },
    {
        'description': 'Swords > No defend for monsters in forced attack list',
        'ai_player': {
            'name': 'Simon Muran',
            'frontrow': [
                {'name': 'Meteor B. Dragon', 'battle_mode': BattleMode.ATTACK, 'is_active': True},
                {'name': 'Boulder Tortoise', 'is_active': False},
                None, None, None
            ],
            'backrow': [None] * 5,
            'remaining_turns_under_swords': 1,
        },
        'expected_combo': [
            Action([Action.Description(Position(0, Position.Mode.FRONTROW), BattleMode.ATTACK)]),  # TODO: darken ?
        ],
        'expected_outcome': {
            'ai_player': {
                'name': 'Simon Muran',
                'frontrow': [
                    {'name': 'Meteor B. Dragon', 'battle_mode': BattleMode.ATTACK, 'is_active': False},
                    {'name': 'Boulder Tortoise', 'is_active': False},
                    None, None, None
                ],
                'backrow': [None] * 5,
                'remaining_turns_under_swords': 1,
            },
        }
    },

    # Next battle
    {
        'description': 'Next battle > Direct attack',
        'player': {
            'frontrow': [None, None, None, None, None],
            'backrow': [{'name': 'Widespread Ruin'}, None, None, None, None],
            'lp': 8_000
        },
        'ai_player': {
            'name': 'Seto 3rd',
            'frontrow': [
                {'name': 'Blue-eyes Ultimate Dragon', 'is_active': True},
                None, None, None, None
            ],
            'backrow': [None] * 5,
            'remaining_turns_under_swords': 0,
        },
        'expected_combo': [
            Action([Action.Description(
                Position(0, Position.Mode.FRONTROW),
                BattleMode.ATTACK,
                Position(2, Position.Mode.FRONTROW)
            )]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [None, None, None, None, None],
                'backrow': [{'name': 'Widespread Ruin'}, None, None, None, None],
                'lp': 3_500
            },
            'ai_player': {
                'name': 'Seto 3rd',
                'frontrow': [
                    {'name': 'Blue-eyes Ultimate Dragon', 'battle_mode': BattleMode.ATTACK, 'is_active': False},
                    None, None, None, None
                ],
                'backrow': [None] * 5,
                'remaining_turns_under_swords': 0,
            },
        }
    },
    {
        'description': 'Next battle > lethal',
        'player': {
            'frontrow': [
                {'name': 'Doron', 'face': Face.UP, 'battle_mode': BattleMode.ATTACK},  # Atk: 900
                {'name': 'Skull Servant', 'face': Face.UP, 'battle_mode': BattleMode.ATTACK},  # Atk: 300
                None, None, None
            ],
            'lp': 1_000
        },
        'ai_player': {
            'name': 'Bandit Keith',
            'frontrow': [
                {'name': 'Doron', 'is_active': True},  # Atk: 900
                {'name': 'Mechanicalchacer', 'is_active': True},  # Atk: 1_850
                None, None, None
            ],
            'backrow': [None] * 5,
            'remaining_turns_under_swords': 0,
        },
        'expected_combo': [
            Action([Action.Description(
                Position(1, Position.Mode.FRONTROW),
                BattleMode.ATTACK,
                Position(1, Position.Mode.FRONTROW)
            )]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [
                    {'name': 'Doron', 'face': Face.UP, 'battle_mode': BattleMode.ATTACK},  # Atk: 900
                    None,
                    None, None, None
                ],
                'lp': 0
            },
            'ai_player': {
                'name': 'Bandit Keith',
                'frontrow': [
                    {'name': 'Doron', 'is_active': True},  # Atk: 900
                    {'name': 'Mechanicalchacer', 'battle_mode': BattleMode.ATTACK, 'is_active': False},  # Atk: 1_850
                    None, None, None
                ],
                'backrow': [None] * 5,
                'remaining_turns_under_swords': 0,
            },
        }
    },
    {
        'description': "Next battle > AI thinks it can lethal but doesn't due to stars",
        'player': {
            'frontrow': [
                {'name': 'Doron', 'face': Face.UP, 'battle_mode': BattleMode.ATTACK},  # Atk: 900
                {'name': 'Petit Angel', 'face': Face.UP, 'star': Star.SUN, 'battle_mode': BattleMode.ATTACK},  # Atk: 600
                None, None, None
            ],
            'lp': 1_000
        },
        'ai_player': {
            'name': 'Bandit Keith',
            'frontrow': [
                {'name': 'Doron', 'is_active': True},  # Atk: 900
                {'name': 'Mechanicalchacer', 'is_active': True},  # Atk: 1_850, Star: Moon
                None, None, None
            ],
            'backrow': [None] * 5,
            'remaining_turns_under_swords': 0,
        },
        'expected_combo': [
            Action([Action.Description(
                Position(1, Position.Mode.FRONTROW),
                BattleMode.ATTACK,
                Position(1, Position.Mode.FRONTROW)
            )]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [
                    {'name': 'Doron', 'face': Face.UP, 'battle_mode': BattleMode.ATTACK},  # Atk: 900
                    None,
                    None, None, None
                ],
                'lp': 250
            },
            'ai_player': {
                'name': 'Bandit Keith',
                'frontrow': [
                    {'name': 'Doron', 'is_active': True},  # Atk: 900
                    {'name': 'Mechanicalchacer', 'battle_mode': BattleMode.ATTACK, 'is_active': False},  # Atk: 1_850, Star: Moon
                    None, None, None
                ],
                'backrow': [None] * 5,
                'remaining_turns_under_swords': 0,
            },
        }
    },
    {
        'description': 'Next battle > Suicide glitch',
        'player': {
            'frontrow': [
                {'name': 'Twin-headed Thunder Dragon', 'star': Star.PLUTO, 'battle_mode': BattleMode.ATTACK, 'equip_stage': 4},
                None, None, None, None
            ],
            'lp': 300
        },
        'ai_player': {
            'name': 'Seto 3rd',
            'frontrow': [
                {'name': 'Blue-eyes Ultimate Dragon', 'is_active': True},  # Star.SUN
                None, None, None, None
            ],
            'backrow': [None] * 5,
            'lp': 8_000,
            'remaining_turns_under_swords': 0,
        },
        'expected_combo': [
            Action([Action.Description(
                Position(0, Position.Mode.FRONTROW),
                BattleMode.ATTACK,
                Position(0, Position.Mode.FRONTROW)
            )]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [
                    {'name': 'Twin-headed Thunder Dragon', 'star': Star.PLUTO, 'battle_mode': BattleMode.ATTACK, 'equip_stage': 4},
                    None, None, None, None
                ],
                'lp': 300
            },
            'ai_player': {
                'name': 'Seto 3rd',
                'frontrow': [
                    None,
                    None, None, None, None
                ],
                'backrow': [None] * 5,
                'lp': 7_700,
                'remaining_turns_under_swords': 0,
            },
        }
    },
    {
        'description': 'Next battle > Attack visible monsters in attack mode thanks to star',
        'player': {
            'frontrow': [
                {'name': 'Twin-headed Thunder Dragon', 'battle_mode': BattleMode.ATTACK, 'star': Star.PLUTO},
                {'name': 'Curse of Dragon', 'battle_mode': BattleMode.ATTACK, 'star': Star.SATURN},
                {'name': 'B. Dragon Jungle King', 'battle_mode': BattleMode.ATTACK, 'star': Star.JUPITER},
                None, None
            ],
            'lp': 8_000
        },
        'ai_player': {
            'name': 'Pegasus',
            'frontrow': [
                {'name': 'Bickuribox', 'is_active': True},  # Star.MOON
                {'name': 'Vermillion Sparrow', 'is_active': True},  # Star.MARS
                None, None, None
            ],
            'backrow': [None] * 5,
            'remaining_turns_under_swords': 0,
        },
        'expected_combo': [
            Action([Action.Description(
                Position(1, Position.Mode.FRONTROW),
                BattleMode.ATTACK,
                Position(2, Position.Mode.FRONTROW)
            )]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [
                    {'name': 'Twin-headed Thunder Dragon', 'battle_mode': BattleMode.ATTACK, 'star': Star.PLUTO},
                    {'name': 'Curse of Dragon', 'battle_mode': BattleMode.ATTACK, 'star': Star.SATURN},
                    None,
                    None, None
                ],
                'lp': 7_700
            },
            'ai_player': {
                'name': 'Pegasus',
                'frontrow': [
                    {'name': 'Bickuribox', 'is_active': True},  # Star.MOON
                    {'name': 'Vermillion Sparrow', 'battle_mode': BattleMode.ATTACK, 'is_active': False},  # Star.MARS
                    None, None, None
                ],
                'backrow': [None] * 5,
                'remaining_turns_under_swords': 0,
            },
        }
    },
    {
        'description': 'Next battle > Attack visible monsters in attack mode',
        'player': {
            'frontrow': [
                {'name': 'Twin-headed Thunder Dragon', 'battle_mode': BattleMode.ATTACK, 'star': Star.PLUTO},
                {'name': 'Curse of Dragon', 'battle_mode': BattleMode.ATTACK, 'star': Star.SATURN},
                {'name': 'B. Dragon Jungle King', 'battle_mode': BattleMode.ATTACK, 'star': Star.JUPITER},
                None, None
            ],
            'lp': 8_000
        },
        'ai_player': {
            'name': 'Pegasus',
            'frontrow': [
                {'name': 'Meteor Dragon', 'is_active': True},  # Star.MARS
                {'name': 'Bickuribox', 'is_active': True},  # Star.MOON
                None, None, None
            ],
            'backrow': [None] * 5,
            'remaining_turns_under_swords': 0,
        },
        'expected_combo': [
            Action([Action.Description(
                Position(1, Position.Mode.FRONTROW),
                BattleMode.ATTACK,
                Position(2, Position.Mode.FRONTROW)
            )]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [
                    {'name': 'Twin-headed Thunder Dragon', 'battle_mode': BattleMode.ATTACK, 'star': Star.PLUTO},
                    {'name': 'Curse of Dragon', 'battle_mode': BattleMode.ATTACK, 'star': Star.SATURN},
                    None,
                    None, None
                ],
                'lp': 7_800
            },
            'ai_player': {
                'name': 'Pegasus',
                'frontrow': [
                    {'name': 'Meteor Dragon', 'is_active': True},  # Star.MARS
                    {'name': 'Bickuribox', 'battle_mode': BattleMode.ATTACK, 'is_active': False},  # Star.MOON
                    None, None, None
                ],
                'backrow': [None] * 5,
                'remaining_turns_under_swords': 0,
            },
        }
    },
    {
        'description': 'Next battle > Attack visible monsters in attack mode before defense mode',
        'player': {
            'frontrow': [
                {'name': 'Twin-headed Thunder Dragon', 'battle_mode': BattleMode.ATTACK, 'star': Star.PLUTO},
                {'name': 'Curse of Dragon', 'battle_mode': BattleMode.ATTACK, 'star': Star.SATURN},
                {'name': 'B. Dragon Jungle King', 'battle_mode': BattleMode.DEFENSE, 'star': Star.JUPITER},
                None, None
            ],
            'lp': 8_000
        },
        'ai_player': {
            'name': 'Pegasus',
            'frontrow': [
                {'name': 'Meteor Dragon', 'is_active': True},  # Star.URANUS
                {'name': 'Bickuribox', 'is_active': True},  # Star.MOON
                None, None, None
            ],
            'backrow': [None] * 5,
            'remaining_turns_under_swords': 0,
        },
        'expected_combo': [
            Action([Action.Description(
                Position(1, Position.Mode.FRONTROW),
                BattleMode.ATTACK,
                Position(1, Position.Mode.FRONTROW)
            )]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [
                    {'name': 'Twin-headed Thunder Dragon', 'battle_mode': BattleMode.ATTACK, 'star': Star.PLUTO},
                    None,
                    {'name': 'B. Dragon Jungle King', 'battle_mode': BattleMode.DEFENSE, 'star': Star.JUPITER},
                    None, None
                ],
                'lp': 7_700
            },
            'ai_player': {
                'name': 'Pegasus',
                'frontrow': [
                    {'name': 'Meteor Dragon', 'is_active': True},  # Star.URANUS
                    {'name': 'Bickuribox', 'battle_mode': BattleMode.ATTACK, 'is_active': False},  # Star.MOON
                    None, None, None
                ],
                'backrow': [None] * 5,
                'remaining_turns_under_swords': 0,
            },
        }
    },
    {
        'description': 'Next battle > Attack visible monsters in defense mode',
        'player': {
            'frontrow': [
                {'name': 'Twin-headed Thunder Dragon', 'battle_mode': BattleMode.ATTACK, 'star': Star.PLUTO},
                {'name': 'Thousand Dragon', 'battle_mode': BattleMode.DEFENSE, 'star': Star.MARS},
                {'name': '30,000-Year White Turtle', 'battle_mode': BattleMode.DEFENSE, 'star': Star.NEPTUNE},
                None, None
            ],
            'lp': 8_000
        },
        'ai_player': {
            'name': 'Pegasus',
            'frontrow': [
                {'name': 'Meteor Dragon', 'is_active': True},  # Star.URANUS
                {'name': 'Bickuribox', 'is_active': True},  # Star.MOON
                None, None, None
            ],
            'backrow': [None] * 5,
            'remaining_turns_under_swords': 0,
        },
        'expected_combo': [
            Action([Action.Description(
                Position(1, Position.Mode.FRONTROW),
                BattleMode.ATTACK,
                Position(2, Position.Mode.FRONTROW)
            )]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [
                    {'name': 'Twin-headed Thunder Dragon', 'battle_mode': BattleMode.ATTACK, 'star': Star.PLUTO},
                    {'name': 'Thousand Dragon', 'battle_mode': BattleMode.DEFENSE, 'star': Star.MARS},
                    None,
                    None, None
                ],
                'lp': 8_000
            },
            'ai_player': {
                'name': 'Pegasus',
                'frontrow': [
                    {'name': 'Meteor Dragon', 'is_active': True},  # Star.URANUS
                    {'name': 'Bickuribox', 'battle_mode': BattleMode.ATTACK, 'is_active': False},  # Star.MOON
                    None, None, None
                ],
                'backrow': [None] * 5,
                'remaining_turns_under_swords': 0,
            },
        }
    },
    {
        'description': 'Next battle > Attack facedown monsters',
        'player': {
            'frontrow': [
                {'name': 'Doron', 'battle_mode': BattleMode.DEFENSE, 'face': Face.DOWN, 'star': Star.NEPTUNE},
                {'name': 'Doron', 'battle_mode': BattleMode.DEFENSE, 'face': Face.DOWN, 'star': Star.NEPTUNE},
                None, None, None
            ],
            'lp': 8_000
        },
        'ai_player': {
            'name': 'Weevil Underwood',
            'frontrow': [
                {'name': 'Jirai Gumo', 'is_active': True, 'star': Star.JUPITER},
                None, None, None, None
            ],
            'backrow': [None] * 5,
            'remaining_turns_under_swords': 0,
        },
        'expected_combo': [
            Action([Action.Description(
                Position(0, Position.Mode.FRONTROW),
                BattleMode.ATTACK,
                Position(0, Position.Mode.FRONTROW)
            )], odds=(50, 100), level=1),
            Action([], odds=(50, 100), next_=Actions([
                Action([Action.Description(
                    Position(0, Position.Mode.FRONTROW),
                    BattleMode.ATTACK,
                    Position(1, Position.Mode.FRONTROW)
                )], odds=(50, 100)),
                Action([Action.Description(
                    Position(0, Position.Mode.FRONTROW),
                    BattleMode.DEFENSE)
                ], odds=(50, 100)),
            ], level=2)),
        ]
    },
    {
        'description': 'Next battle > Attack with remaining monsters',
        'player': {
            'frontrow': [None] * 5,
            'lp': 8_000
        },
        'ai_player': {
            'name': 'Rex Raptor',
            'frontrow': [
                {'name': 'Uraby', 'is_active': False},  # Star.NEPTUNE
                {'name': 'Clown Zombie', 'is_active': True},  # Star.MOON
                {'name': 'Clown Zombie', 'is_active': True},  # Star.MOON
                None, None
            ],
            'backrow': [None] * 5,
            'remaining_turns_under_swords': 0,
        },
        'expected_combo': [
            Action([Action.Description(
                Position(1, Position.Mode.FRONTROW),
                BattleMode.ATTACK,
                Position(2, Position.Mode.FRONTROW)
            )]),
        ],
        'expected_outcome': {
            'player': {
                'frontrow': [None] * 5,
                'lp': 6_650
            },
            'ai_player': {
                'name': 'Rex Raptor',
                'frontrow': [
                    {'name': 'Uraby', 'is_active': False},  # Star.NEPTUNE
                    {'name': 'Clown Zombie', 'battle_mode': BattleMode.ATTACK, 'is_active': False},  # Star.MOON
                    {'name': 'Clown Zombie', 'is_active': True},  # Star.MOON
                    None, None
                ],
                'backrow': [None] * 5,
                'remaining_turns_under_swords': 0,
            },
        }
    },
]

# tests_actions_handler_board_ai = [
#     {
#         'description': 'Next battle > Attack with remaining monsters',
#         'player': {
#             'frontrow': [None]*5,
#             'lp': 8_000
#         },
#         'ai_player': {
#             'name': 'Rex Raptor',
#             'frontrow': [
#                 {'name': 'Clown Zombie', 'is_active': True},
#                 {'name': 'Clown Zombie', 'is_active': True},
#                 {'name': 'Uraby', 'is_active': True},
#                 None, None
#             ],
#             'backrow': [None]*5,
#             'remaining_turns_under_swords': 0,
#         },
#         'expected_outcome': {
#             'player': {
#                 'frontrow': [None]*5,
#                 'lp': 6_500
#             },
#             'ai_player': {
#                 'name': 'Rex Raptor',
#                 'frontrow': [
#                     {'name': 'Clown Zombie', 'is_active': True},
#                     {'name': 'Clown Zombie', 'is_active': True},
#                     {'name': 'Uraby', 'is_active': False},
#                     None, None
#                 ],
#                 'backrow': [None]*5,
#                 'remaining_turns_under_swords': 0,
#             }
#         }
#     },
# ]


def build_situation(cursor: Cursor, player_dic: dict, ai_player_dic: dict, field_dic: dict) \
        -> tuple[Opponent, Opponent, Field | None]:
    """ Returns player, ai_player and field. """

    field_name: str | None = field_dic.get('field', None)

    player = None
    ai_player = None
    field = None
    if field_name is not None:
        field = Field.by_name(field_name, raise_if_not_found=True)

    for pl in [player_dic, ai_player_dic]:
        name = 'Player' if pl == player_dic else ai_player_dic['name']
        type_ = Opponent.Type.PLAYER if name == 'Player' else Opponent.Type.AI
        frontrow = Cards(Position.Mode.FRONTROW)
        backrow = Cards(Position.Mode.BACKROW)
        hand = Cards(Position.Mode.HAND)
        remaining_deck = Cards(Position.Mode.DECK)
        lp = None
        current_turn = None
        remaining_turns_under_swords = None

        if pl is not None:
            lp = pl.get('lp')
            current_turn = pl.get('current_turn')
            remaining_turns_under_swords = pl.get('remaining_turns_under_swords')

            for card_names, row in [
                (pl.get('frontrow'), frontrow),
                (pl.get('backrow'), backrow),
                (pl.get('hand_names'), hand),
                (pl.get('remaining_deck_names'), remaining_deck)
            ]:
                if card_names is None or len(card_names) == 0:
                    continue

                for idx, card_or_card_name in enumerate(card_names):
                    if card_or_card_name is None:
                        row.append(None)
                        continue

                    is_str = isinstance(card_or_card_name, str)
                    board_card_name = card_or_card_name if is_str else card_or_card_name['name']
                    board_card_id = get_card_id_from_name(cursor, board_card_name)
                    if board_card_name is not None and board_card_id is None:
                        # raise ValueError(f"{index}. Couldn't find id of board card name '{board_card_name}'.")
                        raise ValueError(f"Couldn't find id of board card name '{board_card_name}'.")

                    equip_stage = card_or_card_name.get('equip_stage') \
                        if not is_str and row.mode == Position.Mode.FRONTROW \
                        else None
                    star = card_or_card_name.get('star') \
                        if not is_str and row.mode == Position.Mode.FRONTROW \
                        else None
                    battle_mode = card_or_card_name.get('battle_mode') \
                        if not is_str and row.mode == Position.Mode.FRONTROW \
                        else None
                    face = card_or_card_name.get('face') \
                        if not is_str and row.mode in {Position.Mode.FRONTROW, Position.Mode.BACKROW} \
                        else None

                    is_active = card_or_card_name.get('is_active') \
                        if not is_str and row.mode in {Position.Mode.FRONTROW, Position.Mode.BACKROW} \
                        else None

                    card = Card(
                        cursor, board_card_id, field,
                        pos=Position(idx, row.mode),  # if row is not None else None,
                        equip_stage=equip_stage,
                        star=star,
                        battle_mode=battle_mode,
                        face=face,
                        is_active=is_active
                    )

                    row.append(card)

        if len(frontrow) == 0:
            for _ in range(5):
                frontrow.append(None)
        if len(backrow) == 0:
            for _ in range(5):
                backrow.append(None)

        if id(pl) == id(player_dic):
            player = Opponent(name, type_, frontrow, backrow, hand, remaining_deck,
                              lp=lp,
                              current_turn=current_turn,
                              remaining_turns_under_swords=remaining_turns_under_swords
                              )
        else:
            ai_player = Opponent(name, type_, frontrow, backrow, hand, remaining_deck,
                                 lp=lp,
                                 current_turn=current_turn,
                                 remaining_turns_under_swords=remaining_turns_under_swords
                                 )

    return player, ai_player, field


def test_ai(cursor: Cursor, tests, ai_decision: AIDecider, action_handler: ActionHandler = None):
    results = []
    combos = []

    for index, test in enumerate(tests):
        player_dic = test.get('player', {})
        ai_player_dic = test['ai_player']
        field_dic = test

        player, ai_player, field = build_situation(cursor, player_dic, ai_player_dic, field_dic)

        is_passed = True
        try:
            combo = ai_decision(cursor, player, ai_player, field=field)
        except Exception as e:
            print(test['description'])
            is_passed = False
            raise e
        else:
            # Handle generators
            if isinstance(combo, Generator):
                combo = next(combo)

            expected_combo = test.get('expected_combo', None)
            expected_outcome = test.get('expected_outcome', None)

            subtests = [expected_combo]

            expected_player, expected_ai_player, expected_field = None, None, None
            if action_handler is not None and expected_outcome is not None:
                field_change = action_handler(cursor, combo, player, ai_player, field)
                if field_change not in {None, EndOfTurn}:
                    field = field_change  # Cards' field update should already be done inside the action handler

                expected_player, expected_ai_player, expected_field = build_situation(
                    cursor,
                    expected_outcome.get('player', None),
                    expected_outcome['ai_player'],
                    expected_outcome
                )
                subtests.extend([expected_player, expected_ai_player, expected_field])

            combos.append((combo, ((player, expected_player), (ai_player, expected_ai_player), (field, expected_field))))

            for subtest in subtests:  # filter(None, subtests):
                if id(subtest) == id(expected_combo):
                    is_passed &= combo.actions == expected_combo
                elif id(subtest) == id(expected_player):
                    is_passed &= player == expected_player
                elif id(subtest) == id(expected_ai_player):
                    is_passed &= ai_player == expected_ai_player
                elif id(subtest) == id(expected_field):
                    is_passed &= field == expected_field
        finally:
            results.append(is_passed)

    print(f"Successes: {len(list(filter(None, results)))} / {len(results)} :Total")
    if any([not x for x in results]):
        print(f"Differences :", end=' ')
        pprint(*[
            {
                '___index': index,
                '__description': test['description'],
                '_expected_combo': test['expected_combo'],
                '_found_combo': combo,
                'expected_outcome': {'player': expected_player, 'ai_player': expected_ai_player, 'field': expected_field},
                'found_outcome': {'player': player, 'ai_player': ai_player, 'field': field}
            }
            for index, result, test,
            (combo, ((player, expected_player), (ai_player, expected_ai_player), (field, expected_field)))
            in zip(range(len(tests)), tests, results, combos)
            if not result],
            # sep='\n'
        )


if __name__ == '__main__':
    ai_stats = ai.get_all_ai_stats()
    con, cur = db.connect_to_YFM_database()

    print('Tests Hand AI')
    test_ai(
        cur, tests_hand_ai, ai_hand.hand_ai,
        action_handler=lambda c, act, pl, ai_, f: play_from_hand(c, act, source_opp=ai_, target_opp=pl, field=f)
    )

    print('Tests Board AI')
    test_ai(
        cur, tests_board_ai, ai_board.board_ai,
        action_handler=lambda c, act, pl, ai_, f: play_from_board(c, act, source_opp=ai_, target_opp=pl, field=f)
    )

    con.close()
