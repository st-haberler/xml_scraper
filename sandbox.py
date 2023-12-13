from dataclasses import asdict, fields, is_dataclass, replace, dataclass, field
from pathlib import Path
import json


@dataclass
class Annotation: 
    start: int
    end: int
    label: str


@dataclass
class AnnotatedParagraph: 
    text: str
    annotation_container: list[Annotation]

@dataclass
class Document: 
    """A single document in the database"""
    doc_id: str
    doc_ann: list[AnnotatedParagraph] = field(default_factory=lambda : [AnnotatedParagraph("Das ist der Beispielstext", [Annotation(0, 3, "ART"), Annotation(5, 7, "XXX")]), 
                                                                        AnnotatedParagraph("Das ist der zweite Beispieltext", [Annotation(1, 2, "ABC"), Annotation(3, 4, "ZZZ")])])

   



def from_dict(dataclass_type, data):
    if not is_dataclass(dataclass_type):
        raise ValueError(f"{dataclass_type} is not a dataclass")

    # Get the fields of the dataclass
    dataclass_fields = fields(dataclass_type)

    # Initialize an empty dictionary to store the field values
    field_values = {}

    # Iterate over each field
    for field in dataclass_fields:
        field_name = field.name
        field_type = field.type

        print(field_name, field_type)

        # Check if the field is a nested dataclass
        if is_dataclass(field_type):
            # Recursively call from_dict for nested dataclasses
            nested_data = data.get(field_name)
            nested_instance = from_dict(field_type, nested_data)
            field_values[field_name] = nested_instance
        elif field_type == list:
            print(str(field_type) + "is list")
        else:
            # Use the value from the dictionary if present, or use the default value
            print("else: field_name", field_name)
            field_values[field_name] = data.get(field_name)

    # Create an instance of the dataclass using dataclasses.replace
    return dataclass_type(**field_values)





d = Document("This is ID")
d_dict = asdict(d)

d2 = from_dict(Document, d_dict)
print(d2.doc_id)
for ann in d2.doc_ann: 
    print(ann.text)
    for a in ann.annotation_container: 
        print(a.start, a.end, a.label)


print(d2 == d)



