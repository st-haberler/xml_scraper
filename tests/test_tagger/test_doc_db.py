from pathlib import Path

import doc_db


def get_new_entry():
    html_file = Path(r".\data\judikatur\vfgh\html_2022\JFT_20220223_21V00315_00.html") 
    new_entry = doc_db.DB_entry.get_DB_entry_from_html_decision(html_file)

    assert new_entry.document_id == "JFT_20220223_21V00315_00"
    

