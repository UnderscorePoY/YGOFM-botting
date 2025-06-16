# import ai_board
# import db
# import utils
from typing import override


# con, cur = db.connect_to_YFM_database()
#
# print([utils.get_card_id_from_name(cur, name) for name in ai_board.forced_defend_monsters])
#
# con.close()

class StrIndex:
    def __init__(self, string: str):
        self.string = string

    def __len__(self):
        return len(self.string)


class Things(list[int | None]):
    def __init__(self, cards: list[int | None]):
        super().__init__(cards)

    @override
    def __getitem__(self, string: StrIndex):
        return super().__getitem__(len(string))


if __name__ == '__main__':
    frontrow = Things([54, 21, 64, None, None])
    print(frontrow[StrIndex("")])
