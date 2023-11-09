# download requests for decisions from everey month in 2023 
# extract the OgdDocumentReference for each decision and save it to a list/file 
# before saving: check if the decision is already in the list/file

import calendar
import datetime
import xml.etree.ElementTree as ET
from lxml import etree
from zeep import Client
from pathlib import Path

def get_days_in_month(year:int, month:int) -> int:
    _, num_days = calendar.monthrange(year, month)
    return num_days

def get_current_month() -> int:
    return datetime.datetime.now().month


def get_date_range(year:int) -> list:
    """
    returns list of tuples with (begin_date, end_date), 
    where each tuple represents the first and the last day of one month of a given year
    date format: YYYY-MM-DD
    """
    return [(f"{year}-{month:02d}-01", f"{year}-{month:02d}-{get_days_in_month(year, month)}") for month in range(1, 13)]


#---------------------------------------------

YEAR = 2023
DATE_RANGE = get_date_range(YEAR)
query_template = ET.parse(r"xml\requests_examples\justiz_query_01.xml")
root = query_template.getroot()
begin_date_element = root.find(".//{http://ris.bka.gv.at/ogd/V2_6}EntscheidungsdatumVon")
end_date_element = root.find(".//{http://ris.bka.gv.at/ogd/V2_6}EntscheidungsdatumBis")
save_file = Path(Path.cwd() / "xml" / "justiz_all_2023.xml")


# prepare search request xml 
all_search_results_xml = []
search_template = ET.parse(r"xml\requests_examples\justiz_query_01.xml")
root = search_template.getroot()
begin = root.find(".//{http://ris.bka.gv.at/ogd/V2_6}EntscheidungsdatumVon")
begin.text = "2023-01-01"
end = root.find(".//{http://ris.bka.gv.at/ogd/V2_6}EntscheidungsdatumBis")
end.text = "2023-01-31"
ET.register_namespace("", "http://ris.bka.gv.at/ogd/V2_6")
search_template.write(r"xml\requests_examples\justiz_query_02.xml")

# validate search request xml against xsd
search_query = etree.parse(r"xml\requests_examples\justiz_query_02.xml")
xsd = etree.XMLSchema(file=r"xml\xsd\OGD_Request.xsd")
try: 
    xsd.assertValid(search_query)
except etree.DocumentInvalid as err:
    print("XML is invalid")
    print(err.error_log)

# Send search request to API
search_query_string = etree.tostring(search_query)
client = Client("https://data.bka.gv.at/ris/ogd/v2.6/?WSDL")
search_result_string = client.service.SearchDocumentsXml(search_query_string)
print(f"{type(search_result_string) = }")

# save result to file
Path(r"xml\temp.xml").write_text(search_result_string, encoding="utf-8")

# load file and extract document references from search result
search_result_xml = etree.parse(r"xml\temp.xml")

all_documents = search_result_xml.findall(".//{http://ris.bka.gv.at/ogd/V2_6}OgdDocumentReference")
print(f"{len(all_documents) = }")


all_search_results_xml = []
for doc in all_documents: 
    all_search_results_xml.append(doc)

# save search result to file
for ref_xml in all_search_results_xml:
    ref_str = etree.tostring(ref_xml)
    with save_file.open("a", encoding="utf-8") as f:
        f.write(ref_str.decode("utf-8"))
        f.write("\n")





# all_search_results_string = etree.tostring(all_search_results_xml)
# save_file.write_text(all_search_results_string, encoding="utf-8")


# for month in range(1): 
#     BEGIND_DATE = DATE_RANGE[month][0]
#     END_DATE = DATE_RANGE[month][1]
#     begin_date_element.text = BEGIND_DATE
#     end_date_element.text = END_DATE
#     ET.register_namespace("", "http://ris.bka.gv.at/ogd/V2_6")
#     query_template.write(r"xml\requests_examples\justiz_query_02.xml")

#     xml_query = etree.parse(r"xml\requests_examples\justiz_query_02.xml")
#     xsd = etree.XMLSchema(file=r"xml\xsd\OGD_Request.xsd")
#     try: 
#         xsd.assertValid(xml_query)
#     except etree.DocumentInvalid as err:
#         print("XML is invalid")
#         print(err.error_log) 
#     xml = etree.tostring(xml_query)
#     print(f"{xml = }")
#     client = Client("https://data.bka.gv.at/ris/ogd/v2.6/?WSDL")
#     search_result_string = client.service.SearchDocumentsXml(xml)
#     Path(r"xml\temp.xml").write_text(search_result_string, encoding="utf-8")

#     search_result_xml = etree.parse(r"xml\temp.xml")
#     all_documents = search_result_xml.findall(".//{http://ris.bka.gv.at/ogd/V2_6}OgdDocumentReference")
#     print("-------------------")
#     print(all_documents[0].text)
#     print("-------------------")

#     for doc in all_documents: 
#         search_results.append(doc.text)







    
