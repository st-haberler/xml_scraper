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


class MetaInterface:
    def __init__(self) -> None:
        pass
    
    def retrieve_meta_data(self, branch:str="vfgh", year:str="2023", save_meta:bool=True) -> None:
        """Orchestration method for retrieving meta data (download, extract, save)."""
        
        loader = MetaLoader(branch, year)
        raw_meta_data = loader.load_meta_data()

        if save_meta: 
            MetaSaver.save_meta_data(raw_meta_data, branch, year)

        return raw_meta_data

        
class DatetimeWrapper: 
    @classmethod
    def now(cls) -> str:
        return datetime.datetime.now().strftime("%Y-%m-%d")
    
    @classmethod
    def year(cls) -> str:
        return str(datetime.datetime.now().year)
        

class MetaSaver:
    """Saves meta data to one XML file."""

    @classmethod
    def _get_meta_data_file(cls, branch:str="vfgh", year:str="2023") -> Path:
        """Returns path to data directory."""

        return DATA_PATH / branch / "meta_data" / f"{branch}_meta_collection_all_{year}.xml"
    

    @classmethod
    def save_meta_data(cls, meta_data:list[ET.Element], branch:str="vfgh", year:str="2023") -> None:
        """Saves meta data to XML file."""

        meta_data_root = ET.Element("meta_data")

        for meta_data_element in meta_data:
            meta_data_root.append(meta_data_element)

        meta_data_file = cls._get_meta_data_file(branch=branch, year=year)
        ET.register_namespace("", "http://ris.bka.gv.at/ogd/V2_6")
        meta_data_tree = ET.ElementTree(meta_data_root)
        meta_data_tree.write(meta_data_file, encoding="utf-8", xml_declaration=True)

        print(f"Meta data saved to {meta_data_file}.")


class XML_Request():

    def __init__(self, branch:str, year:str) -> None:
        self.branch = branch
        self.year = year


    def _get_template_path(self) -> Path:
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


    def _generate_date_range(self) -> tuple[str, str]:
        """Generates begin and end date for RIS API request."""

        begin_date = f"{self.year}-01-01"

        if self.year == DatetimeWrapper.year():
            end_date = DatetimeWrapper.now()
        else:
            end_date = f"{self.year}-12-31"

        return (begin_date, end_date)


    def generate_xml_request(self, page_number:int=1) -> str:
        """Generates XML request for RIS API based on template file. Returns XML string.
        
        See https://data.bka.gv.at/ris/ogd/v2.6/Documents/Dokumentation_OGD-RIS_Service.pdf
        for the API documentation.
        """
        
        begin_date, end_date = self._generate_date_range()
        print(f"generating xml request from {begin_date} to {end_date}")

        try: 
            template_file = ET.parse(self._get_template_path())
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
            response = client.service.SearchDocumentsXml(xml_request)
        except Exception as e:
            print(e)
            return None

        return response



class MetaLoader:
    """Loads meta data from RIS API to meta_data property."""

    def __init__(self, branch:str, year:str):
        self.branch = branch
        self.year = year

        # self.meta_data_file = self._get_meta_data_file()


    def _get_hits(self, response:str) -> int:
        """Returns number of hits from XML response."""

        response_root = ET.fromstring(response)
        hits_element = response_root.find(".//{http://ris.bka.gv.at/ogd/V2_6}Hits")
        return int(hits_element.text)     


    def _get_page_size(self) -> int:
        
        return PAGE_SIZE
   

    def _extract_meta_data(self, response:str) -> list[ET.Element]:
        """Extracts meta data from XML response and returns a list of dicts."""

        response_root = ET.fromstring(response)
        doc_reference_elements = response_root.findall(".//{http://ris.bka.gv.at/ogd/V2_6}OgdDocumentReference")
        
        return doc_reference_elements


    def load_meta_data(self) -> list[ET.Element]:
        print(f"Loading meta data for {self.branch} from {self.year}...")

        xml_request = XML_Request(self.branch, self.year)
        page_number = 1 
        meta_data = []

        while True:
            print(f"Loading page {page_number}...")

            request = xml_request.generate_xml_request(page_number)
            response = xml_request.send_xml_request(request)

            response_meta_data = self._extract_meta_data(response)
            meta_data += response_meta_data
            
            if self._get_hits(response) > page_number * self._get_page_size():
                page_number += 1
            else: 
                break

        print(f"Loaded {len(meta_data)} meta data entries ({page_number} pages).")
            
        return meta_data
    


if __name__ == "__main__":
    interface = MetaInterface()
    interface.retrieve_meta_data(branch="vfgh", year="2023", save_meta=True)
    

