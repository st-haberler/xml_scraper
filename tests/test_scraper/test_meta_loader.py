import argparse
import datetime
from pathlib import Path 

import pytest
from unittest.mock import Mock, MagicMock
from unittest.mock import patch 

import xml.etree.ElementTree as ET

import meta_loader


# meta_loader.MetaLoader tests: meta_loader.MetaLoader.load_meta_data()
# Testing single-page response: does load_meta_data() return the expected list strings?
@patch("meta_loader.MetaLoader.send_xml_request")
@patch("meta_loader.MetaLoader.extract_meta_data")
@patch("meta_loader.MetaLoader.get_hits")
@patch("meta_loader.MetaLoader.get_page_size")
def test_load_meta_single_page(mock_page_size, mock_hits, mock_extract_meta, mock_send_xml_loader_request): 
    mock_page_size.return_value = 100
    mock_hits.return_value = 2
    mock_extract_meta.return_value = [ET.fromstring("<test>ABC</test>"),
                                      ET.fromstring("<test>DEF</test>")]
    mock_send_xml_loader_request.return_value = "not needed in this test"

    expected = [ET.fromstring("<test>ABC</test>"), 
                ET.fromstring("<test>DEF</test>")]

    test_loader = meta_loader.MetaLoader("vfgh", str(2021))
    result = test_loader.load_meta_data()

    for result_element, expected_element in zip(result, expected):
        assert result_element.tag == expected_element.tag
        assert result_element.text == expected_element.text



# meta_loader.MetaLoader tests: meta_loader.MetaLoader.load_meta_data()
# Testing multi-page response: does load_meta_data() return the expected list strings?
@patch("meta_loader.MetaLoader.send_xml_request")
@patch("meta_loader.MetaLoader.extract_meta_data")
@patch("meta_loader.MetaLoader.get_hits")
@patch("meta_loader.MetaLoader.get_page_size")
def test_load_meta_multi_page(mock_page_size, mock_hits, mock_extract_meta, mock_send_xml_loader_request):     
    mock_page_size.return_value = 100
    mock_hits.return_value = 101
    mock_extract_meta.side_effect = [[ET.fromstring("<test>ABC</test>"), 
                                      ET.fromstring("<test>DEF</test>")],
                                     [ET.fromstring("<test>GHI</test>"), 
                                      ET.fromstring("<test>JKL</test>")]]
    mock_send_xml_loader_request.return_value = "not needed in this test"

    expected = [ET.fromstring("<test>ABC</test>"), 
                ET.fromstring("<test>DEF</test>"),
                ET.fromstring("<test>GHI</test>"), 
                ET.fromstring("<test>JKL</test>")]
    
    test_loader = meta_loader.MetaLoader("vfgh", str(2021))
    result = test_loader.load_meta_data()

    assert len(result) == 4
    assert type(result) == list
    assert type(result[0]) == ET.Element
    for result_element, expected_element in zip(result, expected):
        assert result_element.tag == expected_element.tag
        assert result_element.text == expected_element.text
    
    
    
# meta_loader.MetaLoader tests: meta_loader.MetaLoader.get_xml_request()
# Testing get_xml_request(): does it return the expected string?
# Expected: page number, begin and end date are inserted into the XML template, 
# and the rest is unmodified.
@patch("meta_loader.MetaLoader.generate_date_range")
def test_get_xml_request(mock_get_date_range):
    mock_get_date_range.return_value = ("2022-01-01", "2022-12-31")
    
    test_loader = meta_loader.MetaLoader("vfgh", str(2021))
    result = test_loader.get_xml_request(page_number=666)
    
    assert type(result) == str
    assert "<Vfgh>" in result
    assert "</Vfgh>" in result
    assert "<EntscheidungsdatumVon>2022-01-01</EntscheidungsdatumVon>" in result
    assert "<EntscheidungsdatumBis>2022-12-31</EntscheidungsdatumBis>" in result
    assert "<Seitennummer>666</Seitennummer>" in result




# meta_loader.MetaLoader tests: meta_loader.MetaLoader.generate_date_range()
# Testing generate_date_range(): 
def test_generate_date_range_current_year():
    test_loader = meta_loader.MetaLoader("vfgh", str(datetime.datetime.now().year))
    result = test_loader.generate_date_range()
    
    assert type(result) == tuple
    assert result[0] == "2023-01-01"
    assert result[1] == str(datetime.datetime.now().strftime("%Y-%m-%d"))



def test_generate_date_range_not_current_year():
    test_loader = meta_loader.MetaLoader("vfgh", str(2020))
    result = test_loader.generate_date_range()
    
    assert type(result) == tuple
    assert result[0] == "2020-01-01"
    assert result[1] == "2020-12-31"



@patch("meta_loader.Client")
def test_send_xml_request(mock_Client):
	mock_Client.return_value =
	test_meta_loader = meta_loader.MetaLoader("vfgh", str(2020))
	
	result = test_meta_loader.send_xml_request("test")
	assert result == "test"
	
	


# meta_loader.MetaLoader tests: meta_loader.MetaLoader.get_hits()
def test_get_hits():
    mock_response = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
	<soap:Body>
		<SearchDocumentsResponse xmlns="http://ris.bka.gv.at/ogd/V2_6">
			<SearchDocumentsResult status="ok">
				<OgdDocumentResults>
					<Hits pageNumber="1" pageSize="10">666</Hits>
					<OgdDocumentReference>
						<Data>
							<Metadaten>
								<Technisch>
									<ID>JJR_20210707_OLG0009_03300R00011_21M0000_005</ID>
									<Applikation>Justiz</Applikation>
									<Organ>OLG Wien</Organ>
									<ImportTimestamp xsi:nil="true"/>
								</Technisch>
								<Allgemein>
									<Veroeffentlicht>2022-10-27</Veroeffentlicht>
									<Geaendert>2023-07-21</Geaendert>
									<DokumentUrl>https://www.ris.bka.gv.at/Dokument.wxe?Abfrage=Justiz&amp;Dokumentnummer=JJR_20210707_OLG0009_03300R00011_21M0000_005</DokumentUrl>
								</Allgemein>
								<Judikatur>
									<Dokumenttyp>Rechtssatz</Dokumenttyp>
									<Geschaeftszahl>
										<item>33R11/21m</item>
									</Geschaeftszahl>
									<Normen>
										<item>MSchG §10a</item>
									</Normen>
									<Entscheidungsdatum>2021-07-07</Entscheidungsdatum>
									<EuropeanCaseLawIdentifier>ECLI:AT:OLG0009:2021:RW0001019</EuropeanCaseLawIdentifier>
									<Justiz>
										<Rechtsgebiete>
											<item>Zivilrecht</item>
										</Rechtsgebiete>
										<Gericht>OLG Wien</Gericht>
										<Rechtssatznummern>
											<item>RW0001019</item>
										</Rechtssatznummern>
										<Anmerkung>Veröff ÖBl 2023/25, 80 (A. Stadler/Krickl)</Anmerkung>
										<Entscheidungstexte>
											<item>
												<Geschaeftszahl>33 R 11/21m</Geschaeftszahl>
												<Dokumenttyp>Text</Dokumenttyp>
												<Gericht>OLG Wien</Gericht>
												<Entscheidungsdatum>2021-07-07</Entscheidungsdatum>
												<DokumentUrl>https://www.ris.bka.gv.at/Dokument.wxe?Abfrage=Justiz&amp;Dokumentnummer=JJT_20210707_OLG0009_03300R00011_21M0000_000</DokumentUrl>
											</item>
										</Entscheidungstexte>
									</Justiz>
								</Judikatur>
							</Metadaten>
							<Dokumentliste>
								<ContentReference>
									<ContentType>MainDocument</ContentType>
									<Name>Hauptdokument</Name>
									<Urls>
										<ContentUrl>
											<DataType>Xml</DataType>
											<Url>https://www.ris.bka.gv.at/Dokumente/Justiz/JJR_20210707_OLG0009_03300R00011_21M0000_005/JJR_20210707_OLG0009_03300R00011_21M0000_005.xml</Url>
										</ContentUrl>
										<ContentUrl>
											<DataType>Html</DataType>
											<Url>https://www.ris.bka.gv.at/Dokumente/Justiz/JJR_20210707_OLG0009_03300R00011_21M0000_005/JJR_20210707_OLG0009_03300R00011_21M0000_005.html</Url>
										</ContentUrl>
										<ContentUrl>
											<DataType>Pdf</DataType>
											<Url>https://www.ris.bka.gv.at/Dokumente/Justiz/JJR_20210707_OLG0009_03300R00011_21M0000_005/JJR_20210707_OLG0009_03300R00011_21M0000_005.pdf</Url>
										</ContentUrl>
										<ContentUrl>
											<DataType>Rtf</DataType>
											<Url>https://www.ris.bka.gv.at/Dokumente/Justiz/JJR_20210707_OLG0009_03300R00011_21M0000_005/JJR_20210707_OLG0009_03300R00011_21M0000_005.rtf</Url>
										</ContentUrl>
									</Urls>
								</ContentReference>
							</Dokumentliste>
						</Data>
					</OgdDocumentReference>
				</OgdDocumentResults>
			</SearchDocumentsResult>
		</SearchDocumentsResponse>
	</soap:Body>
</soap:Envelope>"""

    test_loader = meta_loader.MetaLoader("vfgh", str(2020))
    result = test_loader.get_hits(mock_response)
    
    assert type(result) == int
    assert result == 666
    


# meta_loader.MetaLoader tests: meta_loader.MetaLoader.send_xml_request()
@patch("meta_loader.Client", autospec=True)
def test_send_xml_request(mock_client):
	mock_service = MagicMock()
	mock_service = MagicMock()
	mock_service.SearchDocumentsXml.return_value = "test"
	mock_client.return_value.service = mock_service
    
	result = meta_loader.MetaLoader("vfgh", 2020).send_xml_request("test")

	assert result == "test"
    


# meta_loader.MetaLoader tests: meta_loader.MetaLoader.extract_meta_data()
def test_extract_meta_data():
	response = """<?xml version='1.0' encoding='utf-8'?>
<root xmlns="http://ris.bka.gv.at/ogd/V2_6" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<OgdDocumentReference>A</OgdDocumentReference>
<OgdDocumentReference>B</OgdDocumentReference>
</root>"""
	
	test_loader = meta_loader.MetaLoader("vfgh", 2020)
	result = test_loader.extract_meta_data(response)
	
	assert len(result) == 2
	assert result[0].tag == "{http://ris.bka.gv.at/ogd/V2_6}OgdDocumentReference"
	assert result[0].text == "A"
	assert result[1].tag == "{http://ris.bka.gv.at/ogd/V2_6}OgdDocumentReference"	
	assert result[1].text == "B"



def test_get_meta_data_file():
	test_loader = meta_loader.MetaLoader("vfgh", 2020)
	result = test_loader.get_meta_data_file()
	 
	path = result.parent
	
	assert path.name == "meta_data"

	assert path.exists() == True
	assert path.is_file() == False   
	assert result.name == "vfgh_meta_collection_all_2020.xml"

