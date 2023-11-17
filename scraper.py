# Decision Scraper for the Austrian Legal Information System (RIS)
# Usage: python scraper.py -branch <branch> -year <year> 
# Example: python scraper.py -branch vfgh -year 2020
# Downloads all decisions from the given year and branch of law and saves them as 
# - separate html files 
# - one json file
# - one xml file with metadata
# - one text file with the downloadlinks of the html files (for future reference)
# Author: Stefan Haberler stefan.haberler[at]stefan.priv.at
# Date: 2023-15-11
# 
# unifies all features of the decision scraper (search, link extraction, download, conversion into json)
# and provides a command line interface
# branch and year are the only arguments; they are global since they are more like constants 
# Apart from the global constants at the top, the script contains more global variables that are 
# dynamically set using the command line arguments. 

import argparse
import logging
import datetime
import calendar
import requests
import re
import json
import xml.etree.ElementTree as ET 
import lxml.etree as etree
from pathlib import Path
from zeep import Client
from bs4 import BeautifulSoup
import os




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

RIS_API_WSDL = "https://data.bka.gv.at/ris/ogd/v2.6/?WSDL"



def init_script() -> None:
    """
    Initializes the scraper by command line arguments. All global variables of the script are set here.
    """
    global branch, year
    global meta_collection_file 
    global link_collection_file 
    global html_target_path
    global json_target_path
    global missing_links_file

    parser = argparse.ArgumentParser(description="Download decisions via the RIS API.")
    parser.add_argument("-branch", type=str, help=f"The branch of law to download decisions from: {BRANCHES}")
    parser.add_argument("-year", type=str, help="The year to download decisions from.")
    args = parser.parse_args()

    branch = args.branch
    year = args.year


    if not all([branch, year]): 
        print("Usage: python scraper.py -branch <branch> -year <year>")
        print("Example: python scraper.py -branch vfgh -year 2020")
        exit(2)
    if not all([(branch in BRANCHES), 
                (1946 <= int(year) <= datetime.datetime.now().year)]):
        print("Usage: python scraper.py -branch <branch> -year <year>")
        print(f"<branch> must be one of {BRANCHES}. <year> must be between 1946 and today.")
        print("Example: python scraper.py -branch vfgh -year 2020")
        exit(2)

    # assert branch in BRANCHES, f"Invalid branch. Must be one of {BRANCHES}."
    # assert int(year) <= datetime.datetime.now().year, f"Invalid year. Must be between today and 1946"
    # assert int(year) >= 1946, f"Invalid year. Must be between today and 1946."

    meta_data_path = Path.cwd() / "data" / "judikatur" / branch / "meta_data"
    if not meta_data_path.exists(): meta_data_path.mkdir(parents=True)

    meta_collection_file = meta_data_path / f"{branch}_meta_collection_all_{year}.xml" 
    link_collection_file = meta_data_path / f"{branch}_all_decision_links_{year}.links"
    missing_links_file = meta_data_path / f"{branch}_missing_links_{year}.links"
    
    html_target_path = Path.cwd() / "data" / "judikatur" / branch / f"html_{year}"
    if not html_target_path.exists(): html_target_path.mkdir(parents=True)

    json_target_path = Path.cwd() / "data" / "judikatur" / branch / f"json_database"
    if not json_target_path.exists(): json_target_path.mkdir(parents=True)

    logging.basicConfig(level=logging.INFO)
    logging.info(f"Starting scraper for {branch} from {year}.")


class Decision_Json_Converter:
    def __init__(self) -> None:
        self.year = year
        self.branch = branch
        self.json_database = json_target_path / f"all_{self.year}.json"


    def _get_decision_id(self, file_name:str) -> str: 
        """returns the decision id from the file name"""
        decision_id = file_name[:-5]
        return decision_id

    def is_decision_in_db(self, new_decision, db_content) -> bool: 
        """checks if the decision is already in the database"""
        for decision in db_content: 
            if decision["decision_id"] == new_decision["decision_id"]: 
                return True
        return False

    def add_to_database(self, new_decision_struct:dict) -> None: 
        # if the database does not exist yet, create it
        # otherwise load it, check if the decision is already in it, and append if not
        if not self.json_database.exists(): 
            self.json_database.touch()
            self.json_database.write_text(json.dumps([new_decision_struct], indent=4, ensure_ascii=False), encoding="utf-8")
        else:
            with open(self.json_database, "r", encoding="utf-8") as f: 
                database_content = json.load(f)
            if not self.is_decision_in_db(new_decision_struct, database_content): 
                database_content.append(new_decision_struct)
                with open(self.json_database, "w", encoding="utf-8") as f: 
                    json.dump(database_content, f, indent=4, ensure_ascii=False)
            else: 
                logging.info(f"Decision {new_decision_struct['decision_id']} already in database.")

    def convert_all(self) -> None:
        """
        Converts the decision body of all html files in the html_target_path to json 
        and saves them to the json_target_path.
        """
        counter = 0 
        for html_file in html_target_path.iterdir():

            decision_id = self._get_decision_id(html_file.name)
            soup = BeautifulSoup(html_file.read_text(encoding="utf-8"), "html.parser")
            
            # find the decision body: <body><div><div><h1>Begründung</h1><p>...</p><p>...</p>...
            decision_body = []
            for div in soup.body.div.find_all("div"): 
                # check if h1 tag exists and if it contains "Begründung"
                if div.h1 and (("Begründung" in div.h1.text)
                            or ("Text" in div.h1.text)
                            or ("Rechtliche Beurteilung" in div.h1.text)): 
                    for para in div.find_all("p"):  
                        # remove tags that are not meant for written text 
                        for sr in para.find_all("span", class_="sr-only"): 
                            sr.decompose()
                        decision_body.append(para.text)

            decision_struct = {"decision_id": decision_id, "decision_body": decision_body}
            self.add_to_database(decision_struct)

            counter += 1

        logging.info(f"Converted {counter} decisions for {self.branch} / {self.year} into json database.")
        

class Decision_Downloader:
    def __init__(self) -> None:
        self.year = year
        self.branch = branch


    def _get_filename(self, link:str) -> str:
        """
        Extracts the filename from a link ie the substring after the last slash.
        """
        try: 
            filename = re.search(r"\/([^\/]+)$", link).group(1)
            return filename
        except AttributeError as e:
            logging.error(f"Could not extract filename from:\n{link}.", exc_info=True)
            return None



    def download_decisions(self) -> None:
        """
        Downloads all decisions as html from the link_collection_file and saves them to the html_target_path.
        The links of failed downloads are saved to the missing_links_file.
        """
        
        link_list = self.link_collection.read_text().split("\n")

        counter = 0
        for link in link_list: 
            decision_html_file = self._get_filename(link)
            if (not decision_html_file is None) and (decision_html_file in [html_file.name for html_file in html_target_path.iterdir()]): 
                logging.info(f"{decision_html_file} already exists.")
                continue
            try: 
                response = requests.get(link, timeout=10)
            except Exception as e:
                logging.error(f"Could not download {decision_html_file} (added to missing links)", exc_info=True)
                if not missing_links_file.exists():
                    missing_links_file.touch()
                with missing_links_file.open("a") as f: 
                    f.write(f"{link}\n")
                continue
            (html_target_path / decision_html_file).write_text(response.text, encoding="utf-8")
            counter += 1

        logging.info(f"Downloaded {counter} decisions for {self.branch} / {self.year}.")


class Link_Collection: 
    def __init__(self) -> None:
        self.year = year	
        self.branch = branch
        self.ns = {'ogd': 'http://ris.bka.gv.at/ogd/V2_6'}
        self.content_reference_element = "ogd:OgdDocumentReference/ogd:Data/ogd:Dokumentliste/ogd:ContentReference"
        self.links = []
        # get file path for link_collection_file from global variable in init_script():
        self.link_collection = link_collection_file


    def extract_xml_from_collection(self) -> None:
        """
        Extracts the xml from the metadata collection file for the given branch and year.
        """    
        # get file path for meta_collection_file from global variable in init_script():
        self.meta_collection_file = meta_collection_file
        self.meta_collection_xml = ET.parse(self.meta_collection_file)
        self.meta_collection_root = self.meta_collection_xml.getroot()


    def extract_links_from_xml(self) -> None:   
        """
        Finds all document links in the metadata collection and saves them to self.links 
        for future use inside the Link_Collection object ie for saving to file.
        """
        content_reference_list = self.meta_collection_root.findall(f".//{self.content_reference_element}", namespaces=self.ns)

        # filtered list excludes documents that are not decisions (embedded attachments, etc.)
        filtered_content_reference_list = []
        for content_reference in content_reference_list:
            if content_reference.find("ogd:ContentType", namespaces=self.ns).text == "MainDocument" and content_reference.find("ogd:Name", namespaces=self.ns).text == "Hauptdokument":
                filtered_content_reference_list.append(content_reference)

        for content_reference in filtered_content_reference_list:
            try: 
                urls_element = content_reference.find("ogd:Urls", namespaces=self.ns)
                for content_url in urls_element:
                    if content_url.find("ogd:DataType", namespaces=self.ns).text == "Html":
                        new_link = content_url.find("ogd:Url", namespaces=self.ns).text
                        self.links.append(new_link)
            except AttributeError as e:
                logging.error(f"Could not extract link from meta_data xml.", exc_info=True)
                continue    


    def save_links_to_file(self) -> None:
        with open(self.link_collection, "w") as f:
            for link in self.links:
                f.write(f"{link}\n")

        logging.info(f"Saved {len(self.links)} links to {self.link_collection}.")


    def retrieve_links(self) -> None:
        """
        Entry point for the class right after initialization. Keep in mind that 
        the year parameter will has to be the current year or lower, otherwise
        the script will not download anything, without any error message.
        """
        self.extract_xml_from_collection(self.branch, self.year)
        self.extract_links_from_xml()
        self.save_links_to_file()

        logging.info(f"Finished downloading links for {self.branch} / {self.year}.")


class Meta_Data_Collection:
    def __init__(self) -> None:
        self.branch = branch
        self.year = year
        # get file path from global variable in init_script():
        self.meta_collection = meta_collection_file


    def _is_valid_date(self, input_date:str) -> bool:
        """
        Checks if the date is in the format YYYY-MM-DD. Returns True if it is, False otherwise.
        """
        try:
            date = datetime.datetime.strptime(input_date, '%Y-%m-%d')
            assert date <= datetime.datetime.now()
            return True
        except (ValueError, AssertionError):
            return False


    def _is_valid_xml(self, xml_string:str) -> bool:
        """
        validates the query xml string against the xsd schema. Since apparently the xml 
        library does not support validation, we have to save the xml string to a file and 
        reload it again with the lxml library. The file is deleted afterwards.
        """    
        TEMP_FILE.write_text(xml_string, encoding="utf-8")
        xml_doc = etree.parse(str(TEMP_FILE))
        xsd = etree.XMLSchema(file=str(XSD_PATH / VALIDATION_FILE))

        xml_is_valid = True

        try: 
            xsd.assertValid(xml_doc)
        except etree.DocumentInvalid as err:
            logging.error(f"XML is invalid: {str(TEMP_FILE)}", exc_info=True)
            xml_is_valid = False
        finally: 
            TEMP_FILE.unlink()
        
        return xml_is_valid


    def generate_xml_request(self, begin:str, end:str, page:int=1) -> str:
        """
        Generates a xml request for the RIS api. Returns a string, but in XML format.
        begin and end are strings in the format YYYY-MM-DD and are applied to "Entscheidungsdatum"
        See https://data.bka.gv.at/ris/ogd/v2.6/Documents/Dokumentation_OGD-RIS_Service.pdf
        for the API documentation.
        """    
        assert self._is_valid_date(begin)
        assert self._is_valid_date(end)
        
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

        assert self._is_valid_xml(root_string), "XML request is invalid. "
        return root_string


    def execute_xml_request(self, xml_request:str) -> str:
        """
        Sends the xml request to the RIS api and returns the xml response as string.
        API Url and services are from the documentation at: 
        https://data.bka.gv.at/ris/ogd/v2.6/Documents/Dokumentation_OGD-RIS_Service.pdf
        """    
        client = Client(RIS_API_WSDL)
        search_xml_result = client.service.SearchDocumentsXml(xml_request)
        return search_xml_result


    def add_response_to_collection(self, result_str:str) -> None:	
        """
        Input is the xml response from the RIS api for a search request. The function extracts the OgdDocumentReference 
        elements and saves them to a xml file. If the file already exists, the new elements are appended to the existing
        """        
        result_xml = ET.fromstring(result_str)
        ogd_document_references = result_xml.findall(".//{http://ris.bka.gv.at/ogd/V2_6}OgdDocumentReference")
        
        new_root = ET.Element("root")
        for ogd_document_reference in ogd_document_references:
            new_root.append(ogd_document_reference)
        new_tree = ET.ElementTree(new_root)
        
        ET.register_namespace("", "http://ris.bka.gv.at/ogd/V2_6")
        if self.meta_collection.exists():
            collection_xml = ET.parse(str(self.meta_collection))
            collection_root = collection_xml.getroot()
            for ogd_document_reference in ogd_document_references:
                collection_root.append(ogd_document_reference)
            collection_xml.write(self.meta_collection, encoding="utf-8", xml_declaration=True)  
        else:
            new_tree.write(self.meta_collection, encoding="utf-8", xml_declaration=True)
  

    def download_full_month(self, begin:str, end:str) -> None:
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
        if not (self._is_valid_date(begin) and self._is_valid_date(end)): return
            
        page_number = 1

        # loop through all pages of the search result
        while True:
            xml_request = self.generate_xml_request(begin, end, page_number)
            response = self.execute_xml_request(xml_request)

            self.add_response_to_collection(result_str=response)
            
            # check if we need a request for the next page
            response_xml = ET.fromstring(response)
            hits = int(response_xml.find(".//{http://ris.bka.gv.at/ogd/V2_6}Hits").text)
            if hits > page_number * 100:
                page_number += 1
                xml_request = self.generate_xml_request(begin, end, page_number)
            else: 
                break


    def retrieve_meta(self) -> None: 
        """
        Entry point for the class right after initialization. Keep in mind that 
        the year parameter will has to be the current year or lower, otherwise
        the script will not download anything, without any error message.
        """
        # helper function, returns last day given month of given year
        def get_days_in_month(year:int, month:int) -> int:
            _, num_days = calendar.monthrange(int(year), month)
            return num_days
        
        # date_range is list of tuple of first and last day of every month of 
        # the given year as string YYYY-MM-DD
        date_range = [(f"{self.year}-{month:02d}-01", f"{self.year}-{month:02d}-{get_days_in_month(self.year, month)}") for month in range(1, 13)]
        
        for begin, end in date_range:
            self.download_full_month(begin, end)

        logging.info(f"Finished downloading metadata for {self.branch} / {self.year}.")


if __name__ == "__main__": 
    init_script()
    
    meta_loader = Meta_Data_Collection()
    link_loader = Link_Collection()
    downloader = Decision_Downloader()
    converter = Decision_Json_Converter()
    
    meta_loader.retrieve_meta()
    link_loader.retrieve_links()
    downloader.download_decisions()
    converter.convert_all()
