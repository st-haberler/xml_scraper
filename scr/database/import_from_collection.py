import logging
from pathlib import Path
import xml.etree.ElementTree as ET

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError	

import models


NAMESPACE = {"ogd": "http://ris.bka.gv.at/ogd/V2_6"}


def init_logging() -> None:
    logging.basicConfig(level=logging.INFO)


def populate_from_xml_collection(xml_file:Path, session: Session) -> None:
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    missed_entries = 0
    counter = 0
    for document in root: 
        if "OgdDocumentReference" not in document.tag: 
            missed_entries += 1
            logging.info(f"Skipping entry with tag {document.tag}")
            continue

        try: 
            tech_id = document.find(".//ogd:ID", namespaces=NAMESPACE).text
            applikation = document.find(".//ogd:Applikation", namespaces=NAMESPACE).text
        except AttributeError:
            missed_entries += 1
            logging.info(f"Skipping entry with tag {document.tag}")
            continue
            
        gericht_tag = document.find(".//ogd:Justiz/ogd:Gericht", namespaces=NAMESPACE)
        if gericht_tag is None:
            gericht = None
        else:  
            gericht = gericht_tag.text

        geschaeftszahl_tag = document.find(".//ogd:Judikatur/ogd:Geschaeftszahl", namespaces=NAMESPACE)
        if geschaeftszahl_tag is None: 
            geschaeftszahl = None
        else:
            if len(geschaeftszahl_tag) == 1: 
                geschaeftszahl = geschaeftszahl_tag[0].text
            if len(geschaeftszahl_tag) > 1:
                geschaeftszahl = "; ".join([item.text for item in geschaeftszahl_tag])
        
        entscheidungsdatum_tag = document.find(".//ogd:Judikatur/ogd:Entscheidungsdatum", namespaces=NAMESPACE)
        if entscheidungsdatum_tag is None:
            entscheidungsdatum = None
        else: 
            entscheidungsdatum = entscheidungsdatum_tag.text
        
        kurztitel_tag = document.find(".//ogd:Bundesrecht/ogd:Kurztitel", namespaces=NAMESPACE)
        if kurztitel_tag is None: 
            kurztitel = None
        else:
            kurztitel = kurztitel_tag.text
        
        langtitel_tag = document.find(".//ogd:Bundesrecht/ogd:Titel", namespaces=NAMESPACE)
        if langtitel_tag is None:
            langtitel = None
        else: 
            langtitel = langtitel_tag.text
        
        gesetzesnummer_tag = document.find(".//ogd:BrKons/ogd:Gesetzesnummer", namespaces=NAMESPACE)
        if gesetzesnummer_tag is None: 
            gesetzesnummer = None
        else:
            try: 
                gesetzesnummer = int(gesetzesnummer_tag.text)
            except ValueError: 
                gesetzesnummer = None
                logging.info(f"[{kurztitel}] Could not convert Gesetzesnummer '{gesetzesnummer_tag.text}' to int")
        
        artikelnummer_tag = document.find(".//ogd:BrKons/ogd:Artikelnummer", namespaces=NAMESPACE)
        if artikelnummer_tag is None:
            artikelnummer = None
        else: 
            try: 
                artikelnummer = int(artikelnummer_tag.text)
            except ValueError: 
                artikelnummer = None
                logging.info(f"[{kurztitel}] Could not convert Artikelnummer '{artikelnummer_tag.text}' to int")
        
        paragraphennummer_tag = document.find(".//ogd:BrKons/ogd:Paragraphennummer", namespaces=NAMESPACE)
        if paragraphennummer_tag is None: 
            paragraphennummer = None
        else:
            try: 
                paragraphennummer = int(paragraphennummer_tag.text)
            except ValueError: 
                paragraphennummer = None
                logging.info(f"[{kurztitel}] Could not convert Paragraphennummer '{paragraphennummer_tag.text}' to int")
        
        urls_tag = document.find(".//ogd:ContentReference/ogd:Urls", namespaces=NAMESPACE)
        if urls_tag is None:
            logging.info(f"{kurztitel} / {artikelnummer}{paragraphennummer}: No urls found")
            continue
        else:
            for content_url_tag in urls_tag: 
                if (content_url_tag.find(".//ogd:DataType", namespaces=NAMESPACE) is not None) and (content_url_tag.find(".//ogd:DataType", namespaces=NAMESPACE).text == "Html"): 
                    ris_link = content_url_tag.find(".//ogd:Url", namespaces=NAMESPACE).text
                    break
            if ris_link is None: 
                logging.info(f"{kurztitel} / {artikelnummer}{paragraphennummer}: No html url found")
                continue

        new_document = models.Document(
            tech_id=tech_id,
            applikation=applikation,
            gericht=gericht,
            geschaeftszahl=geschaeftszahl,
            entscheidungsdatum=entscheidungsdatum,
            kurztitel=kurztitel,
            langtitel=langtitel,
            gesetzesnummer=gesetzesnummer,
            artikelnummer=artikelnummer,
            paragraphennummer=paragraphennummer,
            ris_link=ris_link
        )
        session.add(new_document)
        try: 
            counter += 1
            session.commit()
        except IntegrityError: 
            missed_entries += 1
            session.rollback()
            session.expunge_all()
            logging.info(f"Skipping duplicate entry {tech_id = }")
        else: 
            session.expire(new_document)
            logging.info(f"Added {tech_id = }")
    
    print(f"{missed_entries = }")
    print(f"{len(root) = }")
    print(f"{counter = }")


def populate_from_html(session: Session) -> None:
    stmt = select(models.Document).where(models.Document.paragraphs == None)
    documents = session.scalars(stmt)

    print(len(list(documents)))


if __name__ == "__main__":
    init_logging()
    engine = create_engine("sqlite:///test.db", echo=False)
    xml_file = Path.cwd() / r"data\judikatur\justiz\justiz_meta_collection_all_2023.xml"

    with Session(engine) as session:
        populate_from_html(session)


