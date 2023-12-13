from bs4 import BeautifulSoup as bs
from dataclasses import dataclass, field, fields, asdict, is_dataclass, replace 
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
    text: str
    annotation_container: AnnotationContainer

@dataclass
class DB_entry: 
    """A single document in the database (one decision, one paragraph of a regulation etc.). Maps to the RIS database documents. 
    - DB_entries: List of Document objects
        - Document object: 
            - document_id (string, 'technische Dokumentnummer' lt RIS) 
            - document_source_type (string, e.g. 'vfgh', 'justiz', 'norm' etc.)
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
    document_id: str
    document_source_type: str
    document_body: list[AnnotatedParagraph]

    
    @classmethod
    def get_DB_entry_from_html_decision(cls, html_decision:Path, document_source_type:str) -> "DB_entry":
        """Parses the html file and creates a Document object. 
        Make sure that source type is correct.
        """

        document_id = html_decision.stem

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
      
        new_entry = DB_entry(document_id=document_id, 
                             document_source_type=document_source_type,
                             document_body=[AnnotatedParagraph(para, 
                                                               AnnotationContainer(dev_annotations=[])) for para in paragraph_list])
        
        # TODO (maybe) replace /xa0 with whitespace
        return new_entry
  


class DBFile:
    """The actual json file for one year and one branch OR one other source (gesetz etc.).
    """
    # TODO create two classes, one for decisions, one for norms that inherit from this class
    # TODO make clean mapping functions for json database to DB_entry class conversion on load and save 


    def __init__(self, year:int=None, source_type:str=None, db_file:Path=None):
        if year: 
            self.year = year
        if db_file: 
            self.db_file = db_file  

        raw_data = json.loads(self.db_file.read_text(encoding="utf-8"))   
        
        self.db_data = [DB_entry(**entry) for entry in raw_data]


 
        

    

    def convert_decisions_full_year(self): 
        """Converts all decisions for one year and one branch into the DB format"""
        if not self.year:
            raise ValueError("No year specified or source does not support year")

        html_path = Path.cwd() / "data" / "judikatur" / self.document_source_type / f"html_{self.year}"
        
        entry_list = []
        for html_file in html_path.glob("*.html"):
            new_entry = DB_entry.get_DB_entry_from_html_decision(html_file, document_source_type=self.document_source_type)
            entry_list.append(new_entry)
            break # remove later: only convert one file for testing purposes

        db_file = Path.cwd() / "data" / "judikatur" / self.document_source_type / "json_database" / f"db_{self.year}.json"
        db_file.parent.mkdir(parents=True, exist_ok=True)
        db_file.write_text(json.dumps([asdict(entry) for entry in entry_list], indent=4), encoding="utf-8")



    def get_decision_entry(self, index:int) -> DB_entry: 
        db_file = Path.cwd() / "data" / "judikatur" / self.document_source_type / "json_database" / f"db_{self.year}.json"
        data = json.loads(db_file.read_text(encoding="utf-8"))

        if index < len(data): 
            return DB_entry(**data[index])
             
        else:
            raise IndexError(f"Index {index} is out of range for {db_file}")
        
    
    def save_decision_entry(self, new_entry:DB_entry, index:int=None): 
        if new_entry.document_source_type != self.document_source_type: 
            raise ValueError(f"Source type of entry ({new_entry.document_source_type}) does not match source_type argument ({self.document_source_type}) of DBFile object")
        
        db_data = json.loads(self.db_file.read_text(encoding="utf-8"))
        for entry in db_data: 
            if entry["document_id"] == new_entry.document_id: 
                entry = asdict(new_entry)
                self.db_file.write_text(json.dumps(db_data, indent=4), encoding="utf-8")
                return 
        
        raise ValueError(f"Entry with document_id {new_entry.document_id} not found in {self.db_file}")





if __name__ == "__main__":
    db = DBFile(2022, "vfgh", Path.cwd() / "data" / "judikatur" / "vfgh" / "json_database" / "db_2022.json")
    

    # test.convert_decisions_full_year(2022, "vfgh")
   

    
    
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