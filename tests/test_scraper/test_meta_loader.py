"""test suite for meta_loader.py
sut = system under test
"""
from pathlib import Path
from unittest.mock import patch, MagicMock
from xml.etree import ElementTree as ET


import meta_loader 


def __get_test_xml_response() -> str:
	"""Returns test XML request."""

	test_response_file = Path(r"./test_request.xml")
	test_response = test_response_file.read_text(encoding="utf-8")

	return test_response


def __get_test_xml_list_1() -> list[str]:
	"""Returns test XML list."""
	test_response_file = Path(r"./test_response_1.xml")
	test_response = test_response_file.read_text(encoding="utf-8")

	test_xml = ET.fromstring(test_response)
	test_xml_list = test_xml.findall(".//{http://ris.bka.gv.at/ogd/V2_6}OgdDocumentReference")
	
	return test_xml_list

def __get_test_xml_list_2() -> list[str]:
	"""Returns test XML list."""
	test_response_file = Path(r"./test_response_2.xml")
	test_response = test_response_file.read_text(encoding="utf-8")

	test_xml = ET.fromstring(test_response)
	test_xml_list = test_xml.findall(".//{http://ris.bka.gv.at/ogd/V2_6}OgdDocumentReference")
	
	return test_xml_list



class TestMetaLoader: 
    
	@patch("meta_loader.XML_Request")
	def test_load_meta_data(self, mock_request_class):
		"""sut is only function load_meta_data(). Special test xml data is returned by 
		mock_request_class.send_xml_request(). The data has 101 hits."""
		
		mock_xml_request = MagicMock()
		mock_xml_request.send_xml_request.return_value = __get_test_xml_response()
		mock_request_class.return_value = mock_xml_request
		
		sut = meta_loader.MetaLoader("vfgh", 1951)
		expected_result = __get_test_xml_list()

		actual_result = sut.load_meta_data()
		




		
		
		pass
		# assert False, "TODO: implement test"


	


