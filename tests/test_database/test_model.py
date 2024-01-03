import sqlite3
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import models


@pytest.fixture
def sqlalchemy_engine():
    engine = models.create_engine("sqlite:///:memory:", echo=False)
    models.Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def sqlalchemy_session(sqlalchemy_engine, request):
    models.Base.metadata.create_all(sqlalchemy_engine)
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
    
