import sqlite3

dbfile = 'YFM.db'

# Create a SQL connection to our SQLite database
con = sqlite3.connect(dbfile)
# creating cursor
cur = con.cursor()
cur.execute(f"SELECT EquippedID FROM Equipping "
                  f"WHERE EquippedID = 12 AND EquipID = 301")

print(cur.fetchone())
