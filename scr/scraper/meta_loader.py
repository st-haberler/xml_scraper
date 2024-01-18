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
TEMPLATE_BUNDESRECHT = Path(r"brkons_query.xml")
TEMPLATE_PATH = Path.cwd() / "xml" / "request_templates" 

DATA_PATH_JUDIKATUR = Path.cwd() / "data" / "judikatur" 
DATA_PATH_BUNDESRECHT = Path.cwd() / "data" / "bundesrecht"



class MetaInterface:
    def __init__(self) -> None:
        pass
    
    def retrieve_meta_decisions(self, source_type:str="vfgh", year:str="2023", save_meta:bool=True) -> None:
        """Orchestration method for retrieving year-wise meta data for decisions (download, extract, save)."""
        
        loader = MetaLoader(source_type, year=year, gesetzesnummer=None)
        raw_meta_data = loader.load_meta_data()

        if save_meta: 
            MetaSaver.save_meta_judikatur(meta_data=raw_meta_data, source_type=source_type, year=year)

        return raw_meta_data
    
    
    def retrieve_meta_bundesrecht(self, source_type:str="PHG", gesetzesnummer="10002864", save_meta:bool=True) -> None: 
        """Orchestration method for retrieving meta data for entire regulations (Gesetze)."""

        loader = MetaLoader(source_type, year=None, gesetzesnummer=gesetzesnummer)
        raw_meta_data = loader.load_meta_data()

        if save_meta: 
            MetaSaver.save_meta_bundesrecht(meta_data=raw_meta_data, source_type=source_type)

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
    def _get_meta_data_judikatur(cls, source_type:str="vfgh", year:str="2023") -> Path:
        """Returns path to data directory."""

        return DATA_PATH_JUDIKATUR / source_type / "meta_data" / f"{source_type}_meta_collection_all_{year}.xml"
    

    @classmethod
    def _get_meta_data_bundesrecht(cls, source_type:str="PHG") -> Path:
        """Returns path to data directory."""

        return DATA_PATH_BUNDESRECHT / source_type / "meta_data" / f"{source_type}_meta_collection.xml"
    

    @classmethod
    def save_meta_judikatur(cls, meta_data:list[ET.Element], source_type:str="vfgh", year:str="2023") -> None:
        """Saves meta data to XML file."""

        meta_data_root = ET.Element("meta_data")

        for meta_data_element in meta_data:
            meta_data_root.append(meta_data_element)

        meta_data_file = cls._get_meta_data_judikatur(source_type=source_type, year=year)
        meta_data_file.parent.mkdir(parents=True, exist_ok=True)
        ET.register_namespace("", "http://ris.bka.gv.at/ogd/V2_6")
        meta_data_tree = ET.ElementTree(meta_data_root)
        meta_data_tree.write(meta_data_file, encoding="utf-8", xml_declaration=True)

        print(f"Meta data saved to {meta_data_file}.")


    @classmethod
    def save_meta_bundesrecht(cls, meta_data:list[ET.Element], source_type:str="PHG") -> None:
        """Saves meta data to XML file."""

        meta_data_root = ET.Element("meta_data")

        for meta_data_element in meta_data:
            meta_data_root.append(meta_data_element)

        meta_data_file = cls._get_meta_data_bundesrecht(source_type=source_type)
        meta_data_file.parent.mkdir(parents=True, exist_ok=True)
        ET.register_namespace("", "http://ris.bka.gv.at/ogd/V2_6")
        meta_data_tree = ET.ElementTree(meta_data_root)
        meta_data_tree.write(meta_data_file, encoding="utf-8", xml_declaration=True)

        print(f"Meta data saved to {meta_data_file}.")


class XML_Request():

    def _get_template_path(self) -> Path:
        """Returns path to XML template file."""

        match self.source_type:
            case "vfgh":
                return TEMPLATE_PATH / TEMPLATE_VFGH
            case "vwgh":
                return TEMPLATE_PATH / TEMPLATE_VWGH
            case "justiz":
                return TEMPLATE_PATH / TEMPLATE_JUSTIZ
            case _:
                return TEMPLATE_PATH / TEMPLATE_BUNDESRECHT


    def send_xml_request(self, xml_request:str) -> str:
        """Sends XML request to RIS API and returns response."""

        try: 
            client = Client(RIS_API_WSDL)
            response = client.service.SearchDocumentsXml(xml_request)
        except Exception as e:
            print(e)
            return None

        return response


class XML_Judikatur_Request(XML_Request):
    def __init__(self, source_type:str, year:str) -> None:
        self.source_type = source_type
        self.year = year
        print("init xml judikatur request")

    
    def _generate_date_range(self) -> tuple[str, str]:
        """Generates begin and end date for decision RIS API request."""

        begin_date = f"{self.year}-01-01"

        if self.year == DatetimeWrapper.year():
            end_date = DatetimeWrapper.now()
        else:
            end_date = f"{self.year}-12-31"

        return (begin_date, end_date)


    def generate_xml_request(self, page_number:int=1) -> str:
        """Generates XML decision request for RIS API for full year based on template file. 
        Returns XML string.
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


class XML_Bundesrecht_Request(XML_Request):
    def __init__(self, source_type:str, gesetzesnummer:str) -> None:
        self.source_type = source_type
        self.gesetzesnummer = gesetzesnummer
        print("init xml Bundesrecht request")


    def generate_xml_request(self, page_number:int=1) -> str:
        """Generates XML Bundesrecht request for RIS API based on template file. 
        Returns XML string.
        See https://data.bka.gv.at/ris/ogd/v2.6/Documents/Dokumentation_OGD-RIS_Service.pdf
        for the API documentation.
        """
        print("generating xml Bundesrecht request")

        try: 
            template_file = ET.parse(self._get_template_path())
        except Exception as e: 
            print(e)
            return None
        
        template_root = template_file.getroot()
        
        template_page_element = template_root.find(".//{http://ris.bka.gv.at/ogd/V2_6}Seitennummer")
        template_page_element.text = str(page_number)

        template_gesetzesnummer_element = template_root.find(".//{http://ris.bka.gv.at/ogd/V2_6}Gesetzesnummer")
        template_gesetzesnummer_element.text = str(self.gesetzesnummer)

        ET.register_namespace("", "http://ris.bka.gv.at/ogd/V2_6")
        xml_request = ET.tostring(template_root, encoding="utf-8").decode("utf-8")
        return xml_request


class MetaLoader:
    """Loads meta data from RIS API to meta_data property."""

    def __init__(self, source_type:str, year:str=None, gesetzesnummer:str=None) -> None:
        # TODO change type of year and gesetzesnummer to int in whole module 
        self.source_type = source_type
        if (year is None) and (gesetzesnummer is None):
            raise ValueError("Either year or gesetzesnummer must be specified.")
        self.year = year
        self.gesetzesnummer = gesetzesnummer


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


    def _is_request_Bundesrecht(self) -> bool:
        # for now, its sufficient to check if year is None, because Bundesrecht is not organized by year
        return self.year is None


    def load_meta_data(self) -> list[ET.Element]:
        print(f"Loading meta data for {self.source_type} ...")

        if self._is_request_Bundesrecht():
            xml_request = XML_Bundesrecht_Request(self.source_type, self.gesetzesnummer)
        else:
            xml_request = XML_Judikatur_Request(self.source_type, self.year)
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
    interface.retrieve_meta_bundesrecht(source_type="AtomHG", gesetzesnummer="10003613", save_meta=True)
    

