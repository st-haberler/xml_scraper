from dataclasses import dataclass

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
        database = doc_db.DBCollection()        
        
    
    def get_token_frame(self, query:doc_db.Query) -> TokenFrame:
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
                annotation=annotated_paragraph.annotations
            )
            new_token_frame.body.append(new_annotated_tokens)

        return new_token_frame
     

if __name__ == "__main__":
    # ----------- TEST CODE ----------------
    pass
    # ----------- END OF TEST CODE ---------
