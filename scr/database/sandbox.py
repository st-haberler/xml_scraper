import sqlite3

con = sqlite3.connect(":memory:")

cursor = con.cursor()


cursor.execute("""
CREATE TABLE document (
    doc_id INTEGER PRIMARY KEY, 
    source_type INTEGER NOT NULL,
    tech_id TEXT NOT NULL
);
""")

cursor.execute("""
CREATE TABLE paragraph (
    para_id INTEGER PRIMARY KEY, 
    text TEXT NOT NULL,
    doc_id INTEGER NOT NULL,
    FOREIGN KEY (doc_id) REFERENCES document(doc_id)
);
""")

cursor.execute("""
CREATE TABLE annotation (
    anntotation_id INTEGER PRIMARY KEY,
    para_id INTEGER NOT NULL,
    begin_token INTEGER NOT NULL,
    end_token INTEGER NOT NULL,
    label TEXT NOT NULL,
    version INTEGER NOT NULL,
    FOREIGN KEY (para_id) REFERENCES paragraph(para_id)
);
""")

cursor.execute("""
CREATE TABLE meta_judikatur (
    meta_index INTEGER PRIMARY KEY,
    doc_id INTEGER NOT NULL,
    geschaeftszahl TEXT NOT NULL,
    entscheidungsdatum TEXT NOT NULL,
    branch TEXT NOT NULL,
    gericht TEXT NOT NULL,
    FOREIGN KEY (doc_id) REFERENCES paragraph(doc_id)
);
""")

cursor.execute("""
CREATE TABLE meta_bundesrecht (
    meta_index INTEGER PRIMARY KEY,
    doc_id INTEGER NOT NULL,
    kurztitel TEXT,
    titel TEXT,
    paragraphennummer INTEGER, 
    artikelnummer INTEGER,
    gesetzesnummer INTEGER, 
    FOREIGN KEY (doc_id) REFERENCES paragraph(doc_id)
);
""")
    
   
               


cursor.execute("""
INSERT INTO document (source_type, tech_id) VALUES (1, "N123");
""")

cursor.execute("""
INSERT INTO paragraph (text, doc_id) VALUES ("Dies ist ein Test", 1);
""")
cursor.execute("""
INSERT INTO paragraph (text, doc_id) VALUES ("Noch ein Test", 1);
""")


# con.commit()

res = cursor.execute("""
SELECT document.tech_id, paragraph.text FROM document JOIN paragraph ON document.doc_id = paragraph.doc_id;
""")

print(res.fetchall())

