from zeep import Client
from lxml import etree
from pathlib import Path
import xml.etree.ElementTree as ET


## FIRST PART: MODIFY XML

tree = ET.parse(r"xml\requests_examples\justiz_query_01.xml")
root = tree.getroot()
begin = root.find(".//{http://ris.bka.gv.at/ogd/V2_6}EntscheidungsdatumVon")
end = root.find(".//{http://ris.bka.gv.at/ogd/V2_6}EntscheidungsdatumBis")


begin.text = "2023-09-01"
end.text = "2023-09-30"

ET.register_namespace("", "http://ris.bka.gv.at/ogd/V2_6")
tree.write(r"xml\requests_examples\justiz_query_02.xml")

## SECOND PART: VALIDATE XML AGAINST XSD

xml_doc = etree.parse(r"xml\requests_examples\justiz_query_02.xml")
xsd = etree.XMLSchema(file=r"xml\xsd\OGD_Request.xsd")

try: 
    xsd.assertValid(xml_doc)
    print("XML is valid")
except etree.DocumentInvalid as err:
    print("XML is invalid")
    print(err.error_log)


## THIRD PART: SEND REQUEST TO API

xml = etree.tostring(xml_doc)

client = Client("https://data.bka.gv.at/ris/ogd/v2.6/?WSDL")

search_xml_result = client.service.SearchDocumentsXml(xml)
print(search_xml_result)

## FOURTH PART: SAVE RESULT TO FILE

Path(r"xml\temp2.xml").write_text(search_xml_result, encoding="utf-8")
