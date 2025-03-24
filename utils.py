import csv
import random
import sqlite3

START_EXODIA_ID, END_EXODIA_ID = 17, 21
CARD_LIMIT = 3
CARD_LIMIT_EXODIA = 1

DECK_SIZE = 40

LOW_LP_THRESHOLD = 'Low LP Threshold'
CRITICAL_DECK_SIZE = 'Critical Deck Size'
MAX_FUSION_LENGTH = 'Max Fusion Length'
MAX_IMPROVE_LENGTH = 'Max Improve Length'
SPELL_PERCENT = 'Spell Percent'
ATTACK_PERCENT = 'Attack Percent'
TOTAL_DOMINATION = 'Total Domination'
LACKS_TOTAL_DOMINATION = 'Lacks Total Domination'
FIND_BEST_COMBO = 'FIND_BEST_COMBO'
IMPROVE_MONSTER = 'IMPROVE_MONSTER'
SET_MAGIC = 'SET_MAGIC'

ai_stats = None


def get_ai_stats(_ai_stats=ai_stats):
    if _ai_stats is not None:
        return _ai_stats

    _ai_stats = {}
    with open('YFM_AI-stats.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)  # csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            del row['Hand Size']

            row[LOW_LP_THRESHOLD] = int(row[LOW_LP_THRESHOLD])
            row[CRITICAL_DECK_SIZE] = int(row[CRITICAL_DECK_SIZE])
            row[MAX_FUSION_LENGTH] = int(row[MAX_FUSION_LENGTH])
            row[MAX_IMPROVE_LENGTH] = int(row[MAX_IMPROVE_LENGTH])

            row[SPELL_PERCENT] = int(row['Spell Probability'].split('%')[0])
            row[ATTACK_PERCENT] = int(row['Attack Probability'].split('%')[0])
            del row['Spell Probability']
            del row['Attack Probability']

            row[TOTAL_DOMINATION] = {
                FIND_BEST_COMBO: row['Total Domination FIND_BEST_COMBO'],
                IMPROVE_MONSTER: row['Total Domination IMPROVE_MONSTER'],
                SET_MAGIC: row['Total Domination SET_MAGIC']
            }
            del row['Total Domination FIND_BEST_COMBO']
            del row['Total Domination IMPROVE_MONSTER']
            del row['Total Domination SET_MAGIC']

            row[LACKS_TOTAL_DOMINATION] = {
                FIND_BEST_COMBO: row['Lacks Total Domination FIND_BEST_COMBO'],
                IMPROVE_MONSTER: row['Lacks Total Domination IMPROVE_MONSTER'],
                SET_MAGIC: row['Lacks Total Domination SET_MAGIC']
            }
            del row['Lacks Total Domination FIND_BEST_COMBO']
            del row['Lacks Total Domination IMPROVE_MONSTER']
            del row['Lacks Total Domination SET_MAGIC']

            row[TOTAL_DOMINATION][FIND_BEST_COMBO] = int(row[TOTAL_DOMINATION][FIND_BEST_COMBO].split('%')[0])
            row[TOTAL_DOMINATION][IMPROVE_MONSTER] = int(row[TOTAL_DOMINATION][IMPROVE_MONSTER].split('%')[0])
            row[TOTAL_DOMINATION][SET_MAGIC] = int(row[TOTAL_DOMINATION][SET_MAGIC].split('%')[0])
            row[LACKS_TOTAL_DOMINATION][FIND_BEST_COMBO] = int(row[LACKS_TOTAL_DOMINATION][FIND_BEST_COMBO].split('%')[0])
            row[LACKS_TOTAL_DOMINATION][IMPROVE_MONSTER] = int(row[LACKS_TOTAL_DOMINATION][IMPROVE_MONSTER].split('%')[0])
            row[LACKS_TOTAL_DOMINATION][SET_MAGIC] = int(row[LACKS_TOTAL_DOMINATION][SET_MAGIC].split('%')[0])

            _ai_stats[row['Opponent']] = row

            del row['Opponent']

    return _ai_stats


def connect_to_YFM_database(db_file='YFM.db'):
    # Create a SQL connection to our SQLite database
    con = sqlite3.connect(db_file)
    # creating cursor
    cur = con.cursor()

    return con, cur


def generate_decks(cur, duelist_name, num_decks=1):
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


def generate_new_hands(cur, duelist_name, num_hands=1):
    for deck in generate_decks(cur, duelist_name, num_decks=num_hands):
        hand_size, = cur.execute(f"SELECT HandSize "
                                 f"FROM Duelists "
                                 f"WHERE Duelists.DuelistName = \"{duelist_name}\"").fetchone()
        yield deck[:hand_size]


def get_card_name_from_id(cur, card_id):
    card_name = cur.execute(f"SELECT CardName from Cards WHERE CardID = '{card_id}'").fetchone()

    if card_name is not None:
        card_name, = card_name

    return card_name


def get_hand_names(cur, hand):
    hand_names = []
    for card_id in hand:
        hand_names.append(get_card_name_from_id(cur, card_id))

    return hand_names


def get_card_id_from_name(cur, player_cardname):
    card_id = cur.execute(f"SELECT CardID from Cards WHERE CardName = \"{player_cardname}\"").fetchone()

    if card_id is not None:
        card_id, = card_id

    return card_id


def get_card_type_from_id(cur, card_id):
    card_type = cur.execute(f"SELECT CardType from Cards WHERE CardID = \"{card_id}\"").fetchone()

    if card_type is not None:
        card_type, = card_type

    return card_type


def is_magic(cur, card_id):
    _type = get_card_type_from_id(cur, card_id)
    return _type is not None and _type == 'Magic'


if __name__ == '__main__':
    con, cur = connect_to_YFM_database()

    print(get_ai_stats())
    for hand in generate_new_hands(cur, 'Shadi'):
        print(get_hand_names(cur, hand))

    con.close()

