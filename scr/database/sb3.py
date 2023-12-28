import sqlite3

conn = sqlite3.connect('test.db')

c = conn.cursor()

# show all tables
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(c.fetchall())

# show the number of rows in table documents
c.execute("SELECT COUNT(*) FROM documents;")
print(c.fetchall())