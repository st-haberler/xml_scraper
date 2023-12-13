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
    dev_annotations: list[Annotation]
    # other_anns: list[Annotation]


@dataclass
class AnnotatedParagraph: 
    paragraph: str
    annotation_container: AnnotationContainer

@dataclass
class DB_entry: 
    """A single document in the database"""
    document_id: str
    document_body: list[AnnotatedParagraph]

    
    @classmethod
    def get_DB_entry_from_html_decision(cls, html_decision:Path) -> "DB_entry":
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
      
        new_entry = DB_entry(document_id=decision_id, 
                             document_body=[AnnotatedParagraph(para, 
                                                               AnnotationContainer(dev_annotations=[])) for para in paragraph_list])
        
        # TODO (maybe) replace /xa0 with whitespace
        return new_entry
  


class DBFile:
    """The actual json file for one year and one branch OR one other source.
    - DB_entries: List of Document objects
        - Document object: 
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
                                 start and end are token indices per paragraph
                        - other annotations (e.g. from other annotators or epochs)
    """
    
    def convert_decisions_full_year(self, year:int, branch:str): 
        """Converts all decisions for one year and one branch into the DB format"""

        html_path = Path.cwd() / "data" / "judikatur" / branch / f"html_{year}"
        
        entry_list = []
        for html_file in html_path.glob("*.html"):
            new_entry = DB_entry.get_DB_entry_from_html_decision(html_file)
            entry_list.append(new_entry)
            break

        db_file = Path.cwd() / "data" / "judikatur" / branch / "json_database" / f"db_{year}.json"
        db_file.parent.mkdir(parents=True, exist_ok=True)
        db_file.write_text(json.dumps([asdict(entry) for entry in entry_list], indent=4), encoding="utf-8")

    def get_decision_entry(self, year:int, branch:str): 
        db_file = Path.cwd() / "data" / "judikatur" / branch / "json_database" / f"db_{year}.json"
        data = json.loads(db_file.read_text(encoding="utf-8"))

        return data


if __name__ == "__main__":
    test = DBFile()
    # test.convert_decisions_full_year(2022, "vfgh")
    entry = test.get_decision_entry(2022, "vfgh")

    for p in entry[0]["document_body"]:
        print(p["paragraph"])
        # print(p["annotation_container"]["dev_annotations"])
        print("------")
    
    pass
    # html_file = Path(r".\data\judikatur\vfgh\html_2022\JFT_20220223_21V00315_00.html") 
    # new_entry = DB_entry.get_DB_entry_from_html_decision(html_file)

    # show_json = asdict(new_entry)
    # print(json.loads(json.dumps(show_json, indent=4)))




    # ann_1 = Annotation(1, 2, "label1")
    # ann_2 = Annotation(3, 4, "label2")
    # ann_3 = Annotation(5, 6, "label3")
    # ann_4 = Annotation(7, 8, "label4")

    # annotation_container1 = AnnotationContainer(dev_annotation=[ann_1, ann_2], other_ann=[ann_3])
    # annotation_container2 = AnnotationContainer(dev_annotation=[ann_4], other_ann=[])
    
    # para1 = AnnotatedParagraph("a", annotation_container1)
    # para2 = AnnotatedParagraph("b", annotation_container2)
    # dbe = DB_entry(document_id="test", document_body=[para1, para2])
    
    # dbe_json = asdict(dbe)
    # print(json.dumps(dbe_json, indent=4))