import sqlite3


conn = sqlite3.connect('instapy.db')

c = conn.cursor()

c.execute('SELECT * FROM statistics')
print(c.fetchall())

# c.execute("INSERT INTO statistics VALUES (21, 1, 1, 1, 1, '03-01-2017', '03-01-2017')")
#conn.commit()

c.close()
conn.close()

