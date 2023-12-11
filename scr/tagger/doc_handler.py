"""
The data is called source. Source is organised as follows:
- source_type: gesetz, judikatur, etc.
- source_name: either name of the law or name of the court/branch (e.g. eo, vfgh, justiz, etc.)
- year: year of the document (optional and only practical for decisions)
- doc_number: number of the document within the source (mapping to a specific decision - optional and only practical for decisions)
- para_index: number of a paragraph within the source -- this unit is used as input for spacy and the tagger 

The tagger returns .ann files. Each files contains a header with the above metadata so the .ann files can be mapped to the source.
The .ann files contain the entities as received from the tagger and are saved in the same folder as their source databases. 
"""


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

class Annotation: 
    def __init__(self, annotations:list=[], meta:dict={}, cvs_path:Path=CSV_FILE_HANDLER):
        self.source_id = meta["source"] + "_" + meta["index"]
        pass 

    def json_file_exists(self, source_id:str) -> bool:
        """checks if a json file exists for the given source_id"""

        pass



class Document:
    """
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
