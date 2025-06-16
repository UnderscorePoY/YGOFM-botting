# from utils import *
import sqlite3
from sqlite3 import Connection, Cursor


class YGOFMDatabase:  # TODO: implement and use
    def __init__(self, db_filename: str = 'YFM.db'):
        self.filename = db_filename
        self.connection: Connection | None = None
        self.cursor: Cursor | None = None

    def __enter__(self):
        self.connection = sqlite3.connect(self.filename)
        self.cursor = self.connection.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()


def connect_to_YFM_database(db_file='YFM.db'):
    # Create a SQL connection to our SQLite database
    con = sqlite3.connect(db_file)
    # creating cursor
    cur = con.cursor()

    return con, cur


def clean_desc(desc):
    return [col[0] for col in desc]


def print_equip_list_by_monster(cursor: Cursor):
    monsters = [row for row in cursor.execute(
        f"SELECT CardID, CardName "
        f"FROM 'Cards' "
        f"WHERE Attack > 0 "
        f"   OR Defense > 0 "
        f"ORDER BY CardName ASC"
    )]

    for monster_id, monster_name in monsters:
        equips = [row for row, in cursor.execute(
            f"SELECT CardName "
            f"FROM 'Cards' "
            f"WHERE CardName NOT IN ('Megamorph', 'Bright Castle') "
            f"AND CardID IN ("
            f"SELECT EquipID "
            f"FROM Equipping "
            f"WHERE EquippedID = {monster_id} "
            f") ORDER BY CardName ASC"
        )]

        print(monster_name)
        for equip_name in equips:
            print(f" {equip_name}")
        print()


def print_monster_list_by_equip(cur):
    equips = [row for row in
              cur.execute(f"SELECT CardID, CardName FROM 'Cards' WHERE CardType = 'Equip' ORDER BY CardName")]
    print(equips)
    for equip_id, equip_name in equips:
        monsters = [row for row in cur.execute(
            f"SELECT CardName, Attack, Defense, GuardianStar1, GuardianStar2, CardType "
            f"FROM 'Cards' WHERE CardID IN "
            f"(SELECT EquippedID "
            f"FROM 'Equipping' "
            f"WHERE EquipID = '{equip_id}'"
            f") "
            f"ORDER BY MAX(Attack, Defense) DESC, CardName ASC"
        )]

        max_name_len, max_atk_digits, max_def_digits = 0, 0, 0
        max_gs1_len, max_gs2_len, max_type_len = 0, 0, 0
        for monster_name, _atk, _def, gs1, gs2, _type in monsters:
            max_name_len = max(max_name_len, len(monster_name))
            max_atk_digits = max(max_atk_digits, len(str(_atk)))
            max_def_digits = max(max_def_digits, len(str(_def)))
            max_gs1_len = max(max_gs1_len, len(str(gs1)))
            max_gs2_len = max(max_gs2_len, len(str(gs2)))
            max_type_len = max(max_type_len, len(str(_type)))

        print(equip_name)
        for monster_name, _atk, _def, gs1, gs2, _type in monsters:
            template = " {name:<{name_len}s} {atk:>{atk_len}d} {ddef:>{def_len}d} {gs1:<{gs1_len}s} {gs2:<{gs2_len}s} {ttype:<{type_len}s}"\
                .format(name=monster_name, atk=_atk, ddef=_def, name_len=max_name_len, atk_len=max_atk_digits, def_len=max_def_digits,
                        gs1=gs1, gs1_len=max_gs1_len, gs2=gs2, gs2_len=max_gs2_len, ttype=_type, type_len=max_type_len)
            print(template)
        print()


def print_lukadevv_json_for_duelists_per_pool_type(cur):
    duelists = [row for row in cur.execute(f"SELECT DuelistID, DuelistName FROM 'Duelists'")]
    print(duelists)
    pools = [row for row in cur.execute(f"SELECT DuelistPoolTypeID, DuelistPoolType FROM 'DuelistPoolTypes'")]
    for duelist_id, duelist_name in duelists:
        for pool_type_id, pool_type in pools:
            cards = [_id for _id, in cur.execute(f"SELECT CardID "
                                     f"FROM 'DuelistPoolSamplingRates' "
                                     f"WHERE DuelistID = '{duelist_id}' "
                                     f"AND DuelistPoolTypeID = '{pool_type_id}' "
                                     f"AND Prob > 0 "
                                     f"ORDER BY CardID ASC"
            )]
            _str = '{start}"id":"{id}","name":"{name}","cards":{cards}{end}'.format(start="{", end="}", id="", name=f"{duelist_name} {pool_type}", cards=[f'"{_id}"' for _id in cards])
            print(_str.replace("'", ""))
        print()


if __name__ == '__main__':
    con, cur = connect_to_YFM_database()

    table_list = [a for a in cur.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
    print(table_list)
    for (table_name,) in table_list:
        print(f'{table_name} : {clean_desc(cur.execute(f"SELECT * FROM {table_name}").description)}')

    # print_monster_list_by_equip(cur)
    # print_equip_list_by_monster(cur)
    # print_lukadevv_json_for_duelists_per_pool_type(cur)

    # print(list(cur.execute(f"SELECT * FROM 'Duelists'")))
    # print(list(cur.execute(f"SELECT * FROM 'DuelistPoolSamplingRates'")))
    print(list(cur.execute(f"SELECT DISTINCT CardType FROM 'Cards'")))

    con.close()
