from pathlib import Path
import pytest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import link_extractor



@pytest.fixture
def get_justiz_links_2023() -> list[ET.Element]:
    link_file = Path.cwd() / "data" / "judikatur" / "justiz" / "justiz_all_decision_links_2023.links"
    with open(link_file, "r") as f:
        links = f.readlines()
    return links

@pytest.fixture
def get_meta_list_2023() -> list[ET.Element]:
    meta_file = Path.cwd() / "data" / "judikatur" / "justiz" / "justiz_meta_collection_all_2023.xml"
    file_content = ET.fromstring(meta_file.read_text())
    doc_reference_elements = file_content.findall(".//{http://ris.bka.gv.at/ogd/V2_6}OgdDocumentReference")
    return doc_reference_elements



def test_is_decision_true(get_meta_list_2023):
    assert link_extractor.LinkExtractor()._is_decision(get_meta_list_2023[0]) == True



def test_extract_links(get_meta_list_2023, get_justiz_links_2023):
    expected = get_justiz_links_2023
    result = link_extractor.LinkExtractor()._extract_links(get_meta_list_2023)
    
    assert len(result) == len(expected)
    for link_expected, link_result in zip(expected, result):
        assert link_expected == link_result
        