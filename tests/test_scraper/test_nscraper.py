import argparse
import datetime

import pytest
from unittest.mock import Mock
from unittest.mock import patch 

from xml.etree import ElementTree as ET

import nscraper 

## First test: MetaLoader.load_meta_data()

def test_meta_loader(): 
    test_loader = nscraper.MetaLoader("vfgh", 2021)
    
    mock_download = ET.Element("meta_data")
    test_loader.generate_xml_request = Mock(return_value="xml_request")
    test_loader.send_xml_request = Mock(return_value="response")
    
    test_loader.extract_meta_data = Mock(return_value=mock_download)

  

