import logging
from typing import List, Dict

from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session

import scr.database.models as models



engine = create_engine("sqlite:///test.db", echo=False)
logging.basicConfig(level=logging.INFO)


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


def get_all_annotion_labels_asdict(version:int) -> List[Dict[str, str]]:
    # for now, until database has annotation labels: 
    # return ["LABEL1", "LABEL2", "LABEL3"]
    
    with Session(engine) as session:
        q = select(models.Annotation).where(models.Annotation.version == version).group_by(models.Annotation.label)
        result = session.scalars(q).all()
    result_asdict = [label.as_dict() for label in result]
    logging.info(f"from db_utils: {result_asdict = }")

    return result_asdict


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


if __name__ == "__main__":
    r = get_all_Gesetze()
    for g in r: 
        print(g.kurztitel, g.gesetzesnummer)