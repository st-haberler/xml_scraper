import argparse
import datetime
from pathlib import Path
import requests
from typing import NoReturn
import xml.etree.ElementTree as ET

from zeep import Client



RIS_API_WSDL = "https://data.bka.gv.at/ris/ogd/v2.6/?WSDL"




class CLParser(argparse.ArgumentParser):
    def __init__(self):
        super().__init__()
        self.add_arguments()
        self.extract_args()

    def add_arguments(self):
        self.add_argument("--branch", type=str, choices=["vfgh", "vwgh", "justiz"], required=True)
        self.add_argument("--year", type=str, choices=[str(i) for i in range(1946, datetime.datetime.now().year + 1)], required=True)

    def extract_args(self):
        args = self.parse_args()
        self.year = str(args.year)
        self.branch = args.branch
   
    def error(self, message:str) -> NoReturn:
        message = f"Invalid arguments.\nUsage: python scraper.py --branch [vfgh|vwgh|justiz] --year [1946-{datetime.datetime.now().year}]"
        return self.exit(2, message)

class MetaLoader:
    """Loads meta data from RIS API to meta_data property."""

    def __init__(self, branch:str, year:str):
        self.branch = branch
        self.year = year

    def generate_date_range(self) -> tuple[str, str]:
        """Generates begin and end date for RIS API request."""

        begin_date = f"{self.year}-01-01"
        
        if self.year == str(datetime.datetime.now().year):
            end_date = datetime.datetime.now().strftime("%Y-%m-%d")
        else:
            end_date = f"{self.year}-12-31"

        return (begin_date, end_date)

    def get_template_path(self) -> Path:
        """Returns path to XML template file."""

        match self.branch:
            case "vfgh":
                template_path = Path(r"C:\Users\HaberS\dev\Scraper\xml\requests\vfgh_month_query.xml")
            case "vwgh":
                template_path = Path(__file__).parent / "template_vwgh.xml"
            case "justiz":
                template_path = Path(__file__).parent / "template.xml"

        return template_path
        

    def get_xml_request(self, page_number:int) -> str:
        """Generates XML request for RIS API based on template file. Returns XML string.
        
        See https://data.bka.gv.at/ris/ogd/v2.6/Documents/Dokumentation_OGD-RIS_Service.pdf
        for the API documentation."""

        begin_date, end_date = self.generate_date_range()
        print(f"genereating xml request from {begin_date} to {end_date}")

        try: 
            template_file = ET.parse(self.get_template_path())
        except Exception as e: 
            print(e)
            return None
        
        template_root = template_file.getroot()
        
        template_begin_element = template_root.find(".//{http://ris.bka.gv.at/ogd/V2_6}EntscheidungsdatumVon") 
        template_end_element = template_root.find(".//{http://ris.bka.gv.at/ogd/V2_6}EntscheidungsdatumBis")
        template_page_element = template_root.find(".//{http://ris.bka.gv.at/ogd/V2_6}Seitennummer")

        template_begin_element.text = begin_date
        template_end_element.text = end_date
        template_page_element.text = str(page_number)

        ET.register_namespace("", "http://ris.bka.gv.at/ogd/V2_6")
        xml_request = ET.tostring(template_root, encoding="utf-8").decode("utf-8")
        return xml_request



    def send_xml_request(self, xml_request:str) -> str:
        """Sends XML request to RIS API and returns response."""
        return "abs"

        try: 
            client = Client(RIS_API_WSDL)
        except Exception as e:
            print(e)
            return None
        
        try: 
            response = client.service.SearchDocumentsXml(xml_request)
        except Exception as e:
            print(e)
            return None

        return response
        


    def extract_meta_data(self, response:str) -> list[dict]:
        """Extracts meta data from XML response and returns a list of dicts."""

        response_root = ET.fromstring(response)
        doc_reference_elements = response_root.findall(".//{http://ris.bka.gv.at/ogd/V2_6}OgdDocumentReference")

        new_root = ET.Element("root")
        for element in doc_reference_elements:
            new_root.append(element)
        new_tree = ET.ElementTree(new_root)

        return new_tree
    

    
    def load_meta_data(self):
        print(f"Loading meta data for {self.branch} from {self.year}...")

        page_number = 1 
        meta_data = ET.Element("meta_data")

        while True:
            print(f"Loading page {page_number}...")

            xml_request = self.get_xml_request(page_number)
            response = self.send_xml_request(xml_request)
            response_meta_data = self.extract_meta_data(response)
            
            meta_data.append(ET.fromstring(response_meta_data))
            
            # for dev: only load first page
            break

            if self.get_hits(response) > page_number * self.get_page_size(response):
                page_number += 1
            else: 
                break
            
        return meta_data



if __name__ == "__main__":
    cl_parser = CLParser() 
    meta_loader = MetaLoader(cl_parser.branch, cl_parser.year)
    meta_loader.load_meta_data()