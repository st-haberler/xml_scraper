from pathlib import Path
import json
import xml.etree.ElementTree as ET

from zeep import Client


request_file = Path(r"xml\request_templates\brkons_query.xml")

request = request_file.read_text(encoding="utf-8")

client = Client(wsdl="https://data.bka.gv.at/ris/ogd/v2.6/?WSDL")

response = client.service.SearchDocumentsXml(request)

response_file = Path(r"data\bundesrecht\PHG\meta_data\meta_collection.xml")
response_file.parent.mkdir(parents=True, exist_ok=True)
response_file.write_text(response, encoding="utf-8")

