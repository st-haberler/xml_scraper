from pathlib import Path
import pytest

import doc_handler
import doc_db


@pytest.fixture
def collection_fixture():
    p = Path.cwd() / "tests" / "test_tagger" / "test_data"
    p_br = p 
    p_j = p 
    db_path = doc_db.DBPath(p, p_br, p_j)
    collection = doc_db.DBCollection(db_path)

    return collection

@pytest.fixture
def query_fixture():
    query = doc_db.DBQuery(
        source_type="PHG",
        index=0
        )
    return query

class TestDocHandler:

    def test_get_token_frame(self, collection_fixture, query_fixture):
        sut_collection = collection_fixture
        sut = doc_handler.DocumentHandler(sut_collection)

        actual_token_frame = sut.get_token_frame(query_fixture)

        assert actual_token_frame.meta_data.source_type == "PHG"
        assert actual_token_frame.meta_data.index == 0
        assert actual_token_frame.meta_data.year == None

        assert len(actual_token_frame.body) == 5
        assert actual_token_frame.body[0].tokenized_text == ["Haftung"]
        assert actual_token_frame.body[0].annotations == []

    def test_save_tf_to_db

