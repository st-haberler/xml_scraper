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


@pytest.fixture
def token_frame_fixture():
    token_frame = doc_handler.TokenFrame(
        meta_data=doc_db.DBQuery(
            source_type="PHG",
            index=0, 
            doc_id = "NOR12034518"
        ),
        body=[
            doc_handler.AnnotatedTokenParagraph(
                tokenized_text=["Haftung"],
                annotations=[doc_db.Annotation(start=0, end=1, label="TEST", version=0)]
            ),
            doc_handler.AnnotatedTokenParagraph(
                tokenized_text=["XXX"],
                annotations=[]
            ),
            doc_handler.AnnotatedTokenParagraph(
                tokenized_text=["XXX"],
                annotations=[]
            ),
            doc_handler.AnnotatedTokenParagraph(
                tokenized_text=["XXX"],
                annotations=[]
            ),
            doc_handler.AnnotatedTokenParagraph(
                tokenized_text=["XXX"],
                annotations=[]
            )
        ]
    )
    return token_frame

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

    # pytest.mark.skip(reason="not ready yet")
    def test_save_tf_to_db(self, collection_fixture, query_fixture, token_frame_fixture): 
        temp_file = Path.cwd() / "tests/test_tagger/test_data/PHG/json/NOR12034518.json"
        temp_data = temp_file.read_text(encoding="utf-8")
        
        sut = doc_handler.DocumentHandler(collection_fixture)

        try: 
            sut.save_token_frame_to_db(token_frame_fixture)
            
            actual_db_data = sut.database.get_entry_from_query(query_fixture)
            assert actual_db_data.document_body[0].annotations[0].start == 0
            assert actual_db_data.document_body[0].annotations[0].end == 1
            assert actual_db_data.document_body[0].annotations[0].label == "TEST"
            assert actual_db_data.document_body[0].annotations[0].version == 0

        finally:
            temp_file.write_text(temp_data, encoding="utf-8")



