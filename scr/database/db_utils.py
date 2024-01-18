import logging
from typing import List, Dict

from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session

import scr.database.model as model



engine = create_engine("sqlite:///test.db", echo=False)
logging.basicConfig(level=logging.INFO)


def get_all_Gesetze() -> List[model.Document]: 
    with Session(engine) as session:
        q = select(model.Document).where(model.Document.applikation == "BrKons").group_by(model.Document.gesetzesnummer)
        result = session.scalars(q).all()
        return result


def get_all_judikatur() -> List[model.Document]:
    with Session(engine) as session:
        q = select(model.Document).where(model.Document.applikation != "BrKons").group_by(model.Document.gericht)
        result = session.scalars(q).all()
        return result


def get_all_applikations() -> List[model.Document]:
    with Session(engine) as session:
        q = select(model.Document).group_by(model.Document.applikation)
        result = session.scalars(q).all()
        return result


def get_all_annotion_labels_asdict(version:int) -> List[Dict[str, str]]:
    # for now, until database has annotation labels: 
    # return ["LABEL1", "LABEL2", "LABEL3"]
    
    with Session(engine) as session:
        q = select(model.Annotation).where(model.Annotation.version == version).group_by(model.Annotation.label)
        result = session.scalars(q).all()
    result_asdict = [label.as_dict() for label in result]
    logging.info(f"from db_utils: {result_asdict = }")

    return result_asdict


def get_annotated_documents(version:int) -> List[model.Document]:
    with Session(engine) as session:
        q = select(model.Document).where(model.Document.paragraphs.any(model.Paragraph.annotations.any(model.Annotation.version == version)))
        result = session.scalars(q).all()
        return result


def update_para_text(tech_id:str, paragraph_index:int, new_text:str):
    with Session(engine) as session:
        q = select(model.Document).where(model.Document.tech_id == tech_id)
        db_document = session.scalars(q).one()
        db_document.paragraphs[paragraph_index].text = new_text
        session.commit()


def get_gesetz_content(gesetzesnummer:int) -> Dict[str, str]:
    with Session(engine) as session:
        q = select(model.Document).where(model.Document.gesetzesnummer == gesetzesnummer)
        db_document = session.scalars(q).all()
        content_overview = []
        for d in db_document:
            content_overview.append({"id": d.id, 
                                     "artikelnummer": d.artikelnummer, 
                                     "artikelbuchstabe": d.artikelbuchstabe, 
                                     "paragraphnummer": d.paragraphnummer, 
                                     "paragraphbuchstabe": d.paragraphbuchstabe, 
                                     "absatz_length": len(d.paragraphs) if d.paragraphs else 0,
                                    })
        return content_overview
    


if __name__ == "__main__":
    r = get_all_Gesetze()
    for g in r: 
        print(g.kurztitel, g.gesetzesnummer)