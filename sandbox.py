from dataclasses import dataclass, field, asdict
import json


@dataclass
class AnnotatedParagraph: 
    paragraph: str
    annotation_container: dict

@dataclass
class Document: 
    """A single document in the database"""
    doc_id: str
    doc_body: int = field(init=False)
    doc_ann2: list[AnnotatedParagraph] = field(default_factory=lambda : [AnnotatedParagraph("a", {"b": 1})])

    def __post_init__(self):
        self.doc_body = 99

    @classmethod
    def doc_factory(cls) -> "Document": 
        return Document("doc_id")


    def to_json(self):
        return json.dumps(self.__dict__, indent=4)

d = Document.doc_factory()
doc_dict = asdict(d)
print(json.dumps(doc_dict, indent=4))