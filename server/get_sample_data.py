import sqlite3
import hashlib

conn = sqlite3.connect("userdata.db")
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS userdata (
	id INTEGER PRIMARY KEY,
	username VARCHAR(255) NOT NULL,
	password VARCHAR(255) NOT NULL
)
""")

details = [
    ["mike213", "epicPAZSSSWORD"]
]

for i in details:
    cur.execute("INSERT INTO userdata (username, password) VALUES (?, ?)",
                (i[0], hashlib.sha256(
                    i[1].encode()).hexdigest()))
conn.commit()
