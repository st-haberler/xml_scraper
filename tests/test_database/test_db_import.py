from pathlib import Path
import pytest
import db_import 

JUSTIZ_DECISIONS_2023 = 3967
VFGH_DECISIONS_2023 = 391
PHG_DOCS = 36


@pytest.fixture
def justiz_xml_collection_file():
    return Path.cwd() / "tests/test_database/data/test_justiz_collection.xml"


@pytest.fixture
def vfgh_xml_collection_file():
    return Path.cwd() / "tests/test_database/data/test_vfgh_collection.xml"


@pytest.fixture
def bundesrecht_collection_file():
    return Path.cwd() / "tests/test_database/data/test_bundesrecht_collection.xml"


@pytest.fixture
def sqlalchemy_engine():
    engine = db_import.create_engine("sqlite:///:memory:", echo=False)
    db_import.models.Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def sqlalchemy_session(sqlalchemy_engine, request):
    db_import.models.Base.metadata.create_all(sqlalchemy_engine)
    session = db_import.Session(sqlalchemy_engine)

    def teardown():
        session.close()
        db_import.models.Base.metadata.drop_all(sqlalchemy_engine)    
    
    request.addfinalizer(teardown)

    return session


class Test_db_import: 
    
    def test_from_justiz_xml_collection(self, justiz_xml_collection_file, sqlalchemy_session):
        db_import.populate_from_xml_collection(justiz_xml_collection_file, sqlalchemy_session)

        acctual_stmt = db_import.select(db_import.models.Document)
        actual_result = list(sqlalchemy_session.scalars(acctual_stmt))

        assert "JJT_20230131_OGH0002_0040OB00003_23D0000_000" in [doc.tech_id for doc in actual_result]
        assert "JJT_20230131_OGH0002_0040OB00005_23Y0000_000" in [doc.tech_id for doc in actual_result]
        assert "JWR_2022150004_20220209J01" in [doc.tech_id for doc in actual_result]
        assert "JJT_20231003_OGH0002_0120NS00056_23S0000_000" in [doc.tech_id for doc in actual_result]
        assert len(actual_result) == JUSTIZ_DECISIONS_2023

        # TODO: add more assertions to make sure that all documents are added correctly


    def test_for_unique_constraint(self, justiz_xml_collection_file, sqlalchemy_session):
        db_import.populate_from_xml_collection(justiz_xml_collection_file, sqlalchemy_session)
        db_import.populate_from_xml_collection(justiz_xml_collection_file, sqlalchemy_session)
        
        acctual_stmt = db_import.select(db_import.models.Document)
        actual_result = list(sqlalchemy_session.scalars(acctual_stmt))

        assert len(actual_result) == JUSTIZ_DECISIONS_2023


    def test_from_vfgh_xml_collection(self, vfgh_xml_collection_file, sqlalchemy_session):
        db_import.populate_from_xml_collection(vfgh_xml_collection_file, sqlalchemy_session)

        acctual_stmt = db_import.select(db_import.models.Document)
        actual_result = list(sqlalchemy_session.scalars(acctual_stmt))

        assert "JFT_20230227_21E04603_00" in [doc.tech_id for doc in actual_result]
        assert "JFT_20230227_21V00153_00" in [doc.tech_id for doc in actual_result]
        assert "JFT_20230612_23G00098_00" in [doc.tech_id for doc in actual_result]
        assert len(actual_result) == VFGH_DECISIONS_2023

    
    def test_from_bundesrecht_collection(self, bundesrecht_collection_file, sqlalchemy_session):
        db_import.populate_from_xml_collection(bundesrecht_collection_file, sqlalchemy_session)

        acctual_stmt = db_import.select(db_import.models.Document)
        actual_result = list(sqlalchemy_session.scalars(acctual_stmt))

        assert "NOR11002887" in [doc.tech_id for doc in actual_result]
        assert "NOR12034518" in [doc.tech_id for doc in actual_result]
        assert "NOR12036591" in [doc.tech_id for doc in actual_result]
        assert len(actual_result) == PHG_DOCS
