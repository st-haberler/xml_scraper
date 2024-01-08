import pytest
import requests




@pytest.fixture
def base_url():
    return "http://127.0.0.1:5000"


def test_get_token_frame_from_gz(base_url):
    actual_response =  requests.get(f"{base_url}/get_token_frame", json={"geschaeftszahl": "E4603/2021", "doc_paragraph_id": 0})

    assert actual_response.status_code == 200
    assert actual_response.json()["tech_id"] == "JFT_20230227_21E04603_00"
    
    
def test_get_token_from_gesetz(base_url): 
    actual_response =  requests.get(f"{base_url}/get_token_frame", json={"gesetzesnummer": 10002864, "paragraphennummer": 5, "doc_paragraph_id": 0})

    assert actual_response.status_code == 200
    assert actual_response.json()["tech_id"] == "NOR12034522"