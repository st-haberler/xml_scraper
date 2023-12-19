from dataclasses import dataclass, asdict

import spacy

import doc_db

@dataclass
class AnnotatedTokens:
    tokenized_text: list[str]
    annotations: list[doc_db.Annotation]


@dataclass
class TokenFrame(): 
    meta_data: doc_db.DBQuery
    body: list[AnnotatedTokens]


class DocumentHandler: 
    # TODO: move get_token_frame function into doc_db.BDocument class 

    def __init__(self) -> None:
        self.database = doc_db.DBCollection()        
        
    
    def get_token_frame(self, query:doc_db.DBQuery) -> TokenFrame:
        """Returns a token frame from database for a given query."""
        nlp = spacy.load("de_core_news_sm")

        db_document = self.database.get_entry_from_query(query)

        new_token_frame = TokenFrame(
            meta_data=query,
            body=[]
        )

        for annotated_paragraph in db_document.document_body:
            spacy_doc = nlp(annotated_paragraph.text)
            new_annotated_tokens = AnnotatedTokens(
                tokenized_text=[token.text_with_ws for token in spacy_doc],
                annotations=annotated_paragraph.annotations
            )
            new_token_frame.body.append(new_annotated_tokens)

        return new_token_frame


    def get_token_frame_as_json(self, query:doc_db.DBQuery) -> dict:
        """Returns a token frame from database for a given query as json."""
        token_frame = self.get_token_frame(query)
        return asdict(token_frame)
    

    def save_token_frame_to_db(self, token_frame:TokenFrame) -> None:
        """Saves a token frame to the database (actually, it updates the
        annotations of the document in the database)."""
        self.database.
        
        pass

if __name__ == "__main__":
    d = DocumentHandler()
    q = doc_db.DBQuery(
        source_type="PHG",
        index=0,
        annotation_version=1
    )
    t = d.get_token_frame(q)

    for token in t.body[0].tokenized_text: print(token)
    print("---------------------------------")
    for token in t.body[2].tokenized_text: print(token)
