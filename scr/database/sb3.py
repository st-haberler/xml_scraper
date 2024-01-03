import sqlite3

conn = sqlite3.connect('test.db')

c = conn.cursor()




c.execute("SELECT text FROM paragraphs JOIN documents ON paragraphs.document_id = documents.id WHERE documents.id = 3;")
# for p in c.fetchall():
#     print(p, "\n------------------\n")





# find all documents with exactly one paragraph
c.execute("""SELECT ris_link, geschaeftszahl 
          FROM documents JOIN paragraphs ON documents.id = paragraphs.document_id 
          GROUP BY documents.id 
          HAVING COUNT(*) = 1;""")

# for res in c.fetchall():
#     print(res)

# find all documents that are not referenced by any paragraph
c.execute("""SELECT COUNT(geschaeftszahl)
          FROM documents 
          WHERE documents.id NOT IN (SELECT document_id FROM paragraphs);""")

print("not referenced:", c.fetchone())

# find all documents 
c.execute("""SELECT COUNT(*)
          FROM documents;""")

print("all documents:", c.fetchone())