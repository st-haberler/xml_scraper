from pathlib import Path
import xml.etree.ElementTree as ET
import datetime
import calendar
from zeep import Client


RIS_API_WSDL = "https://data.bka.gv.at/ris/ogd/v2.6/?WSDL"
client = Client(RIS_API_WSDL)

xml_request = Path(r"xml\requests_examples\OgdVwgh.xml").read_text(encoding="utf-8")

search_xml_result = client.service.SearchDocumentsXml(xml_request)

print(search_xml_result)