import pytest
from unittest.mock import patch

import flask_server


@pytest.fixture
def query_dict():
    return {
        "source_type": "PHG",
        "index": 0,
        "year": None,
        "annotation_version": 0,
        "doc_id": None
    }

class TestFlaskServer:
    @pytest.mark.skip(reason="Not implemented yet")
    @patch("flask_server.doc_handler.DocumentHandler.get_token_frame_as_json")
    @patch("flask_server.request")
    def test_get_token_frame(self, mock_request, mock_get_tf, query_dict):
        mock_request.get_json.return_value = query_dict
        mock_get_tf.return_value = "test"

        sut_retval = flask_server.get_token_frame()

        

    def test_submit(self):
        pass



