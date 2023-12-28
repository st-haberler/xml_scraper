from pathlib import Path
from typing import List
import xml.etree.ElementTree as ET

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, relationship
from sqlalchemy import create_engine, select, ForeignKey


NAMESPACE = {'ogd': 'http://ris.bka.gv.at/ogd/V2_6'}


class Base(DeclarativeBase):
    pass


class SourceType(Base):
    __tablename__ = "source_type"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column("name")
    sources: Mapped[List["Document"]] = relationship(back_populates="source_type")
    

class Document(Base): 
    __tablename__ = "document"
    id: Mapped[int] = mapped_column(primary_key=True)
    tech_id: Mapped[str] = mapped_column(unique=True)
    source_type_id: Mapped[int] = mapped_column("source_type_id", ForeignKey("source_type.id"))
    applikation: Mapped[str] = mapped_column(nullable=True)
    gericht: Mapped[str] = mapped_column(nullable=True)
    geschaeftszahl: Mapped[str] = mapped_column(nullable=True)
    entscheidungsdatum: Mapped[str] = mapped_column(nullable=True)
    kurztitel: Mapped[str] = mapped_column(nullable=True)
    langtitel: Mapped[str] = mapped_column(nullable=True)
    gesetzesnummer: Mapped[int] = mapped_column(nullable=True)
    artikelnummer: Mapped[int] = mapped_column(nullable=True)
    paragraphennummer: Mapped[int] = mapped_column(nullable=True)
    ris_link: Mapped[str] 

    source_type: Mapped["SourceType"] = relationship(back_populates="sources")
    paragraphs: Mapped[List["Paragraph"]] = relationship(back_populates="document")
   


class Paragraph(Base): 
    __tablename__ = "paragraph"
    id: Mapped[int] = mapped_column("id", primary_key=True)
    index: Mapped[int]
    text: Mapped[str]
    document_id: Mapped[int] = mapped_column(ForeignKey("document.id"))

    document: Mapped["Document"] = relationship(back_populates="paragraphs")
    annotations: Mapped[List["Annotation"]] = relationship(back_populates="paragraph")


class Annotation(Base):
    __tablename__ = "annotation"
    id: Mapped[int] = mapped_column(primary_key=True)
    begin: Mapped[int]
    end: Mapped[int]
    label: Mapped[str]
    version: Mapped[int]
    paragraph_id: Mapped[int] = mapped_column(ForeignKey("paragraph.id"))

    paragraph: Mapped["Paragraph"] = relationship(back_populates="annotations") 
    


if __name__ == "__main__":
    engine = create_engine("sqlite:///test.db", echo=False)
    Base.metadata.create_all(engine)

    meta_file = Path.cwd() / r"data\judikatur\justiz\justiz_meta_collection_all_2023.xml"
    tree = ET.parse(meta_file)
    root = tree.getroot()
    xml_docs = root.findall(".//ogd:OgdDocumentReference", namespaces=NAMESPACE)
    

    judikatur_source = SourceType(name="judikatur")

    for xml_doc in xml_docs: 
        tech_id = xml_doc.find("ogd:Data/ogd:Metadaten/ogd:Technisch/ogd:ID", namespaces=NAMESPACE).text
        applikation = xml_doc.find("ogd:Data/ogd:Metadaten/ogd:Technisch/ogd:Applikation", namespaces=NAMESPACE).text
        if xml_doc.find("ogd:Data/ogd:Metadaten/ogd:Judikatur/ogd:Justiz/ogd:Gericht", namespaces=NAMESPACE) is not None: 
            gericht = xml_doc.find("ogd:Data/ogd:Metadaten/ogd:Judikatur/ogd:Justiz/ogd:Gericht", namespaces=NAMESPACE).text
        else: 
            print(f"No gericht found: {tech_id = }\n{applikation = }")
        geschaeftszahl = xml_doc.find("ogd:Data/ogd:Metadaten/ogd:Judikatur/ogd:Geschaeftszahl/ogd:item", namespaces=NAMESPACE).text
        entscheidungsdatum = xml_doc.find("ogd:Data/ogd:Metadaten/ogd:Judikatur/ogd:Entscheidungsdatum", namespaces=NAMESPACE).text
        kurztitel = None
        langtitel = None
        gesetzesnummer = None
        artikelnummer = None
        paragraphennummer = None
        # print(f"{tech_id = }\n{applikation = }\n{gericht = }\n{geschaeftszahl = }\n{entscheidungsdatum = }\n{kurztitel = }\n{langtitel = }\n{gesetzesnummer = }\n{artikelnummer = }\n{paragraphennummer = }\n")
        # break
        new_document = Document(
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
            source_type=judikatur_source
        )
        with Session(engine) as session: 
            session.add(new_document)
            session.commit()
            session.expire(new_document)
            # print(new_document.id)
            # break
       

