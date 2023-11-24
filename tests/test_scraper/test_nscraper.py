import argparse
import datetime

import pytest
from unittest.mock import Mock
from unittest.mock import patch 

import xml.etree.ElementTree as ET

import nscraper 


def test_meta_loader(): 
    expected = ET.Element("meta_data")
    
    expected.append(ET.fromstring("<test>CCC</test>"))
    
    test_loader = nscraper.MetaLoader("vfgh", 2021)
    test_loader.get_xml_request = Mock(return_value="")
    test_loader.send_xml_request = Mock(return_value="")
    test_loader.extract_meta_data = Mock(return_value="<test>CCC</test>")

    result = test_loader.load_meta_data()

    assert ET.tostring(result[0]) == ET.tostring(expected[0])
    
