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

    for decision in result[:2]:
        print(f"{decision.applikation = }")
        print(f"{decision.gericht = }")
        print(f"{decision.geschaeftszahl = }")
        print(f"{decision.tech_id = }")
        print(f"{decision.id = }")
        for para in decision.paragraphs:
            print(f"{para.text[:50] = }")
            print(f"{para.id = }")
            print(f"{para.index = }")
            print(f"{para.document_id = }")
            print("-------------------")
        print("=====================================")

Path("test.db").unlink()