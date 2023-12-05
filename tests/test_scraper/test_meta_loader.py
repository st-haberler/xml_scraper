"""test suite for meta_loader.py
sut = system under test
"""
from unittest.mock import patch


import meta_loader 


MOCK_RESPONSE = "MOCK"

class TestMetaLoader: 
    
	@patch("meta_loader.XML_Request")
	def test_load_meta_data(self, mock_request_class):
		
		mock_xml_request = mock_request_class.return_value
		mock_xml_request.generate_xml_request.return_value = "test_request"
		mock_xml_request.send_xml_request.return_value = MOCK_RESPONSE

		sut = meta_loader.MetaLoader("vfgh", 1951)



		
		
		pass
		# assert False, "TODO: implement test"


	


