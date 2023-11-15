# this script searches the RIS for all decisions of one branch
# result is one xml file with the complete metadata of all decisions of one year
# the queries are created from xml files located in the ./xml folder (see global constants)
# each branch has its own xml file for the query because writing a template an adapting it 
# is more of a hassle 
# the query xml files are sent as parameters to the XMLSearch() function of the API 
# the validation files for the xml query files are located in the ./xml/xsd folder

import argparse
import datetime
import calendar
import xml.etree.ElementTree as ET
import lxml.etree as etree
from pathlib import Path
from zeep import Client


BRANCHES = ["vwgh", "vfgh", "justiz"]

SEARCH_YEAR = datetime.datetime.now().year
SEARCH_BRANCH = "justiz"
# DATA_PATH = Path.cwd() / "data" / "judikatur"/ SEARCH_BRANCH

# COLLECTION_FILE = f"{SEARCH_BRANCH}_meta_collection_all_{SEARCH_YEAR}.xml"

XSD_PATH = Path.cwd() / "xml" / "xsd"
VALIDATION_FILE = "OGD_Request.xsd"

REQUESTS_PATH = Path.cwd() / "xml" / "requests"
VWGH_XML_REQUEST = "vwgh_month_query.xml"
VFGH_XML_REQUEST = "vfgh_month_query.xml"
JUSTIZ_XML_REQUEST = "justiz_month_query.xml"
REQUEST_MAP = {"vfgh": VFGH_XML_REQUEST, 
               "vwgh": VWGH_XML_REQUEST, 
               "justiz": JUSTIZ_XML_REQUEST}
TEMP_FILE = Path.cwd() / "xml" / "temp.xml"
RIS_API_WSDL = "https://data.bka.gv.at/ris/ogd/v2.6/?WSDL"


def set_search_branch(branch:str):
    global SEARCH_BRANCH
    if branch not in BRANCHES: 
        # TODO: check if IndexError is the right exception.
        raise IndexError
    SEARCH_BRANCH = branch
    

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


def init_by_args() -> None:
    """
    Initialize the script by command line arguments.
    """
    global SEARCH_BRANCH, SEARCH_YEAR

    parser = argparse.ArgumentParser(description="Search the RIS for decisions of a specific branch.")
    parser.add_argument("-branch", choices=BRANCHES, help="The branch of the RIS to search in.")
    parser.add_argument("-year", type=int, help="The year to search in.")
    args = parser.parse_args()

    # general indtruction message
    print("Module for year-wise search of the RIS/Judikatur application. ")

    # check if arguments are valid, if not: display message and exit
    if args.branch not in BRANCHES:
        print(f"Invalid argument: Branch must be one of {BRANCHES}.")
        exit()
    if args.year < 1946 or args.year > datetime.datetime.now().year:
        print(f"Invalid argument: Year must be between 1946 and {datetime.datetime.now().year}.")
        exit()

    SEARCH_BRANCH = args.branch
    SEARCH_YEAR = args.year

    print(f"{SEARCH_BRANCH} is selected.")
    print(f"{SEARCH_YEAR} is selected.")


def is_valid_xml(xml_string) -> bool:
    """
    validates the query xml string against the xsd schema. Since apparently the xml 
    library does not support validation, we have to save the xml string to a file and 
    reload it again with the lxml library. The file is deleted afterwards.
    """    
    TEMP_FILE.write_text(xml_string, encoding="utf-8")
    xml_doc = etree.parse(str(TEMP_FILE))
    xsd = etree.XMLSchema(file=str(XSD_PATH / VALIDATION_FILE))

    try: 
        xsd.assertValid(xml_doc)
        # delete the temp file
        TEMP_FILE.unlink()
        return True
    except etree.DocumentInvalid as err:
        print(f"XML is invalid: {str(TEMP_FILE)}")
        print(err.error_log)
        return False


def add_response_to_collection(result_str:str, year:str) -> None:	
    """
    Input is the xml response from the RIS api for a search request. The function extracts the OgdDocumentReference 
    elements and saves them to a xml file. If the file already exists, the new elements are appended to the existing
    """
    file_name = f"{SEARCH_BRANCH}_meta_collection_all_{year}.xml"
    data_path = Path.cwd() / "data" / "judikatur" / SEARCH_BRANCH
    collection = data_path / file_name 
    
    result_xml = ET.fromstring(result_str)
 
    # result_root = result_xml.getroot()
    ogd_document_references = result_xml.findall('.//{http://ris.bka.gv.at/ogd/V2_6}OgdDocumentReference')
    
    new_root = ET.Element("root")
    for ogd_document_reference in ogd_document_references:
        new_root.append(ogd_document_reference)
    new_tree = ET.ElementTree(new_root)
    
    ET.register_namespace("", "http://ris.bka.gv.at/ogd/V2_6")
    if collection.exists():
        collection_xml = ET.parse(str(collection))
        collection_root = collection_xml.getroot()
        for ogd_document_reference in ogd_document_references:
            collection_root.append(ogd_document_reference)
        collection_xml.write(collection, encoding="utf-8", xml_declaration=True)  
    else:
        print(f"Creating new file {collection}")
        new_tree.write(collection, encoding="utf-8", xml_declaration=True)

    print(f"Saved {len(ogd_document_references)} new elements to {collection}")
    

# # Since add_to_collection seems to work perfectly, we dont need to save every response 
# # to a file in addition  
# def save_response_to_xmlfile(response:str, page_number:int=1, year:str="2023", month:str="01"): 
#     """
#     Accepts the xml response of the RIS api as string. Saves it to a file.
#     """
#     file_name = f"temp_y{year}_m{month}_pg{page_number:02d}.xml"
#     Path(Path.cwd() / "xml" / file_name).write_text(response, encoding="utf-8")



def generate_xml_request(begin:str, end:str, page:int=1) -> str:
    """
    Generates a xml request for the RIS api. Returns a string, but in XML format.
    begin and end are strings in the format YYYY-MM-DD and are applied to "Entscheidungsdatum"
    See https://data.bka.gv.at/ris/ogd/v2.6/Documents/Dokumentation_OGD-RIS_Service.pdf
    for the API documentation.
    """    
    assert is_valid_date(begin)
    assert is_valid_date(end)
    
    tree = ET.parse(str(REQUESTS_PATH / REQUEST_MAP[SEARCH_BRANCH]))
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


def execute_xml_request(xml_request:str) -> str:
    """
    Sends the xml request to the RIS api and returns the xml response as string.
    API Url and services are from the documentation at: 
    https://data.bka.gv.at/ris/ogd/v2.6/Documents/Dokumentation_OGD-RIS_Service.pdf
    """
    global RIS_API_WSDL
    
    client = Client(RIS_API_WSDL)
    search_xml_result = client.service.SearchDocumentsXml(xml_request)
    return search_xml_result


def download_full_month(begin:str, end:str) -> None:
    """
    Returns a list with metadata and links of all decisions in the given month and year. 
    If the year is the current year, the function will skip the months that are in the 
    future.
    The function works by generating a xml request for the full month. The response 
    is limited to max 100 hits. if there are more than 100 hits, the function will  
    generate a new xml request for the next page and repeat the process until all 
    pages are downloaded. 
    Every response is saved to a separate xml file and also added to a collection file.
    """
    if not (is_valid_date(begin) and is_valid_date(end)): return
    
    # we need month and year for the file name. we assume that month can be extracted 
    # from the begin date at the given position. 
    year = SEARCH_YEAR
    month = begin[5:7]
    page_number = 1

    # loop through all pages of the search result
    while True:
        print(f"download_full_month(): {month = }, {year = }, {page_number = }")

        xml_request = generate_xml_request(begin, end, page_number)
        response = execute_xml_request(xml_request)

        # save result of current page 
        # # we probably dont need that (see comment in definition); maybe delete later
        # save_response_to_xmlfile(response, page_number=page_number, year=year, month=month)
        print(f"download_full_month(): calling add_to_collection with {year = }")
        add_response_to_collection(result_str=response, year=year)
        
        # check if we need a request for the next page
        response_xml = ET.fromstring(response)
        hits = int(response_xml.find(".//{http://ris.bka.gv.at/ogd/V2_6}Hits").text)
        if hits > page_number * 100:
            page_number += 1
            xml_request = generate_xml_request(begin, end, page_number)
        else: 
            break


def download_full_year(year:int=SEARCH_YEAR): 
    """
    Entry point for the script right after initialization. Keep in mind that 
    the year parameter will has to be the current year or lower, otherwise
    the script will not download anything, without any error message.
    """
    def get_days_in_month(year:int, month:int) -> int:
        _, num_days = calendar.monthrange(year, month)
        return num_days
    
    date_range = [(f"{year}-{month:02d}-01", f"{year}-{month:02d}-{get_days_in_month(year, month)}") for month in range(1, 13)]
    for begin, end in date_range:
        download_full_month(begin, end)


if __name__ == "__main__": 
    init_by_args()
    download_full_year(year=SEARCH_YEAR)