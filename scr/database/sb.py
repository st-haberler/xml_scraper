from typing import List

from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session

import models



engine = create_engine("sqlite:///test.db", echo=False)


def get_all_Gesetze() -> List[models.Document]: 
    with Session(engine) as session:
        q = select(models.Document).where(models.Document.applikation == "BrKons").group_by(models.Document.gesetzesnummer)
        result = session.scalars(q).all()
        return result


def get_all_judikatur() -> List[models.Document]:
    with Session(engine) as session:
        q = select(models.Document).where(models.Document.applikation != "BrKons").group_by(models.Document.gericht)
        result = session.scalars(q).all()
        return result


def get_all_applikations() -> List[models.Document]:
    with Session(engine) as session:
        q = select(models.Document).group_by(models.Document.applikation)
        result = session.scalars(q).all()
        return result


def get_all_annotion_labels(version:int) -> List[models.Annotation]:
    with Session(engine) as session:
        q = select(models.Annotation).where(models.Annotation.version == version).group_by(models.Annotation.label)
        result = session.scalars(q).all()
        return result


def get_annotated_documents(version:int) -> List[models.Document]:
    with Session(engine) as session:
        q = select(models.Document).where(models.Document.paragraphs.any(models.Paragraph.annotations.any(models.Annotation.version == version)))
        result = session.scalars(q).all()
        return result


def update_para_text(tech_id:str, paragraph_index:int, new_text:str):
    with Session(engine) as session:
        q = select(models.Document).where(models.Document.tech_id == tech_id)
        db_document = session.scalars(q).one()
        db_document.paragraphs[paragraph_index].text = new_text
        session.commit()


print(get_all_annotion_labels(0))

r = get_all_applikations()
for d in r:
    print(f"{d.applikation = }")

r = get_all_judikatur()

for d in r:
    print(f"{d.gericht = }")


      