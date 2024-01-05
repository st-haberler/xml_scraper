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
            
           
            print(db_document.paragraphs[doc_paragraph_id].text)
            print(db_document.paragraphs[doc_paragraph_id].id)
            print(db_document.paragraphs[doc_paragraph_id].index)


            nlp = spacy.load("de_core_news_sm")
            spacy_document = nlp(db_document.paragraphs[doc_paragraph_id].text)
            tokenized_text = [token.text_with_ws for token in spacy_document]

            annotations = db_document.paragraphs[doc_paragraph_id].annotations

            return cls(
                tech_id=db_document.tech_id,
                doc_paragraph_id=doc_paragraph_id,
                applikation=db_document.applikation,
                gericht=db_document.gericht,
                geschaeftszahl=db_document.geschaeftszahl,
                entscheidungsdatum=db_document.entscheidungsdatum,
                kurztitel=db_document.kurztitel,
                langtitel=db_document.langtitel,
                gesetzesnummer=db_document.gesetzesnummer,
                artikelnummer=db_document.artikelnummer,
                paragraphennummer=db_document.paragraphennummer,
                tokenized_text=tokenized_text,
                annotations=annotations
            )
            

            

            
            
if __name__ == "__main__":
    t = TokenFrame.create_token_frame("NOR40045767", 0)
    print(t.langtitel)
    