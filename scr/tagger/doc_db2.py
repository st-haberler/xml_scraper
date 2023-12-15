from dataclasses import dataclass, asdict
import json
from pathlib import Path

from bs4 import BeautifulSoup as bs

from utils import source_from_ecli


@dataclass
class DBQuery:
    source_type: str
    index: int
    year: int
    annotation_version: int


@dataclass
class Annotation: 
    start: int
    end: int
    label: str


@dataclass
class AnnotatedParagraph:
    text: str
    annotations: list[list[Annotation]]


@dataclass
class DBDocument: 
    document_id: str
    document_body: list[AnnotatedParagraph]
    

class DBCollection: 
    def __init__(self, db_path:Path=None) -> None:
        if db_path is None:
            self.db_path = Path.cwd() / "data" 
        else:
            self.db_path = db_path

        # set all path constants for Bundesrecht, Judikatur etc 


    def get_entry(self, query): 
        """Returns a DB_Document object including all annotations from the database."""
        # TODO check if index is within range of available documents

        if query.year: 
            filepath = self.db_path / "judikatur" / query.source_type / str(query.year) / "json"
        else:
            filepath = self.db_path / "judikatur" / query.source_type / "json"
        
        for file_index, json_file in enumerate(filepath.glob("*.json")):
            if file_index == query.index: 
                json_data = json.loads(json_file.read_text(encoding="utf-8"))
        
                return DBDocument.from_db_dict(json_data)


    def add_html_bundesrecht(self, html_bundesrecht:Path):
        # TODO: implement scraper first 
        soup = bs(html_bundesrecht.read_text(), "html.parser")

        document_id = html_bundesrecht.stem

        # get source_type from the "grandparent" directory name, for lack of a better idea
        source_type = html_bundesrecht.parent.parent.stem


        paragraph_text_list = []
        for div in soup.body.find_all("div"):
            if div.h1 and ("Text" in div.h1.text):  
                for para in div.find_all(["p", "ol", "ul"]):  
                    # remove tags that are not meant for written text 
                    for sr in para.find_all("span", class_="sr-only"): 
                        sr.decompose()
                    paragraph_text_list.append(para.text)

        document_body = [AnnotatedParagraph(text=para, annotations=[]) for para in paragraph_text_list]
        new_document = DBDocument(document_id=document_id, document_body=document_body)

        new_file = self.db_path / "bundesrecht" / source_type / "json" / f"{document_id}.json"
        new_file.parent.mkdir(parents=True, exist_ok=True)
        new_file.write_text(json.dumps(asdict(new_document), indent=4), encoding="utf-8")

    
    def add_html_decision(self, html_decision:Path):
        soup = bs(html_decision.read_text(encoding="utf-8"), "html.parser")

        # we presume that the file name is the technical document number as per RIS standard
        document_id = html_decision.stem

        # get source_type from ECLI identifier: 
        # ECLI identifier is usually in a <p> tag right after the
        # <h1>European Case Law Identifier</h1> tag
        ecli = None
        for h1 in soup.body.find_all("h1"):
            if h1.text == "European Case Law Identifier": 
                ecli = h1.find_next("p").text
                break
        if ecli is None:
            raise ValueError("No ECLI identifier found, cannot add decision to database")
            # TODO add unfinished json to unfinished folder for manual completion
        source_type = source_from_ecli(ecli)

        # find the decision year: 
        # decision date is usually in a <p> tag right after <h1>Entscheidungsdatum</h1> tag
        # the year is the last 4 characters of the date
        year = None
        for h1 in soup.body.find_all("h1"):
            if h1.text == "Entscheidungsdatum": 
                year = h1.find_next("p").text[-4:]
                break
        if year is None:
            raise ValueError("No year found, cannot add decision to database")
            # TODO add unfinished json to unfinished folder for manual completion

        # find the decision body: 
        # <body><div><div><h1>Begründung</h1><p>...</p><p>...</p>...
        paragraph_text_list = []
        for div in soup.body.div.find_all("div"): 
            # check if h1 tag exists and if it contains "Begründung"
            if div.h1 and (("Begründung" in div.h1.text)
                        or ("Text" in div.h1.text)
                        or ("Rechtliche Beurteilung" in div.h1.text)): 
                for para in div.find_all("p"):  
                    # remove tags that are not meant for written text 
                    for sr in para.find_all("span", class_="sr-only"): 
                        sr.decompose()
                    paragraph_text_list.append(para.text)

        # create the DBDocument object
        document_body = [AnnotatedParagraph(text=para, annotations=[]) for para in paragraph_text_list]
        new_document = DBDocument(document_id=document_id, document_body=document_body)

        # add the document to the database
        new_file = self.db_path / source_type / str(year) / f"{document_id}.json"
        new_file.parent.mkdir(parents=True, exist_ok=True)
        new_file.write_text(json.dumps(asdict(new_document), indent=4), encoding="utf-8")

        


if __name__ == "__main__": 
    html = Path.cwd() / "data/bundesrecht/PHG/html/NOR12034518.html"
    db = DBCollection()
    db.add_html_bundesrecht(html)

