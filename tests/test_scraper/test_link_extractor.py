from pathlib import Path
import pytest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import link_extractor


class TestLinkExtractor:

    def __get_expected_links(self): 
        link_file = Path("./tests/test_scraper/test_data/test_links_vfgh_2022.links")
        return link_file.read_text(encoding="utf-8").split("\n")


    def test_extract_links(self): 
        source = Path("./tests/test_scraper/test_data/test_vfgh_2022_meta.xml")
        sut = link_extractor.LinkExtractor()
        actual_result = sut.get_links(source, todisk=False)
        expected_result = self.__get_expected_links()

        for actual, expected in zip(actual_result, expected_result):
            assert actual == expected
       
        