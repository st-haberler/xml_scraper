# unifies all features of the decision scraper (search, link extraction, download, conversion into json)
# and provides a command line interface
# branch and year are the only arguments; they are global since they are more like constants 

import argparse
from pathlib import Path
import datetime
import calendar
import xml.etree.ElementTree as ET 
import lxml.etree as etree

BRANCHES = ["vfgh", "vwgh", "justiz"]

REQUESTS_PATH = Path.cwd() / "xml" / "requests"
VWGH_XML_REQUEST = "vwgh_month_query.xml"
VFGH_XML_REQUEST = "vfgh_month_query.xml"
JUSTIZ_XML_REQUEST = "justiz_month_query.xml"
REQUEST_MAP = {"vfgh": VFGH_XML_REQUEST, 
               "vwgh": VWGH_XML_REQUEST, 
               "justiz": JUSTIZ_XML_REQUEST}

TEMP_FILE = Path.cwd() / "xml" / "temp.xml"
XSD_PATH = Path.cwd() / "xml" / "xsd"
VALIDATION_FILE = "OGD_Request.xsd"



def init_args() -> None:
    """
    Initializes the scraper by command line arguments.
    """
    global branch, year

    parser = argparse.ArgumentParser(description="Download decisions via the RIS API.")
    parser.add_argument("-branch", type=str, help=f"The branch of law to download decisions from: {BRANCHES}")
    parser.add_argument("-year", type=str, help="The year to download decisions from.")
    args = parser.parse_args()

    branch = args.branch
    year = args.year

    assert branch in BRANCHES, f"Invalid branch. Must be one of {BRANCHES}."
    assert int(year) <= datetime.datetime.now().year, f"Invalid year. Must be between today and 1946"
    assert int(year) >= 1946, f"Invalid year Must be between today and 1946."

    print(f"{branch} from {year} is selected.")


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


def generate_xml_request(begin:str, end:str, page:int=1) -> str:
    """
    Generates a xml request for the RIS api. Returns a string, but in XML format.
    begin and end are strings in the format YYYY-MM-DD and are applied to "Entscheidungsdatum"
    See https://data.bka.gv.at/ris/ogd/v2.6/Documents/Dokumentation_OGD-RIS_Service.pdf
    for the API documentation.
    """    
    assert is_valid_date(begin)
    assert is_valid_date(end)
    
    tree = ET.parse(str(REQUESTS_PATH / REQUEST_MAP[branch]))
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


def download_full_month(begin:str, end:str) -> None:
    """
    Downloads a list with metadata and links of all decisions in the given month and year. 
    If the year is the current year, the function will skip the months that are in the 
    future.
    The function works by generating a xml request for the full month. The response 
    is limited to max 100 hits. if there are more than 100 hits, the function will  
    generate a new xml request for the next page and repeat the process until all 
    pages are downloaded. 
    Every response is added to a collection file.
    """
    # if begin or end are in the future: no search 
    if not (is_valid_date(begin) and is_valid_date(end)): return
    
    # we need month and year for the file name. we assume that month can be extracted 
    # from the begin date at the given position. 
  
    page_number = 1

    # loop through all pages of the search result
    while True:
        xml_request = generate_xml_request(begin, end, page_number)
        response = execute_xml_request(xml_request)

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



def download_meta_full_year() -> None: 
    """
    Entry point for the script right after initialization. Keep in mind that 
    the year parameter will has to be the current year or lower, otherwise
    the script will not download anything, without any error message.
    """
    # helper function, returns last day given month of given year
    def get_days_in_month(year:int, month:int) -> int:
        _, num_days = calendar.monthrange(year, month)
        return num_days
    
    # date_range is list of tuple of first and last day of every month of 
    # the given year as string YYYY-MM-DD
    date_range = [(f"{year}-{month:02d}-01", f"{year}-{month:02d}-{get_days_in_month(year, month)}") for month in range(1, 13)]
    
    for begin, end in date_range:
        download_full_month(begin, end)


if __name__ == "__main__": 
    init_args()
    download_meta_full_year()