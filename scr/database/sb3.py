from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

import models


engine = create_engine("sqlite:///test.db", echo=False)
with Session(engine) as session: 
    q = select(models.Document).where(models.Document.applikation == "VfGH")
    db_documents = session.scalars(q).all()
    
    for d in db_documents[:1]: 
        print(d.kurztitel)
        print(f"{d.tech_id = }, {d.id = }")
        print(f"{len(d.paragraphs) = }")
        print(f"{d.paragraphnummer = }")
        for p in d.paragraphs:
            print(f"    {p.document_id = }") 
            print(f"    {p.index = }")
            print(f"    {p.text = }")
            print(f"    {p.id = }")
            print("-------------------")
        print("=====================================")


    l1 = models.Annotation(label="TEST", begin=0, end=1, version=0, )
    l2 = models.Annotation(label="TEST", begin=3, end=4, version=0)
    l3 = models.Annotation(label="TEST_2", begin=6, end=7, version=0)
    l4 = models.Annotation(label="TEST_3", begin=9, end=10, version=0)
    l5 = models.Annotation(label="TEST_3", begin=10, end=11, version=0)


    for ann in [l1, l2, l3, l4, l5]:
        session.add(ann)