import sqlite3

import ai_board
import db
import utils

con, cur = db.connect_to_YFM_database()

print([utils.get_card_id_from_name(cur, name) for name in ai_board.forced_defend_monsters])

con.close()
