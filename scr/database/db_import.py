import logging
from pathlib import Path
import re
import requests
from typing import List
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup as bs

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, InvalidRequestError, OperationalError, ProgrammingError

import models


NAMESPACE = {"ogd": "http://ris.bka.gv.at/ogd/V2_6"}


def _init_logging() -> None:
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


def _html_splitter_judikatur(html_decision:str) -> List[str]:
        soup = bs(html_decision, "html.parser")

        # find the decision body: 
        # <body><div><div><h1>Begründung</h1><p>...</p><p>...</p>...
        paragraph_text_list = []
        for div in soup.body.div.find_all("div"): 
            # check if h1 tag exists and if it contains "Begründung"
            if div.h1 and (("Begründung" in div.h1.text)
                        or ("Text" in div.h1.text)
                        or ("Rechtliche Beurteilung" in div.h1.text)): 
                for para in div.find_all("p"):  
                    # remove tags that are not meant for written text 
                    for sr in para.find_all("span", class_="sr-only"): 
                        sr.decompose()
                    paragraph_text_list.append(para.text)

        return paragraph_text_list


def _html_splitter_bundesrecht(html_bundesrecht:str) -> List[str]:
    soup = bs(html_bundesrecht, "html.parser")

    paragraph_text_list = []
    for div in soup.body.find_all("div"):
        if div.h1 and ("Text" in div.h1.text):  
            for para in div.find_all(["p", "ol", "ul"]):  
                # remove tags that are not meant for written text 
                for sr in para.find_all("span", class_="sr-only"): 
                    sr.decompose()
                paragraph_text_list.append(para.text)

    return paragraph_text_list


def _augment_text(text:str) -> str: 
    return re.sub(r"\xa0+", " ", text)


def populate_from_html(session: Session) -> None:
    # select statement for all rows in documents that are not referenced by any paragraph
    stmt = select(models.Document).where(models.Document.paragraphs == None)
    documents = session.scalars(stmt)
   
    timeout_counter = 0

    for document in documents: 
        # TODO move loading of html to separate function; Not trivial because timeouts continue the loop
        try: 
            logging.info(f"Requesting {document.ris_link = }")
            html = requests.get(document.ris_link, timeout=10).text
        except requests.exceptions.Timeout:
            timeout_counter += 1
            if timeout_counter > 5: 
                logging.info(f"Timeout counter exceeded, stopping")
                break
            continue
        except requests.exceptions.RequestException as e: 
            logging.info(f"Error {e} while requesting {document.ris_link = }")
            continue

        logging.info(f"Splitting html of {document.ris_link = }")

        match document.applikation: 
            case "Justiz": new_paragraphs = _html_splitter_judikatur(html)
            case "Vwgh": new_paragraphs = _html_splitter_judikatur(html)
            case "Vfgh": new_paragraphs = _html_splitter_judikatur(html)
            case "BrKons": new_paragraphs = _html_splitter_bundesrecht(html)

        new_paragraphs = [_augment_text(para) for para in new_paragraphs]

        for para_index, new_paragraph in enumerate(new_paragraphs): 
            new_db_paragraph = models.Paragraph(text=new_paragraph, document=document, index=para_index)
            session.add(new_db_paragraph)
            logging.info(f"Added paragraph {para_index} to document {document.id}")
        try: 
            session.commit()
        except (IntegrityError, InvalidRequestError, OperationalError, ProgrammingError) as e: 
            session.rollback()
            session.expunge_all()
            logging.info(f"Paragraphs of {document.tech_id = } not added to database")





if __name__ == "__main__":
    _init_logging()
    engine = create_engine("sqlite:///:memory:", echo=False)
    models.Base.metadata.create_all(engine)
    xml_file = Path.cwd() / r"data\judikatur\justiz\justiz_meta_collection_all_2023.xml"


    with Session(engine) as session:
        populate_from_xml_collection(xml_file, session)
        # populate_from_html(session)
        pass


   


