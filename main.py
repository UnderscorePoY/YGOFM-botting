import random
import sqlite3

# Card ids
ID, NAME, STAR1, STAR2, TYPE, ATTACK, DEFENSE = 0, 1, 3, 4, 6, 8, 9


def seto3_topdecks(NUM_SIMU=1_000):
    duelist = 'Seto 3rd'
    poolType = 'Deck'
    BEUD_id = 380

    # player_card = (get_card_from_name(cards, player_cardname), star, mode)  # card, star, 'Attack'/'Defense'

    # Pool type id
    pool_typeID = None
    for id in cur.execute(
            f"SELECT DuelistPoolTypeID "
            f"FROM DuelistPoolTypes "
            f"WHERE DuelistPoolTypes.DuelistPoolType = \"{poolType}\""
    ):
        pool_typeID, = id

    # Hand size
    hand_size = None
    for h in cur.execute(
            f"SELECT HandSize "
            f"FROM Duelists "
            f"WHERE Duelists.DuelistName = \"{duelist}\" "
    ):
        hand_size, = h
    # print(hand_size)

    # (cardID, prob) list
    cards_probs = list(cur.execute(
        f"SELECT CardID, Prob "
        f"FROM DuelistPoolSamplingRates "
        f"LEFT JOIN Duelists ON Duelists.DuelistID = DuelistPoolSamplingRates.DuelistID "
        f"WHERE DuelistPoolSamplingRates.DuelistPoolTypeID = {pool_typeID} "
        f"AND Duelists.DuelistName = \"{duelist}\" "
        f"AND DuelistPoolSamplingRates.Prob > 0 "
    ))

    CARD_LIMIT = 3
    CARD_LIMIT_EXODIA = 1

    traps = {k: None for k in cur.execute(
        f"SELECT CardID "
        f"FROM Cards "
        f"WHERE CardType = 'Trap'"
    )}
    equips = {k: None for k in cur.execute(
        f"SELECT CardID "
        f"FROM Cards "
        f"WHERE CardType = 'Equip'"
    )}
    magics = {k: None for k in cur.execute(
        f"SELECT CardID "
        f"FROM Cards "
        f"WHERE CardType = 'Magic'"
    )}
    rituals = {k: None for k in cur.execute(
        f"SELECT CardID "
        f"FROM Cards "
        f"WHERE CardType = 'Ritual'"
    )}

    nb_useful_samples = [0]*20
    nb_useful_samples[0] = NUM_SIMU
    # id 0 is turn 1, etc.
    BEUD_number_per_turn = [0]*20
    for _ in range(NUM_SIMU):
        cards_probs_nums = [
            [id, prob, CARD_LIMIT if id not in range(17, 21 + 1) else CARD_LIMIT_EXODIA] for (id, prob) in cards_probs
        ]

        # Build Deck
        DECK_SIZE = 40
        PROB, NUM = 1, 2
        deck_ids = []
        # print(clean_desc(cur.execute("SELECT * FROM Cards").description))
        for _ in range(DECK_SIZE):
            chosen, = random.choices(cards_probs_nums, weights=[prob for (_, prob, _) in cards_probs_nums])
            # print(chosen)
            deck_ids.append(chosen[0])
            chosen[NUM] -= 1
            if chosen[NUM] == 0:
                chosen[PROB] = 0
        # print(deck_ids)

        # Count BEUD number and retry if zero
        BEUD_number = 0
        for id in deck_ids:
            if id == BEUD_id:
                BEUD_number += 1

        # if BEUD_number == 0:
        #     continue

        random.shuffle(deck_ids)

        # Draw
        hand_ids: list = None
        previously_played_id = None
        for turn in range(1, 20+1):
            # if BEUD_number == 0:
            #     break

            if turn == 1:
                hand_ids = deck_ids[:hand_size]
                deck_ids = deck_ids[hand_size:]
            else:
                hand_ids.remove(previously_played_id)
                if len(deck_ids) > 0:
                    drawn_id = deck_ids[0]
                    hand_ids.append(drawn_id)
                    del deck_ids[0]
                pass

            # Choose card to play
            ## Assumes not in control
            previously_played_id = None
            max_stat = -1
            card_to_play = None
            for id in hand_ids:
                enemy_atk = cards[id-1][ATTACK]
                enemy_def = cards[id-1][DEFENSE]

                if enemy_atk > max_stat:
                    previously_played_id = id
                    max_stat = enemy_atk

                if enemy_def > max_stat:
                    previously_played_id = id
                    max_stat = enemy_def

            if previously_played_id is None:
                previously_played_id = random.choice(hand_ids[:5])

            if previously_played_id == BEUD_id:
                BEUD_number_per_turn[turn-1] += 1
                # BEUD_number -= 1
                break
            else:
                if turn > 1:
                    nb_useful_samples[turn-1] += 1

    return BEUD_number_per_turn, nb_useful_samples


def heishin_MM(NUM_SIMU=1_000):
    duelist = 'Heishin'
    odds_to_frontrow_in_control = 0.7
    poolType = 'Deck'
    MM_id = 657
    DK_id = 342

    # player_card = (get_card_from_name(cards, player_cardname), star, mode)  # card, star, 'Attack'/'Defense'

    # Pool type id
    pool_typeID = None
    for id in cur.execute(
            f"SELECT DuelistPoolTypeID "
            f"FROM DuelistPoolTypes "
            f"WHERE DuelistPoolTypes.DuelistPoolType = \"{poolType}\""
    ):
        pool_typeID, = id

    # Hand size
    hand_size = None
    for h in cur.execute(
            f"SELECT HandSize "
            f"FROM Duelists "
            f"WHERE Duelists.DuelistName = \"{duelist}\" "
    ):
        hand_size, = h
    # print(hand_size)

    # (cardID, prob) list
    cards_probs = list(cur.execute(
        f"SELECT CardID, Prob "
        f"FROM DuelistPoolSamplingRates "
        f"LEFT JOIN Duelists ON Duelists.DuelistID = DuelistPoolSamplingRates.DuelistID "
        f"WHERE DuelistPoolSamplingRates.DuelistPoolTypeID = {pool_typeID} "
        f"AND Duelists.DuelistName = \"{duelist}\" "
        f"AND DuelistPoolSamplingRates.Prob > 0 "
    ))

    CARD_LIMIT = 3
    CARD_LIMIT_EXODIA = 1

    traps = {k: None for k in cur.execute(
        f"SELECT CardID "
        f"FROM Cards "
        f"WHERE CardType = 'Trap'"
    )}
    equips = {k: None for k in cur.execute(
        f"SELECT CardID "
        f"FROM Cards "
        f"WHERE CardType = 'Equip'"
    )}
    magics = {k: None for k in cur.execute(
        f"SELECT CardID "
        f"FROM Cards "
        f"WHERE CardType = 'Magic'"
    )}
    rituals = {k: None for k in cur.execute(
        f"SELECT CardID "
        f"FROM Cards "
        f"WHERE CardType = 'Ritual'"
    )}

    # nb_useful_samples = [0]*20
    # nb_useful_samples[0] = NUM_SIMU
    # id 0 is turn 1, etc.
    # BEUD_number_per_turn = [0]*20
    number_of_MM_combo = 0
    number_of_MM_no_monster = 0
    number_of_no_MM_monster = 0
    number_of_MM_monster = 0

    for _ in range(NUM_SIMU):
        cards_probs_nums = [
            [id, prob, CARD_LIMIT if id not in range(17, 21 + 1) else CARD_LIMIT_EXODIA] for (id, prob) in cards_probs
        ]

        # Build Deck
        DECK_SIZE = 40
        PROB, NUM = 1, 2
        deck_ids = []
        # print(clean_desc(cur.execute("SELECT * FROM Cards").description))
        for _ in range(DECK_SIZE):
            chosen, = random.choices(cards_probs_nums, weights=[prob for (_, prob, _) in cards_probs_nums])
            # print(chosen)
            deck_ids.append(chosen[0])
            chosen[NUM] -= 1
            if chosen[NUM] == 0:
                chosen[PROB] = 0
        # print(deck_ids)

        random.shuffle(deck_ids)

        # Draw
        hand_ids = deck_ids[:hand_size]

        # Choose card to play
        ## Assumes not in control
        previously_played_id = None
        max_stat = -1
        position = None
        first_MM_position = None
        first_DK_position = None
        has_2_DK = False
        already_MM_this_try = False
        for i, id in enumerate(hand_ids):
            if first_MM_position is None and id == MM_id:
                first_MM_position = i

            if first_DK_position is not None and id == DK_id:
                has_2_DK = True

            if first_DK_position is None and id == DK_id:
                first_DK_position = i

            enemy_atk = cards[id-1][ATTACK]
            enemy_def = cards[id-1][DEFENSE]

            if enemy_atk > max_stat:
                previously_played_id = id
                max_stat = enemy_atk
                position = i

            if enemy_def > max_stat:
                previously_played_id = id
                max_stat = enemy_def
                position = i

        if previously_played_id is None or (first_MM_position is None and not has_2_DK):
            number_of_MM_no_monster += (first_MM_position is not None)
            number_of_no_MM_monster += (previously_played_id is not None and not has_2_DK)
            continue

        # number_of_MM_monster += 1

        if first_MM_position is not None and \
            (first_MM_position < position or cards[previously_played_id-1][TYPE] in ['Fiend', 'Spellcaster']) \
        or has_2_DK and (first_DK_position < position or cards[previously_played_id-1][TYPE] in ['Fiend', 'Spellcaster']):
            number_of_MM_combo += 1

    return {"number_of_MM_combo": round(odds_to_frontrow_in_control * 10_000 * number_of_MM_combo/NUM_SIMU) / 100,
            # "number_of_MM_monster": round(odds_to_frontrow_in_control * 10_000 * number_of_MM_monster/NUM_SIMU) / 100,
            "number_of_MM_no_monster": round(odds_to_frontrow_in_control * 10_000 * number_of_MM_no_monster/NUM_SIMU) / 100,
            "number_of_no_MM_monster": round(odds_to_frontrow_in_control * 10_000 * number_of_no_MM_monster/NUM_SIMU) / 100,
            }


def meadow_mage_swords_backrow(NUM_SIMU=1_000):
    duelist = 'Meadow Mage'
    odds_to_backrow_in_control = 0.15
    poolType = 'Deck'
    MM_id = 657
    DK_id = 342
    swords_ID = 348

    # player_card = (get_card_from_name(cards, player_cardname), star, mode)  # card, star, 'Attack'/'Defense'

    # Pool type id
    pool_typeID = None
    for id in cur.execute(
            f"SELECT DuelistPoolTypeID "
            f"FROM DuelistPoolTypes "
            f"WHERE DuelistPoolTypes.DuelistPoolType = \"{poolType}\""
    ):
        pool_typeID, = id

    # Hand size
    hand_size = None
    for h in cur.execute(
            f"SELECT HandSize "
            f"FROM Duelists "
            f"WHERE Duelists.DuelistName = \"{duelist}\" "
    ):
        hand_size, = h
    # print(hand_size)

    # (cardID, prob) list
    cards_probs = list(cur.execute(
        f"SELECT CardID, Prob "
        f"FROM DuelistPoolSamplingRates "
        f"LEFT JOIN Duelists ON Duelists.DuelistID = DuelistPoolSamplingRates.DuelistID "
        f"WHERE DuelistPoolSamplingRates.DuelistPoolTypeID = {pool_typeID} "
        f"AND Duelists.DuelistName = \"{duelist}\" "
        f"AND DuelistPoolSamplingRates.Prob > 0 "
    ))

    CARD_LIMIT = 3
    CARD_LIMIT_EXODIA = 1

    traps = {k: None for k, in cur.execute(
        f"SELECT CardID "
        f"FROM Cards "
        f"WHERE CardType = 'Trap'"
    )}
    equips = {k: None for k, in cur.execute(
        f"SELECT CardID "
        f"FROM Cards "
        f"WHERE CardType = 'Equip'"
    )}
    magics = {k: None for k, in cur.execute(
        f"SELECT CardID "
        f"FROM Cards "
        f"WHERE CardType = 'Magic'"
    )}
    rituals = {k: None for k, in cur.execute(
        f"SELECT CardID "
        f"FROM Cards "
        f"WHERE CardType = 'Ritual'"
    )}

    # nb_useful_samples = [0]*20
    # nb_useful_samples[0] = NUM_SIMU
    # id 0 is turn 1, etc.
    # BEUD_number_per_turn = [0]*20
    swords_in_hand, swords_backrow = 0, 0

    for _ in range(NUM_SIMU):
        cards_probs_nums = [
            [id, prob, CARD_LIMIT if id not in range(17, 21 + 1) else CARD_LIMIT_EXODIA] for (id, prob) in cards_probs
        ]

        # Build Deck
        DECK_SIZE = 40
        PROB, NUM = 1, 2
        deck_ids = []
        # print(clean_desc(cur.execute("SELECT * FROM Cards").description))
        for _ in range(DECK_SIZE):
            chosen, = random.choices(cards_probs_nums, weights=[prob for (_, prob, _) in cards_probs_nums])
            # print(chosen)
            deck_ids.append(chosen[0])
            chosen[NUM] -= 1
            if chosen[NUM] == 0:
                chosen[PROB] = 0
        # print(deck_ids)

        random.shuffle(deck_ids)

        # Draw
        hand_ids = deck_ids[:hand_size]

        # Choose card to play
        ## Assumes in control
        previously_played_id = None
        max_stat = -1
        swords_pos = None
        first_magic_pos = None
        for i, id_ in enumerate(hand_ids):
            if id_ == swords_ID:
                swords_in_hand += 1
                if swords_pos is None:
                    swords_pos = i
            if id_ in magics and first_magic_pos is None:
                first_magic_pos = i

        if swords_pos is not None and swords_pos == first_magic_pos:
            swords_backrow += 1

    return {
        "Swords in hand": round(odds_to_backrow_in_control * 1_000_000 * swords_in_hand/NUM_SIMU) / 10_000,
        "Swords backrow": round(odds_to_backrow_in_control * 1_000_000 * swords_backrow/NUM_SIMU) / 10_000,
    }


def choose_card_t1(cards_probs, hand_size):  # card, star, 'Attack'/'Defense'
    CARD_LIMIT = 3
    CARD_LIMIT_EXODIA = 1

    cards_probs_nums = [
        [id, prob, CARD_LIMIT if id not in range(17, 21 + 1) else CARD_LIMIT_EXODIA] for (id, prob) in cards_probs
    ]

    # Build Deck
    DECK_SIZE = 40
    PROB, NUM = 1, 2
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

    # Draw
    random.shuffle(deck_ids)
    hand_ids = deck_ids[:hand_size]
    # print(hand_ids)

    hand = [cards[id - 1] for id in hand_ids]
    # print(hand)

    # Choose card to play
    max_stat = -1
    card_to_play = None
    for enemy_card in hand:
        enemy_atk = enemy_card[ATTACK]
        enemy_def = enemy_card[DEFENSE]

        if enemy_atk > max_stat:
            card_to_play = enemy_card
            max_stat = enemy_atk

        if enemy_def > max_stat:
            card_to_play = enemy_card
            max_stat = enemy_def

    return card_to_play, [card[NAME] for card in hand]


def clean_desc(desc):
    return [col[0] for col in desc]


def get_card_from_name(cards, player_cardname):
    for card in cards:
        if card[NAME] == player_cardname:
            return card

    return None


def id_dic_to_name_dic(dic, cards):
    total = 0
    new_dic = {}
    for (id, val) in dic.items():
        total += val
        name = cards[id-1][NAME]
        new_dic[name] = val

    # Convert to 3-decimal percentages
    for (name, val) in new_dic.items():
        new_dic[name] = int(100_000 * val / total) / 1_000

    return new_dic


def id_dic_to_star1_dic(dic, cards):
    new_dic = {}
    total = 0
    for id, val in dic.items():
        total += val

        star1 = cards[id-1][STAR1]

        star1_dic = new_dic[star1] if star1 in new_dic else {}
        new_dic[star1] = star1_dic

        if id in star1_dic:
            star1_dic[cards[id-1][NAME]] += val
        else:
            star1_dic[cards[id-1][NAME]] = val

    # Convert to 3-decimal percentages
    for star, d in new_dic.items():
        star_total = sum(val for val in d.values())
        for (name, val) in d.items():
            d[name] = int(100_000 * d[name] / star_total) / 1_000
        new_dic[star] = (int(100_000 * star_total / total) / 1_000, new_dic[star])

    return dict(sorted(new_dic.items(), key=lambda item: item[1][0], reverse=True))


def gradient_odds(dic, cards, field):
    total = 0
    player_win_odds = {}
    # print(f"Start gradient : {dic}")
    for id, occurrences in dic.items():
        total += occurrences
        card = cards[id-1]
        _atk = card[ATTACK]
        _def = card[DEFENSE]
        star = card[STAR1]
        # type = card[TYPE]
        stat = max(_atk, _def)
        if is_boosted(card, field):
            stat += 500
        if is_nerfed(card, field):
            stat -= 500
        if stat < 0:
            stat = 0
        # print(f"{stat=}, {star=}, {occurrences=}")
        for player_star in ['Sun', 'Moon', 'Venus', 'Mercury', 'Pluto', 'Neptune', 'Mars', 'Jupiter', 'Saturn', 'Uranus']:
            stat_copy = stat
            star_dic = player_win_odds[player_star] if player_star in player_win_odds else {}
            player_win_odds[player_star] = star_dic
            # stat_orig = stat
            if has_advantage_over(star, player_star):
                stat_copy += 500
            if has_advantage_over(player_star, star):
                stat_copy -= 500
            if stat_copy < 0:
                stat_copy = 0

            if stat_copy in star_dic:
                star_dic[stat_copy] += occurrences
            else:
                star_dic[stat_copy] = occurrences

    # Sort by Atk
    player_win_odds = {star: dict(sorted(star_dic.items(), reverse=True)) for star, star_dic in player_win_odds.items()}

    # Cumulate
    for star, star_dic in player_win_odds.items():
        total_num = 0
        for stat, num in star_dic.items():
            total_num += num
            player_win_odds[star][stat] = total_num

    # Convert to 3-decimal percentages
    for star, star_dic in player_win_odds.items():
        for stat, num in star_dic.items():
            player_win_odds[star][stat] = int(100_000 * num / total) / 1_000

    return player_win_odds


def print_star_dic(dic):
    atks = {}
    for _, d in dic.items():
        for atk, _ in d.items():
            atks[atk] = None

    # print(list(sorted(atks.keys(), reverse=True)))
    for star, d in dic.items():
        atks_copy = list(sorted(atks.keys(), reverse=True))
        print("{:>7}: ".format(star), end='')
        print("{", end='')
        for atk, prob in d.items():
            for a in list(atks_copy):
                atks_copy.remove(a)
                if a > atk:
                    print(" "*(4+2+6+1), end='')
                else:
                    print("{:4d}: {:6.2f} ".format(atk, prob), end='')
                    break
        print("}")


def print_draws_information(field=None, NB_DRAWS=1_000):
    poolType = 'Deck'

    # player_card = (get_card_from_name(cards, player_cardname), star, mode)  # card, star, 'Attack'/'Defense'

    # Pool type id
    pool_typeID = None
    for id in cur.execute(
            f"SELECT DuelistPoolTypeID "
            f"FROM DuelistPoolTypes "
            f"WHERE DuelistPoolTypes.DuelistPoolType = \"{poolType}\""
    ):
        pool_typeID, = id

    print(f"Draws : {NB_DRAWS}")
    # if player_cardname is not None:
    #     print(f"vs. '{player_cardname}', '{star}', {mode}")
    # print()

    for duelist, fields in duelists_field.items():
        # Hand size
        hand_size = None
        for h in cur.execute(
                f"SELECT HandSize "
                f"FROM Duelists "
                f"WHERE Duelists.DuelistName = \"{duelist}\" "
        ):
            hand_size, = h
        # print(hand_size)

        # (cardID, prob) list
        cards_probs = list(cur.execute(
            f"SELECT CardID, Prob "
            f"FROM DuelistPoolSamplingRates "
            f"LEFT JOIN Duelists ON Duelists.DuelistID = DuelistPoolSamplingRates.DuelistID "
            f"WHERE DuelistPoolSamplingRates.DuelistPoolTypeID = {pool_typeID} "
            f"AND Duelists.DuelistName = \"{duelist}\" "
            f"AND DuelistPoolSamplingRates.Prob > 0 "
        ))

        for field in fields:
            if field != 'Yami':
                break
            # Draws
            draw_dic = {}

            for _ in range(NB_DRAWS):
                # card_to_play, hand = choose_card(cards_probs, hand_size)
                card_to_play, hand = choose_card_t1(cards_probs, hand_size)

                cardname = card_to_play[ID]
                if card_to_play[ID] in draw_dic:
                    draw_dic[cardname] += 1
                else:
                    draw_dic[cardname] = 1

            # Sort from highest to lowest occurrence rate
            draw_dic = dict(sorted(draw_dic.items(), key=lambda item: item[1], reverse=True))

            print(f"Opponent : '{duelist}' (hand size : {hand_size})")
            if field is not None:
                print(f"on field '{field}")
            # print(draw_dic)
            print(f"Turn 1 draws (%) : {id_dic_to_name_dic(draw_dic, cards)}")
            star_dic = id_dic_to_star1_dic(draw_dic, cards)
            print(f"Turn 1 draws, grouped by opponent star (%) : {star_dic}")

            print(f"Turn 1 odds to tie, grouped by player star (%) : ")
            print_star_dic(gradient_odds(draw_dic, cards, field=field))
            print()


def fn():
    pass


if __name__ == '__main__':
    dbfile = 'YFM.db'
    # Create a SQL connection to our SQLite database
    con = sqlite3.connect(dbfile)
    # creating cursor
    cur = con.cursor()

    # reading all table names
    table_list = [a for a in cur.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
    print(table_list)

    duelists_field = {}
    # duelists_field['Guardian Neku'] = ['Yami']
    for row in cur.execute("SELECT * FROM Duelists"):
        duelists_field[row[1]] = [None]
    duelists_field['Heishin'].insert(0, 'Yami')
    duelists_field['Ocean Mage'].insert(0, 'Umi')
    duelists_field['High Mage Secmeton'].insert(0, 'Umi')
    duelists_field['Forest Mage'].insert(0, 'Forest')
    duelists_field['High Mage Anubisius'].insert(0, 'Forest')
    duelists_field['Mountain Mage'].insert(0, 'Mountain')
    duelists_field['High Mage Atenza'].insert(0, 'Mountain')
    duelists_field['Desert Mage'].insert(0, 'Desert')
    duelists_field['High Mage Martis'].insert(0, 'Desert')
    duelists_field['Meadow Mage'].insert(0, 'Sogen')
    duelists_field['High Mage Kepura'].insert(0, 'Sogen')
    duelists_field['Guardian Sebek'].insert(0, 'Yami')
    duelists_field['Guardian Neku'].insert(0, 'Yami')
    duelists_field['Heishin 2nd'].insert(0, 'Yami')

    for (table_name,) in table_list:
        print(f'{table_name} : {clean_desc(cur.execute(f"SELECT * FROM {table_name}").description)}')

    # for row in cur.execute(f"SELECT * FROM Fusions"):
    #     print(row)

    cards = list(cur.execute(
        f"SELECT * "
        f"FROM Cards "
    ))
    # print(cards)

    ########
    # ARGS #
    ########
    # player_cardname, star, mode = None, None, None
    # player_cardname, star, mode = 'Twin-headed Thunder Dragon', 'Pluto', 'Attack'
    # NB_DRAWS = 1_000_000
    # duelist = 'Seto 3rd'
    # field = None

    ########
    # CODE #
    ########
    # print_draws_information(NB_DRAWS=NB_DRAWS)

    # NUM_SIMU = 1_000_000
    # top_deck, nb_useful_samples = seto3_topdecks(NUM_SIMU=NUM_SIMU)
    # print(top_deck, nb_useful_samples)
    # top_deck = [100*i/n for i, n in zip(top_deck, nb_useful_samples)]
    # print(f"Odds of 1st time seing BEUD : {top_deck}")

    # NUM_SIMU = 10_000
    # MM_data = heishin_MM(NUM_SIMU=NUM_SIMU)
    # print(f"{NUM_SIMU} draws | Percent of ting ting on Heishin : {MM_data}")

    NUM_SIMU = 100_000
    MM_data = meadow_mage_swords_backrow(NUM_SIMU=NUM_SIMU)
    print(f"{NUM_SIMU} draws | Swords Meadow Mage : {MM_data}")


    con.close()
