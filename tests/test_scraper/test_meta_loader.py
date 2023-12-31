"""test suite for meta_loader.py
sut = system under test
"""
import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock
from xml.etree import ElementTree as ET


import meta_loader 


class TestMetaLoader: 

	def __get_response(self, page:int=1) -> str:
		"""Returns test XML request."""

		test_response_file = Path(f"./tests/test_scraper/test_data/test_response_{page}.xml")
		test_response = test_response_file.read_text(encoding="utf-8")

		return test_response


	def __get_test_xml_list(self, page:int=1) -> list[str]:
		"""Returns test XML list."""
		test_response_file = Path(f"./tests/test_scraper/test_data/test_response_{page}.xml")
		test_response = test_response_file.read_text(encoding="utf-8")

		test_xml = ET.fromstring(test_response)
		test_xml_list = test_xml.findall(".//{http://ris.bka.gv.at/ogd/V2_6}OgdDocumentReference")
		
		return test_xml_list


	@patch("meta_loader.XML_Request", autospec=True)
	def test_load_two_pages(self, mock_request_class):
		"""The actual download is mocked out. The mock XML result files are 
		located in tests/test_scraper/. The xml request sent to the API is not 
		tested here, because the it is generated by the XML_Request class 
		(maybe a bad idea). The calls to XML_Request are also not tested, 
		because they are implementation details.
		"""
		
		mock_request_instance = MagicMock()
		mock_request_instance.send_xml_request.side_effect = [self.__get_response(1), self.__get_response(2)]
		mock_request_class.return_value = mock_request_instance
		sut = meta_loader.MetaLoader("vfgh", 2022)

		expected_result = self.__get_test_xml_list(1) + self.__get_test_xml_list(2)

		actual_result = sut.load_meta_data()

		for actual, expected in zip(actual_result, expected_result):
			assert ET.tostring(actual) == ET.tostring(expected)
		
		

class TestXMLRequest:
	"""Test if XML request (time constraints) is generated correctly."""

	def test_past_year(self):
		sut = meta_loader.XML_Request("vfgh", 2022)
		actual_result = sut.generate_xml_request(page_number=1)
		
		expected_result = Path("./tests/test_scraper/test_data/test_request.xml").read_text(encoding="utf-8")

		assert actual_result == expected_result


	@patch("meta_loader.DatetimeWrapper")
	def test_current_year(self, mock_wrapper): 
		mock_now = MagicMock()
		mock_now.return_value = "2023-05-05"
		mock_year = MagicMock()
		mock_year.return_value = "2023"
		mock_wrapper.now = mock_now
		mock_wrapper.year = mock_year

		sut = meta_loader.XML_Request("vfgh", "2023")
		
		expected_result = Path("./tests/test_scraper/test_data/test_request2.xml").read_text(encoding="utf-8") 

		actual_result = sut.generate_xml_request(page_number=1)

		assert actual_result == expected_result



class TestMetaSaver: 
	def __get_meta_collection(self) -> list[ET.Element]:
		e1 = ET.fromstring("<test1>abc</test1>")
		e2 = ET.fromstring("<test2>abc</test2>")
		
		return [e1, e2]

	
	@patch("meta_loader.MetaSaver._get_meta_data_file")
	def test_save_meta_data(self, mock_get_file):
		# setup
		test_file = Path("./tests/test_scraper/test_data/test_meta_data_actual.xml")
		mock_get_file.return_value = test_file
		expected_result_file = Path("./tests/test_scraper/test_data/test_meta_data_expected.xml")
		
		# act
		meta_loader.MetaSaver.save_meta_data(self.__get_meta_collection(), branch="vfgh", year="2022")

		# assert
		actual_result = test_file.read_text(encoding="utf-8")
		expected_result = expected_result_file.read_text(encoding="utf-8")
		assert actual_result == expected_result

		# teardown
		test_file.unlink()

		
		
		


	


