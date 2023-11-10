from pathlib import Path
import xml.etree.ElementTree as ET
import datetime
import calendar
from zeep import Client
import lxml.etree as etree

RIS_API_WSDL = "https://data.bka.gv.at/ris/ogd/v2.6/?WSDL"


def is_valid_xml(xml_string) -> bool:
    Path(r"xml\temp.xml").write_text(xml_string, encoding="utf-8")
    xml_doc = etree.parse(r"xml\temp.xml")
    xsd = etree.XMLSchema(file=r"xml\xsd\OGD_Request.xsd")

    try: 
        xsd.assertValid(xml_doc)
        print("XML is valid")
        return True
    except etree.DocumentInvalid as err:
        print("XML is invalid")
        print(err.error_log)
        return False


def is_valid_date(input_date:str) -> bool:
    """
    Checks if the date is in the format YYYY-MM-DD. Returns True if it is, False otherwise.
    """
    try:
        date = datetime.datetime.strptime(input_date, '%Y-%m-%d')
        assert date <= datetime.datetime.now()
        return True
    except (ValueError, AssertionError):
        return False


def execute_xml_request(xml_request:str) -> str:
    """
    Sends the xml request to the RIS api and returns the xml response as string.
    """
    client = Client(RIS_API_WSDL)
    search_xml_result = client.service.SearchDocumentsXml(xml_request)
    return search_xml_result

def generate_xml_request(begin:str, end:str, page:int=1) -> str:
    """
    Generates a xml request for the RIS api. Returns a string, but in XML format.
    begin and end are strings in the format YYYY-MM-DD and are applied to "Entscheidungsdatum"
    """
    assert is_valid_date(begin)
    assert is_valid_date(end)
    
    tree = ET.parse(r"xml\requests_examples\vwgh_query_01.xml")
    root = tree.getroot()
    begin_element = root.find(".//{http://ris.bka.gv.at/ogd/V2_6}EntscheidungsdatumVon")
    end_element = root.find(".//{http://ris.bka.gv.at/ogd/V2_6}EntscheidungsdatumBis")
    seitennummer_element = root.find(".//{http://ris.bka.gv.at/ogd/V2_6}Seitennummer")
    begin_element.text = begin
    end_element.text = end
    seitennummer_element.text = str(page)

    ET.register_namespace("", "http://ris.bka.gv.at/ogd/V2_6")
    root_string = ET.tostring(root, encoding="utf-8").decode("utf-8")

    assert is_valid_xml(root_string)
    return root_string



def save_response_to_collection(result_str:str="", year:str="2023") -> None:	
    """
    Input is the xml response from the RIS api for a search request. The function extracts the OgdDocumentReference 
    elements and saves them to a xml file. If the file already exists, the new elements are appended to the existing
    """
    file_name = f"vwgh_meta_collection_all_{year}.xml"
    COLLECTION = Path(Path.cwd() / "xml" / file_name) 
    
    result_xml = ET.fromstring(result_str)
 
    
    # result_root = result_xml.getroot()
    ogd_document_references = result_xml.findall('.//{http://ris.bka.gv.at/ogd/V2_6}OgdDocumentReference')
    
    new_root = ET.Element("root")
    for ogd_document_reference in ogd_document_references:
        new_root.append(ogd_document_reference)
    new_tree = ET.ElementTree(new_root)
    
    ET.register_namespace("", "http://ris.bka.gv.at/ogd/V2_6")
    if COLLECTION.exists():
        collection_xml = ET.parse(COLLECTION)
        collection_root = collection_xml.getroot()
        print(f"Previous total number of elements in {COLLECTION}: {len(collection_root)}")
        for ogd_document_reference in ogd_document_references:
            collection_root.append(ogd_document_reference)
        collection_xml.write(COLLECTION, encoding="utf-8", xml_declaration=True)  
    else:
        print(f"Creating new file {COLLECTION}")
        new_tree.write(COLLECTION, encoding="utf-8", xml_declaration=True)

    print(f"Saved {len(ogd_document_references)} elements to {COLLECTION}")
    

def save_response_to_xmlfile(response:str, page_number:int=1, year:str="2023", month:str="01"): 
    """
    Accepts the xml response of the RIS api as string. Saves it to a file.
    """
    file_name = f"temp_y{year}_m{month}_pg{page_number:02d}.xml"
    Path(Path.cwd() / "xml" / file_name).write_text(response, encoding="utf-8")


def download_full_month(begin:str, end:str):
    """
    Returns a list of all dates in the given month and year. 
    """
    if not (is_valid_date(begin) and is_valid_date(end)): return
    
    page_number = 1
    year = begin[0:4]
    print(f"{year = }")
    month = begin[5:7]
    print(f"{month = }")
    xml_request = generate_xml_request(begin, end, page_number)
    
    while True:
        # save result of current page 
        response = execute_xml_request(xml_request)
        response_xml = ET.fromstring(response)
        save_response_to_xmlfile(response, page_number=page_number, year=year, month=month)
        
        save_response_to_collection(result_str=response, year=year)
        
        # check if we need to go to next page
        hits = int(response_xml.find(".//{http://ris.bka.gv.at/ogd/V2_6}Hits").text)
        if hits > page_number * 100:
            page_number += 1
            xml_request = generate_xml_request(begin, end, page_number)
        else: 
            break


def download_full_year(year:int): 
    def get_days_in_month(year:int, month:int) -> int:
        _, num_days = calendar.monthrange(year, month)
        return num_days
    
    date_range = [(f"{year}-{month:02d}-01", f"{year}-{month:02d}-{get_days_in_month(year, month)}") for month in range(1, 13)]

    for begin, end in date_range:
        download_full_month(begin, end)


def collection_counter(year:int=2023): 
    """
    Counts the number of elements in the collection file.
    """
    file_name = f"vfgh_meta_collection_all_{year}.xml"
    COLLECTION = Path(Path.cwd() / "xml" / file_name) 
    
    collection_xml = ET.parse(COLLECTION)
    collection_root = collection_xml.getroot()
    print(f"Total number of elements in {COLLECTION}: {len(collection_root)}")    


if __name__ == "__main__":
    
    download_full_year(2023)
    collection_counter(2023)