from dataclasses import dataclass, asdict
import logging
from typing import List

import spacy
from sqlalchemy import create_engine, select, and_, Select
from sqlalchemy.orm import Session 
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

import scr.database.models as models 
# import models


DATABASE = "sqlite:///test.db"

engine = create_engine(DATABASE, echo=False)


@dataclass
class Annotation:
    begin: int
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



    # standard entry points for creating a TokenFrame
    @classmethod
    def create_token_frame(cls, sql_stmt, doc_paragraph_id:int) -> "TokenFrame":
        with Session(engine) as session: 
            try: 
                db_document = session.scalars(sql_stmt).one()
            except NoResultFound:
                raise ValueError(f"Document not found in database")
            except MultipleResultsFound:
                raise ValueError(f"Multiple documents found in database")
            if doc_paragraph_id >= len(db_document.paragraphs): 
                raise ValueError(f"Document has no paragraph with id {doc_paragraph_id}")

            nlp = spacy.load("de_core_news_sm")
            spacy_document = nlp(db_document.paragraphs[doc_paragraph_id].text)
            tokenized_text = [token.text_with_ws for token in spacy_document]

            annotations = [annotation.as_dict() for annotation in db_document.paragraphs[doc_paragraph_id].annotations]

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
                paragraphennummer=db_document.paragraphnummer,
                tokenized_text=tokenized_text,
                annotations= annotations
            )
            

    @classmethod
    def create_token_frame_from_gz(cls, gz:str, doc_paragraph_id:int) -> "TokenFrame": 
        with Session(engine) as session:
            query_stmt = select(models.Document).where(models.Document.geschaeftszahl == gz)
            return cls.create_token_frame(query_stmt, doc_paragraph_id)
        
    
    @classmethod
    def create_token_frame_from_gesetzesnummer(cls, gesetzesnummer:int, paragraphennummer:int, artikelnummer:int, doc_paragraph_id:int) -> "TokenFrame": 
        with Session(engine) as session:
            query_stmt = select(models.Document).where(and_((models.Document.gesetzesnummer == gesetzesnummer), 
                                                            (models.Document.paragraphnummer == paragraphennummer), 
                                                            (models.Document.artikelnummer == artikelnummer)))
            return cls.create_token_frame(query_stmt, doc_paragraph_id)


    @classmethod
    def create_token_frame_from_request(cls, request:dict) -> "TokenFrame":
        if (request.get("geschaeftszahl") and 
            (request.get("doc_paragraph_id") is not None)):
            return cls.create_token_frame_from_gz(
                gz=request.get("geschaeftszahl"),
                doc_paragraph_id=request.get("doc_paragraph_id"))
        if (request.get("gesetzesnummer") and 
            (request.get("doc_paragraph_id") is not None) and
            ((request.get("paragraphennummer") is not None) or 
             ((request.get("artikelnummer")) is not None))):          
            return cls.create_token_frame_from_gesetzesnummer(gesetzesnummer=request.get("gesetzesnummer"),
                                                               paragraphennummer=request.get("paragraphennummer", None),
                                                               artikelnummer=request.get("artikelnummer", None),
                                                               doc_paragraph_id=request.get("doc_paragraph_id"))
        else:
            raise ValueError("Request does not contain the required fields")


if __name__ == "__main__":
    t = TokenFrame.create_token_frame_from_gesetzesnummer(gesetzesnummer=10002864, 
                                                          paragraphennummer=5, 
                                                          artikelnummer=None, 
                                                          doc_paragraph_id=0)
    print(t.kurztitel)

    print(t.tokenized_text)
    print(t.annotations)

    t = TokenFrame.create_token_frame_from_gz(gz="V153/2021 (V153/2021-13)", doc_paragraph_id=3)
    print(t.gericht)
    print(t.tokenized_text)
    print(t.annotations)
    