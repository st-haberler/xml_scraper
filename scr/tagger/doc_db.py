from bs4 import BeautifulSoup as bs
from dataclasses import dataclass, field, asdict
import json
from pathlib import Path


@dataclass
class Annotation: 
    start: int
    end: int
    label: str


@dataclass
class AnnotationContainer: 
    dev_annotation: list[Annotation]
    other_ann: list[Annotation]


@dataclass
class AnnotatedParagraph: 
    paragraph: str
    annotation_container: AnnotationContainer

@dataclass
class DB_entry: 
    """A single document in the database"""
    document_id: str
    document_body: list[AnnotatedParagraph]

class DBFile:
    """The actual json file for one year and one branch OR one other source.
    - DB_entries: List of Document objects
        - Dcoument object
            - document_id (string)
            - document_body 
                - list of annotated paragraphs 
                    - paragraph (string) 
                    - annotation container 
                        - dev_ann
                            - list of annotations
                                - start (int)
                                - end (int)
                                - label (string)
                                # start and end are token indices per paragraph
                        - other annotations (e.g. from other annotators or epochs)
    """
    
    def get_DB_entry_from_html_decision(self, html_decision:Path) -> None:
        """Parses the html file and creates a Document object"""

        decision_id = html_decision.stem
        soup = bs(html_decision.read_text(encoding="utf-8"), "html.parser")
        
        # find the decision body: <body><div><div><h1>Begründung</h1><p>...</p><p>...</p>...
        paragraph_list = []
        for div in soup.body.div.find_all("div"): 
            # check if h1 tag exists and if it contains "Begründung"
            if div.h1 and (("Begründung" in div.h1.text)
                        or ("Text" in div.h1.text)
                        or ("Rechtliche Beurteilung" in div.h1.text)): 
                for para in div.find_all("p"):  
                    # remove tags that are not meant for written text 
                    for sr in para.find_all("span", class_="sr-only"): 
                        sr.decompose()
                    paragraph_list.append(para.text)

        decision_struct = {"doc_id": decision_id, 
                           "doc_body": paragraph_list
                           }     
        return decision_struct
  



    pass

if __name__ == "__main__":
    ann_1 = Annotation(1, 2, "label1")
    ann_2 = Annotation(3, 4, "label2")
    ann_3 = Annotation(5, 6, "label3")
    ann_4 = Annotation(7, 8, "label4")

    annotation_container1 = AnnotationContainer(dev_annotation=[ann_1, ann_2], other_ann=[ann_3])
    annotation_container2 = AnnotationContainer(dev_annotation=[ann_4], other_ann=[])
    
    para1 = AnnotatedParagraph("a", annotation_container1)
    para2 = AnnotatedParagraph("b", annotation_container2)
    dbe = DB_entry(document_id="test", document_body=[para1, para2])
    
    dbe_json = asdict(dbe)
    print(json.dumps(dbe_json, indent=4))