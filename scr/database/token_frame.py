from dataclasses import dataclass
from typing import List

import spacy
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session 
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

import models


DATABASE = "sqlite:///test.db"

engine = create_engine(DATABASE, echo=False)


@dataclass
class Annotation:
    start: int
    end: int
    label: str
    version: int


@dataclass
class TokenFrame: 
    tech_id: str
    doc_paragraph_id: int
    applikation: str
    gericht: str
    geschaeftszahl: str
    entscheidungsdatum: str
    kurztitel: str
    langtitel: str
    gesetzesnummer: int
    artikelnummer: int
    paragraphennummer: int

    tokenized_text: List[str]
    annotations: List[Annotation]


    # standard entry point for creating a TokenFrame
    @classmethod
    def create_token_frame(cls, tech_id:str, doc_paragraph_id:int) -> "TokenFrame":
        with Session(engine) as session: 
            query_stmt = select(models.Document).where(models.Document.tech_id == tech_id)
            try: 
                db_document = session.scalars(query_stmt).one()
            except NoResultFound:
                raise ValueError(f"Document with tech_id {tech_id} not found in database")
            except MultipleResultsFound:
                raise ValueError(f"Multiple documents with tech_id {tech_id} found in database")
            if doc_paragraph_id >= len(db_document.paragraphs): 
                raise ValueError(f"Document with tech_id {tech_id} has no paragraph with id {doc_paragraph_id}")
            
            print(len(db_document.paragraphs))
            print(db_document.kurztitel, "§ ", db_document.paragraphennummer)
            print(db_document.paragraphs[doc_paragraph_id].text)

if __name__ == "__main__":
    TokenFrame.create_token_frame("NOR12034529", 0)