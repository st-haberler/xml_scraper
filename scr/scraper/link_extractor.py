import logging
from pathlib import Path
import xml.etree.ElementTree as ET


NAMESPACE = {'ogd': 'http://ris.bka.gv.at/ogd/V2_6'}
CONTENT_REFERENCE_ELEMENT = "ogd:OgdDocumentReference/ogd:Data/ogd:Dokumentliste/ogd:ContentReference"

DATA_PATH_JUDIKATUR = Path.cwd() / "data" / "judikatur"
DATA_PATH_BUNDESRECHT = Path.cwd() / "data" / "bundesrecht"
META_PATH = "meta_data"

logging.basicConfig(level=logging.INFO)


class LinkExtractor:
    """Extracts links from a given XML-Metadata collection file or 
    from a list of xml-Elements with the same data.
    """

    def __init__(self):
        pass 


    def _get_root_from_source(self, source:Path) -> ET.Element:
        """Returns the root element of a given XML-Metadata collection file."""

        tree = ET.parse(source)
        root = tree.getroot()

        return root


    def _is_legal_document(self, meta_element:ET.Element) -> bool:
        """An XML-tag is a legal document if the tag <ContentType> contains "MainDocument"
        and the tag <Name> containts "Hauptdokument". As per RIS standard."""

        if meta_element.find("ogd:ContentType", namespaces=NAMESPACE).text == "MainDocument" and meta_element.find("ogd:Name", namespaces=NAMESPACE).text == "Hauptdokument":            
            return True
        else:
            return False



    def _get_filtered_content_references(self, source:Path) -> list[ET.Element]:
        """Finds all content references in a given XML-Metadata collection file.
        Filters out references that are not decisions. Returns filters list.
        """
        
        root = self._get_root_from_source(source)

        content_references = root.findall(f".//{CONTENT_REFERENCE_ELEMENT}", namespaces=NAMESPACE)
        content_references = filter(self._is_legal_document, content_references)

        return content_references
    

    def _get_link_from_reference(self, reference:ET.Element) -> str:
        urls_element = reference.find("ogd:Urls", namespaces=NAMESPACE)
        for content_url in urls_element:
            if content_url.find("ogd:DataType", namespaces=NAMESPACE).text == "Html":
                new_link = content_url.find("ogd:Url", namespaces=NAMESPACE).text
                return new_link
       

    def _save_links_to_file(self, links:list[str], year:str, branch:str) -> None:
        """Saves a list of links to a file."""

        link_file = DATA_PATH_JUDIKATUR / branch / META_PATH / f"{branch}_all decision_links_{year}.links"
        
        with open(link_file, "w") as f:
            for link in links:
                f.write(link + "\n")


    def _save_bundesrecht_links_to_file(self, links:list[str], source_type:str) -> None:
        """Saves a list of links to a file."""

        link_file = DATA_PATH_BUNDESRECHT / source_type / META_PATH / f"{source_type}.links"
        
        with open(link_file, "w") as f:
            for link in links:
                f.write(link + "\n")



    def get_bundesrecht_links(self, source_type:str, meta_collection:Path=None, todisk:bool=False) -> list[str]:
        if meta_collection is None:
            meta_collection = DATA_PATH_BUNDESRECHT / source_type / META_PATH / f"{source_type}_meta_collection.xml"

        content_references = self._get_filtered_content_references(meta_collection)

        links = []
        for reference in content_references:
            try:
                links.append(self._get_link_from_reference(reference))
            except AttributeError as e:
                logging.error(f"Could not extract link from meta_data.", exc_info=True)
                continue

        if todisk:
            self._save_bundesrecht_links_to_file(links, source_type)
            logging.info(f"Links saved to {DATA_PATH_BUNDESRECHT / source_type / META_PATH / f'{source_type}.links'}.")

        return links
    

    def get_decision_links(self, year:str, branch:str, source:Path=None, todisk:bool=False) -> list[str]:
        """Extracts links from a given XML-Metadata collection file or 
        from a list of xml-Elements with the same data.
        Returns a list of links.
        """

        if source is None:
            source = DATA_PATH_JUDIKATUR / branch / META_PATH / f"{branch}_meta_collection_all_{year}.xml"

        content_references = self._get_filtered_content_references(source)

        links = []
        for reference in content_references:
            try:
                links.append(self._get_link_from_reference(reference))
            except AttributeError as e:
                logging.error(f"Could not extract link from meta_data.", exc_info=True)
                continue  

        if todisk:
            self._save_links_to_file(links, year, branch)
            logging.info(f"Links saved to {DATA_PATH_JUDIKATUR / branch / META_PATH / f'{branch}_all decision_links_{year}.links'}.")
        return links


if __name__ == "__main__": 
    le = LinkExtractor()
    le.get_bundesrecht_links("PHG", todisk=True)