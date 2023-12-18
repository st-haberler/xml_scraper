from pathlib import Path
import pytest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import link_extractor


class TestLinkExtractor:

    def __get_expected_decision_links(self): 
        link_file = Path("./tests/test_scraper/test_data/test_links_vfgh_2022.links")
        return link_file.read_text(encoding="utf-8").split("\n")


    def __get_expected_bundesrecht_links(self):
        link_file = Path("./tests/test_scraper/test_data/test_PHG.links")
        return link_file.read_text(encoding="utf-8").split("\n")


    def test_extract_decision_links(self): 
        meta_collection_source = Path("./tests/test_scraper/test_data/test_vfgh_2022_meta.xml")
        sut = link_extractor.LinkExtractor()
        
        actual_result = sut.get_decision_links(year="2022", source_type="vfgh", meta_collection=meta_collection_source, todisk=False)
        
        expected_result = self.__get_expected_decision_links()

        for actual, expected in zip(actual_result, expected_result):
            assert actual == expected

    
    def test_extract_bundesrecht_links(self):
        meta_collection_source = Path("./tests/test_scraper/test_data/test_PHG_meta_collection.xml")
        sut = link_extractor.LinkExtractor()
        
        actual_result = sut.get_bundesrecht_links(source_type="PHG", meta_collection=meta_collection_source, todisk=False)
        
        expected_result = self.__get_expected_bundesrecht_links()

        for actual, expected in zip(actual_result, expected_result):
            assert actual == expected

       
        