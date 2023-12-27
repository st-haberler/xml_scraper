from sqlalchemy import create_engine

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

# create a table with three columns, id, tech_id and source_type using the orm syntax
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column

Base = declarative_base()

class Document(Base):
    __tablename__ = "document"
    
    doc_id: Mapped[int] = mapped_column(primary_key=True)
    source_type = mapped_column
    tech_id = Column(String, nullable=False)
    
    paragraphs = relationship("Paragraph", back_populates="document")
    
    def __repr__(self):
        return f"Document(doc_id={self.doc_id}, source_type={self.source_type}, tech_id={self.tech_id})"
    

class Paragraph(Base):
    __tablename__ = "paragraph"
    
    para_id: Mapped[int] = mapped_column(primary_key=True)
    text = Column(Text, nullable=False)
    doc_id = Column(Integer, ForeignKey("document.doc_id"))
    
    document = relationship("Document", back_populates="paragraphs")
    annotations = relationship("Annotation", back_populates="paragraph")
    
    def __repr__(self):
        return f"Paragraph(para_id={self.para_id}, doc_id={self.doc_id}, text={self.text})"

class Annotation(Base):
    __tablename__ = "annotation"
    
    annotation_id: Mapped[int] = mapped_column(primary_key=True)
    para_id = Column(Integer, ForeignKey("paragraph.para_id"))
    begin_token = Column(Integer, nullable=False)
    end_token = Column(Integer, nullable=False)
    label = Column(String, nullable=False)
    version = Column(Integer, nullable=False)
    
    paragraph = relationship("Paragraph", back_populates="annotations")
    
    def __repr__(self):
        return f"Annotation(annotation_id={self.annotation_id}, para_id={self.para_id}, begin_token={self.begin_token}, end_token={self.end_token}, label={self.label}, version={self.version})"