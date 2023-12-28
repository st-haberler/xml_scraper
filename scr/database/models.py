from typing import List

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import create_engine, ForeignKey


class Base(DeclarativeBase):
    pass
  

class Document(Base): 
    __tablename__ = "documents"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tech_id: Mapped[str] = mapped_column(unique=True)
    applikation: Mapped[str]
    gericht: Mapped[str] = mapped_column(nullable=True)
    geschaeftszahl: Mapped[str] = mapped_column(nullable=True)
    entscheidungsdatum: Mapped[str] = mapped_column(nullable=True)
    kurztitel: Mapped[str] = mapped_column(nullable=True)
    langtitel: Mapped[str] = mapped_column(nullable=True)
    gesetzesnummer: Mapped[int] = mapped_column(nullable=True)
    artikelnummer: Mapped[int] = mapped_column(nullable=True)
    paragraphennummer: Mapped[int] = mapped_column(nullable=True)
    ris_link: Mapped[str] 

    paragraphs: Mapped[List["Paragraph"]] = relationship(back_populates="document")
   


class Paragraph(Base): 
    __tablename__ = "paragraphs"

    id: Mapped[int] = mapped_column("id", primary_key=True)
    index: Mapped[int]
    text: Mapped[str]
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))

    document: Mapped["Document"] = relationship(back_populates="paragraphs")
    annotations: Mapped[List["Annotation"]] = relationship(back_populates="paragraph")


class Annotation(Base):
    __tablename__ = "annotations"
    id: Mapped[int] = mapped_column(primary_key=True)
    begin: Mapped[int]
    end: Mapped[int]
    label: Mapped[str]
    version: Mapped[int]
    paragraph_id: Mapped[int] = mapped_column(ForeignKey("paragraphs.id"))

    paragraph: Mapped["Paragraph"] = relationship(back_populates="annotations") 
    

if __name__ == "__main__":
    engine = create_engine("sqlite:///test.db", echo=False)
    Base.metadata.create_all(engine)