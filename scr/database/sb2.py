from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session


import models
import db_import

engine = create_engine("sqlite:///test.db", echo=False)
# models.Base.metadata.create_all(engine)
with Session(engine) as session:
    # db_import.populate_from_xml_collection(Path(r"data\judikatur\vfgh\meta_data\vfgh_meta_collection_all_2021.xml"), session)
    # db_import.populate_from_html(session)
    # ann_1 = models.Annotation(label="TEST_1", begin=0, end=1, version=0, paragraph_id=3)
    # ann_2 = models.Annotation(label="TEST_2", begin=3, end=4, version=0, paragraph_id=4)
    # session.add(ann_1)
    # session.add(ann_2)
    # session.commit()

    q = select(models.Document).where(models.Document.applikation == "Vfgh")
    result = session.scalars(q).all()

    for decision in result[:1]:
        print(f"{decision.applikation = }")
        print(f"{decision.gericht = }")
        print(f"{decision.geschaeftszahl = }")
        print(f"{decision.tech_id = }")
        print(f"{decision.id = }")
        for para in decision.paragraphs[:2]:
            print(f"{para.text[:50] = }")
            print(f"{para.id = }")
            print(f"{para.index = }")
            print(f"{para.document_id = }")
            print("-------------------")
        print("=====================================")

a1 = models.Annotation(label="TEST_1", begin=0, end=1, version=0, paragraph_id=70)
a2 = models.Annotation(label="TEST_2", begin=3, end=4, version=0, paragraph_id=71)

with Session(engine) as session:
    # session.add(a1)
    # session.add(a2)
    # session.commit()
    q = select(models.Annotation)
    result = session.scalars(q).all()
    for a in result:
        print(f"{a.label = }")
        print(f"{a.begin = }")
        print(f"{a.end = }")
        print(f"{a.version = }")
        print(f"{a.paragraph_id = }")
        print(f"{a.id = }")
        print("-------------------")