import sqlite3

TEST = "SELECT * FROM users"

conn = sqlite3.connect("users.db")
c = conn.cursor()
arr = c.execute(TEST).fetchall()
print (arr)