"""
The data is called source. Source is organised as follows:
- source_type: gesetz, judikatur, etc.
- source_name: either name of the law or name of the court/branch (e.g. eo, vfgh, justiz, etc.)
- year: year of the document (optional and only practical for decisions)
- doc_number: number of the document within the source (mapping to a specific decision - optional and only practical for decisions)
- doc_id: the html filename without extension of the document. Kind of redundant but useful for mapping to the html file.
- para_index: number of a paragraph within the source -- this unit is used as input for spacy and the tagger 

For concise description of a source paragraph, the source_meta object (actually a dataclass dict) is used.

The tagger returns .ann files. Each files contains a header with the above metadata so the .ann files can be mapped to the source.
The name of the .ann file is the the doc_id with the extension .ann.
The .ann files contain the entities as received from the tagger and are saved in the same folder as their source databases. 

If at a later point different versions of annotations are needed, the .ann extension will simply get a _01 number suffix.
"""

from dataclasses import dataclass
from pathlib import Path
import json
import spacy
from spacy.tokens import Doc
from spacy.tokens import Span
from spacy.tokens import DocBin
import logging

SPACY_FILE = Path(Path.cwd() / "data" / "gesetze" / "eo" / "eo.spacy")
JSON_FILE = Path(Path.cwd() / "data" / "gesetze" / "eo" / "eo2.json")
CSV_FILE_HANDLER = Path(Path.cwd() / "data" / "file_handler.csv")

# TODO: separate Object for .ann files. This would allow to load/save .ann files without loading the whole spacy file.
# TODO: methods for loading/saving .ann files in sync with spacy file/legal source. Even better: CSV with mapping of .ann files to spacy file and source 



@dataclass
class SourceMeta:
    source_type: str = "judikatur"
    source_name: str = "vfgh"
    year: int = 2023
    doc_number: int = 0
    doc_id: str = "JFT_20230227_21E04603_00" 
    para_index: int = 0


class ProjectAnnotations: 
    """
    Class property: A list of all Labels currently used in the project. 
    This property is the single source of truth for all labels.
    """
    project_labels = ["PERSON", "AUTHORITY"]

    @classmethod
    def __refresh_project_labels(cls) -> None:
        """refreshes the project labels from the .ann files in all source folders. 
        To be invoked whenever a new .ann file is saved to disk. 
        """

        current_project_labels = set(cls.project_labels)
        for ann_file_iterator in Path(Path.cwd() / "data").rglob("*.ann"):
            iterator_content = json.loads(ann_file_iterator.read_text(encoding="utf-8"))
            for annotation in iterator_content["annotations"]:
                current_project_labels.add(annotation["label"])
        cls.project_labels = list(current_project_labels)


@dataclass
class Annotation: 
    """ 
    A single annotation. 
    """
    start: int
    end: int
    label: str
 

@dataclass
class DocumentAnnotations(ProjectAnnotations):
    entities: list = [Annotation]

     

class AnnotationFile(ProjectAnnotations): 

    def __init__(self, meta_info:SourceMeta, annotations:DocumentAnnotations):
        self.meta_info = meta_info
        self.annotations = annotations
        self.ann_data = {"meta": self.meta_info, "annotations": self.annotations}


    def __refresh_project_labels(self) -> None:
        """refreshes the project labels from the .ann files in the source folder"""
        # TODO: this method should be called whenever a new .ann file is saved to disk or loaded from disk
        # TODO remove path literal to init or config module/file 
        current_project_labels = set(ProjectAnnotations.project_labels)
        for ann_file_iterator in Path(Path.cwd() / "data" / self.meta_info.source_type / self.meta_info.source_name).glob("*.ann"):  
            iterator_content = json.loads(ann_file_iterator.read_text(encoding="utf-8"))
            for annotation in iterator_content["annotations"]:
                current_project_labels.add(annotation["label"])
        ProjectAnnotations.project_labels = list(current_project_labels)
    
    
    def get_filename(self) -> Path:
        """returns the path of the annotation file"""
        ann_file = Path(Path.cwd() / "data" / self.meta_info.source_type / self.meta_info.source_name / f"{self.meta_info.doc_id}.ann")
        return ann_file
    
    def save_to_disk(self) -> None:
        """saves the annotations to disk"""
        ann_file = self.get_filename()
        self.__refresh_project_labels()
        ann_file.write_text(json.dumps(self.ann_data, indent=4, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load_from_disk(cls, source_meta:SourceMeta) -> None:        
        
        pass
        

    def json_file_exists(self, source_id:str) -> bool:
        """checks if a json file exists for the given source_id"""

        pass






class DocumentHandler: 
    
    def get_all_labels(self) -> list:
        """returns a list of all labels currently used in the project"""
        return Annotations.project_labels
    
    def get_doc_as_token_frame(self, source_meta:dict) -> dict:
        """returns one paragraph as list of tokens with ws"""
        pass
    pass


class Document:
    """
    NEW CONCEPT: 
    - to client: token_frame
        - required: 
            - meta_info as parameter, 
            - tokenized_text: from json db, processed with spacy, 
            - entities from ann, inclusion of entities from spacy doc optional 
        - return value: 
            - token_frame: meta_info (including project ann), tokenized_text, entities 
    - from client: ann
        - meta_info including project ann
        - entities
        - tokenized_text for now not needed; maybe later for client side tokenization
    - interface for spacy
        - adding entities from ann file into spacy doc (later)
        - loading entities from spacy doc into ann file (see: to client)
    
    ====================
    - loads either from .spacy with doc/doc_bin or from .json with list of strings
    - allows export of one single 'doc as token' (list of tokens with ws).
    - the export data is a dict: meta: {"type":..., "source": ..., "index": ...}, tokenized_text: [...], entities: [(start, end, label), ...]
    - receives the modified dict json data from frontend and saves ONLY THE ENTITIES to disk as .ann file
    - planned: integration of .ann (annotation metadata) with  .spacy docs.
    """

    def __init__(
        self,
        spacy_file: Path = SPACY_FILE,
        json_file: Path = JSON_FILE,
        source_type: str = "gesetz",
        source_name: str = "eo",
        load_from_spacy: bool = False,
    ):
        logging.basicConfig(level=logging.DEBUG)

        self.nlp = spacy.load("de_core_news_sm")
        # self.nlp = spacy.blank("de")

        self.source_name = source_name
        self.source_type = source_type

        if load_from_spacy and spacy_file.exists():
            self.documents = self.load_from_spacy(spacy_file)
        else:
            self.documents = self.load_from_json(json_file)
            self.save_to_spacy(spacy_file)

        try:
            self.entity_labels = self.nlp.get_pipe("ner").labels
        except KeyError:
            self.entity_labels = []

    def get_doc_count(self, source) -> int:
        """returns the number of documents"""
        return len(self.documents)

    def get_entity_labels(self) -> list:
        """returns the list of entity labels"""
        return self.entity_labels

    def load_from_spacy(self, spacy_file: Path) -> list:
        """loads a list of paragraphs from a spacy file"""
        logging.info(f"loading paragraphs from {spacy_file}")
        doc_bin = DocBin().from_disk(spacy_file)
        documents = list(doc_bin.get_docs(self.nlp.vocab))
        return documents

    def load_from_json(self, json_file: Path) -> list:
        """loads a list of paragraphs from a json file"""
        logging.info(f"loading paragraphs from {json_file}")
        eo_json = json.loads(json_file.read_text(encoding="utf-8"))
        documents = [self.nlp(paragraph) for paragraph in eo_json[:5]]
        return documents

    def save_to_spacy(self, spacy_file: Path):
        """saves the documents to a spacy file"""
        doc_bin = DocBin(docs=self.documents)
        doc_bin.to_disk(spacy_file)
        logging.info(f"saved documents to {spacy_file}")

    def get_doc_as_token_frame(self, source: str = "eo", index: int = "0") -> list:
        """ returns one paragraph as list of tokens with ws """
        meta = {"type": self.source_type, "source": self.source_name, "index": index}
        tokenized_text = [token.text_with_ws for token in self.documents[index]]
        entities = [
            (ent.start, ent.end, ent.label_) for ent in self.documents[index].ents
        ]
        # TODO/IDEA: add ent.text to entities. This would allow easier processing of the .ann files. 


        return {"meta": meta, "tokenized_text": tokenized_text, "entities": entities}

    def save_entities_to_disk(self, entities: list, source: str, index: int):
        """
        saves the entities as received from frontend via flask_server to disk as .ann file
        """

        filename = f"{source}_{index:03}.ann"
        filepath = Path(Path.cwd() / "data" / source / filename)
        filepath.write_text(
            json.dumps(entities, indent=4, ensure_ascii=False), encoding="utf-8"
        )

    def save_all_to_disk(self, spacy_file: Path = SPACY_FILE):
        """saves the documents to a spacy file"""
        doc_bin = DocBin(docs=self.documents)
        doc_bin.to_disk(spacy_file)
        logging.info(f"saved documents to {spacy_file}")


if __name__ == "__main__":
    # ----------- TEST CODE ----------------
    pass
    # ----------- END OF TEST CODE ---------
