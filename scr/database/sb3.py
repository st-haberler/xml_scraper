import sqlite3

conn = sqlite3.connect('test.db')

c = conn.cursor()

# show all tables
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(c.fetchall())

# show the number of rows in table documents
c.execute("SELECT tech_id FROM documents WHERE documents.id = 1;")
print(c.fetchall())

c.execute("SELECT COUNT(*) FROM paragraphs;")
print(c.fetchall())
c.execute("SELECT text FROM paragraphs JOIN documents ON paragraphs.document_id = documents.id WHERE documents.id = 3;")
for p in c.fetchall():
    print(p, "\n------------------\n")



c.execute("SELECT COUNT(*) FROM annotations;")
print(c.fetchall())