import datetime
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

from zeep import Client


PAGE_SIZE = 100
RIS_API_WSDL = "https://data.bka.gv.at/ris/ogd/v2.6/?WSDL"
TEMPLATE_VFGH = Path(r"vfgh_query.xml")
TEMPLATE_VWGH = Path(r"vwgh_query.xml")
TEMPLATE_JUSTIZ = Path(r"justiz_query.xml")
TEMPLATE_PATH = Path.cwd() / "xml" / "request_templates" 

DATA_PATH = Path.cwd() / "data" / "judikatur" 


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
                return TEMPLATE_PATH / TEMPLATE_VFGH
            case "vwgh":
                return TEMPLATE_PATH / TEMPLATE_VWGH
            case "justiz":
                return TEMPLATE_PATH / TEMPLATE_JUSTIZ
            case _:
                raise ValueError("Invalid branch argument. Must be one of 'vfgh', 'vwgh' or 'justiz'.")



    def get_hits(self, response:str) -> int:
        """Returns number of hits from XML response."""

        response_root = ET.fromstring(response)
        hits_element = response_root.find(".//{http://ris.bka.gv.at/ogd/V2_6}Hits")
        return int(hits_element.text)
        


    def get_page_size(self) -> int:
        
        return PAGE_SIZE



    def get_meta_data_file(self) -> Path:
        """Returns path to data directory."""

        return DATA_PATH / self.branch / "meta_data" / f"{self.branch}_meta_collection_all_{self.year}.xml"
    

    
    def get_xml_request(self, page_number:int=1) -> str:
        """Generates XML request for RIS API based on template file. Returns XML string.
        
        See https://data.bka.gv.at/ris/ogd/v2.6/Documents/Dokumentation_OGD-RIS_Service.pdf
        for the API documentation."""

        begin_date, end_date = self.generate_date_range()
        print(f"generating xml request from {begin_date} to {end_date}")

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
        


    def extract_meta_data(self, response:str) -> list[ET.Element]:
        """Extracts meta data from XML response and returns a list of dicts."""

        response_root = ET.fromstring(response)
        doc_reference_elements = response_root.findall(".//{http://ris.bka.gv.at/ogd/V2_6}OgdDocumentReference")
        
        return doc_reference_elements

        

    
    def load_meta_data(self) -> list[ET.Element]:
        print(f"Loading meta data for {self.branch} from {self.year}...")

        page_number = 1 
        meta_data = []

        while True:
            print(f"Loading page {page_number}...")

            xml_request = self.get_xml_request(page_number)
            response = self.send_xml_request(xml_request)
            response_meta_data = self.extract_meta_data(response)
            
            meta_data += response_meta_data
            

            if self.get_hits(response) > page_number * self.get_page_size():
                page_number += 1
            else: 
                break
            
        return meta_data
    


    def save_meta_data(self, meta_data:list[ET.Element]) -> None:
        
        pass


if __name__ == "__main__":
    test = MetaLoader("vfgh", 2021)
    test.load_meta_data()