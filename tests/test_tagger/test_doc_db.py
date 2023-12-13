from pathlib import Path

import doc_db


class TestDB_entry: 

    def test_get_DB_entry_from_html_decision(self):
        html_file = Path(r".\tests\test_tagger\test_data\JFT_20220223_21V00315_00.html") 
        new_entry = doc_db.DB_entry.get_DB_entry_from_html_decision(html_file, "vfgh")
        
        assert new_entry.document_id == "JFT_20220223_21V00315_00"
        assert new_entry.document_source_type == "vfgh"
        assert new_entry.document_body[0].paragraph == "Begr\u00fcndung"
        assert new_entry.document_body[2].paragraph == "Gest\u00fctzt auf Art139 Abs1 B-VG begehrt die Antragstellerin mit ihrem am 21.\u00a0Dezember 2021 eingebrachten Antrag, der Verfassungsgerichtshof m\u00f6ge"
        assert new_entry.document_body[2].annotation_container.dev_annotations == []	

  
class TestDBFile: 
    pass
