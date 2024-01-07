import sqlite3
from pathlib import Path
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

import models
import db_import 


@pytest.fixture
def sqlalchemy_engine():
    engine = models.create_engine("sqlite:///:memory:", echo=False)
    models.Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def sqlalchemy_session(sqlalchemy_engine, request):
    session = Session(sqlalchemy_engine)

    def teardown():
        session.close()
        models.Base.metadata.drop_all(sqlalchemy_engine)    
    
    request.addfinalizer(teardown)

    return session


def test_model(sqlalchemy_session):  
    assert "documents" in models.Base.metadata.tables.keys()
    assert "paragraphs" in models.Base.metadata.tables.keys()
    assert "annotations" in models.Base.metadata.tables.keys()


def test_bundesrecht_datastructure(sqlalchemy_session): 
    db_import.populate_from_xml_collection(Path("tests/test_database/data/test_bundesrecht_collection.xml"), sqlalchemy_session)
    # attention: this one loads data from online RIS 
    db_import.populate_from_html(sqlalchemy_session)
    ann_1 = models.Annotation(label="TEST_1", begin=0, end=1, version=0, paragraph_id=3)
    ann_2 = models.Annotation(label="TEST_2", begin=3, end=4, version=0, paragraph_id=4)
    sqlalchemy_session.add(ann_1)
    sqlalchemy_session.add(ann_2)
    sqlalchemy_session.commit()

    q1 = select(models.Document)
    actual_result_1 = sqlalchemy_session.scalars(q1).all()

    assert len(actual_result_1) == 36
    for doc in actual_result_1:
        assert doc.applikation == "BrKons"
        assert doc.gericht == None
        assert doc.gesetzesnummer == 10002864

    q2 = select(models.Document).where(models.Document.paragraphs.any(models.Paragraph.id == 3))
    actual_result_2 = sqlalchemy_session.scalars(q2).one()
    assert actual_result_2.paragraphnummer == 1



    q3 = select(models.Paragraph).where(models.Paragraph.id == 3)
    actual_result_3 = sqlalchemy_session.scalars(q3).one()
    assert actual_result_3.text.startswith("§ 1. (1) Wird durch den Fehler eines Produkts ein Mensch getötet")
    assert len(actual_result_3.annotations) == 1
    assert actual_result_3.annotations[0].label == "TEST_1"

    q4 = select(models.Paragraph).where(models.Paragraph.id == 4)
    actual_result_4 = sqlalchemy_session.scalars(q4).one()  
    assert actual_result_4.text.startswith("1.der Unternehmer, der es hergestellt und ")
    assert actual_result_4.annotations[0].label == "TEST_2"

    
def test_vfgh_datastructure(sqlalchemy_session): 
    pre_result = sqlalchemy_session.scalars(select(models.Document)).all()
    assert len(pre_result) == 0

    db_import.populate_from_xml_collection(Path("tests/test_database/data/test_vfgh_collection.xml"), sqlalchemy_session)
     # attention: this one loads data from online RIS 
    db_import.populate_from_html(sqlalchemy_session)
    ann_1 = models.Annotation(label="TEST_1", begin=0, end=1, version=0, paragraph_id=3)
    ann_2 = models.Annotation(label="TEST_2", begin=3, end=4, version=0, paragraph_id=4)
    sqlalchemy_session.add(ann_1)
    sqlalchemy_session.add(ann_2)
    sqlalchemy_session.commit()

    q1 = select(models.Document)
    actual_result_1 = sqlalchemy_session.scalars(q1).all()
    
    for decision in actual_result_1:
        assert decision.applikation == "Vfgh"
        assert "VfGH" in decision.gericht
        assert decision.gesetzesnummer == None

    q2 = select(models.Document).where(models.Document.paragraphs.any(models.Paragraph.id == 3))
    actual_result_2 = sqlalchemy_session.scalars(q2).one()
    assert actual_result_2.geschaeftszahl == "E4603/2021"

    q3 = select(models.Paragraph).where(models.Paragraph.id == 3)
    actual_result_3 = sqlalchemy_session.scalars(q3).one()
    # assert actual_result_3.text.startswith("§ 1. (1) Wird durch den Fehler eines Produkts ein Mensch getötet")
    assert len(actual_result_3.annotations) == 1
    assert actual_result_3.annotations[0].label == "TEST_1"

    q4 = select(models.Paragraph).where(models.Paragraph.id == 4)
    actual_result_4 = sqlalchemy_session.scalars(q4).one()  
    # assert actual_result_4.text.startswith("1.der Unternehmer, der es hergestellt und ")
    assert actual_result_4.annotations[0].label == "TEST_2"    
