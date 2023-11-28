import logging
import xml.etree.ElementTree as ET


NAMESPACE = {'ogd': 'http://ris.bka.gv.at/ogd/V2_6'}



class LinkExtractor:
    """Extracts links from a given XML-Metadata collection file or 
    from a list of xml-Elements with the same data.
    """

    def __init__(self):
        pass 



    def _is_decision(self, meta_element:ET.Element) -> bool:
        """Checks if a given xml-Element is a decision.
        Returns True if it is, False otherwise."""
        
        if meta_element.find("ogd:ContentType", namespaces=NAMESPACE).text == "MainDocument" and meta_element.find("ogd:Name", namespaces=NAMESPACE).text == "Hauptdokument":            
            return True
        else:
            return False



    def _extract_links(self, xml_meta_data:list[ET.Element]) -> list[str]:
        """Extracts links from a given list of xml-Elements with the same data.
        Returns a list of links."""

        decisions_xml = filter(self._is_decision, xml_meta_data)

        links = []

        for doc_reference in decisions_xml:
            try: 
                urls_element = doc_reference.find("ogd:Urls", namespaces=NAMESPACE)
                for content_url in urls_element:
                    if content_url.find("ogd:DataType", namespaces=NAMESPACE).text == "Html":
                        new_link = content_url.find("ogd:Url", namespaces=NAMESPACE).text
                        links.append(new_link)
            except AttributeError as e:
                logging.error(f"Could not extract link from meta_data xml.", exc_info=True)
                continue  

        return links  
