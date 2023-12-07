import logging
from pathlib import Path
import xml.etree.ElementTree as ET


NAMESPACE = {'ogd': 'http://ris.bka.gv.at/ogd/V2_6'}
CONTENT_REFERENCE_ELEMENT = "ogd:OgdDocumentReference/ogd:Data/ogd:Dokumentliste/ogd:ContentReference"

DATA_PATH = Path.cwd() / "data" / "judikatur"


class LinkExtractor:
    """Extracts links from a given XML-Metadata collection file or 
    from a list of xml-Elements with the same data.
    """

    def __init__(self):
        pass 


    def _get_root_from_source(self, source:str) -> ET.Element:
        """Returns the root element of a given XML-Metadata collection file."""

        tree = ET.parse(source)
        root = tree.getroot()

        return root


    def _is_decision(self, meta_element:ET.Element) -> bool:
        """An XML is a decision if the tag <ContentType> contains "MainDocument"
        and the tag <Name> containts "Hauptdokument". That's the way it is."""

        if meta_element.find("ogd:ContentType", namespaces=NAMESPACE).text == "MainDocument" and meta_element.find("ogd:Name", namespaces=NAMESPACE).text == "Hauptdokument":            
            return True
        else:
            return False



    def _get_filtered_content_references(self, source:str) -> list[ET.Element]:
        """Finds all content references in a given XML-Metadata collection file.
        Filters out references that are not decisions. Returns filters list.
        """
        
        root = self._get_root_from_source(source)

        content_references = root.findall(f".//{CONTENT_REFERENCE_ELEMENT}", namespaces=NAMESPACE)
        content_references = filter(self._is_decision, content_references)

        return content_references
    

    def _get_link_from_reference(self, reference:ET.Element) -> str:
        urls_element = reference.find("ogd:Urls", namespaces=NAMESPACE)
        for content_url in urls_element:
            if content_url.find("ogd:DataType", namespaces=NAMESPACE).text == "Html":
                new_link = content_url.find("ogd:Url", namespaces=NAMESPACE).text
                return new_link
       

    def _save_links_to_file(self, links:list[str], year:str, branch:str) -> None:
        """Saves a list of links to a file."""

        with open(f"links_{branch}_{year}.txt", "w") as f:
            for link in links:
                f.write(link + "\n")


    def get_links(self, source:str, todisk:bool=False, year:str="2022", branch:str="vfgh") -> list[str]:
        """Extracts links from a given XML-Metadata collection file or 
        from a list of xml-Elements with the same data.
        Returns a list of links.
        """

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

        return links
