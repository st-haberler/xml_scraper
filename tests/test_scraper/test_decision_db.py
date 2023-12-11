import json
from pathlib import Path

import decision_db


class TestDecisionDB:
    def __get_decision(self) -> Path:
        decision_file = Path("tests/test_scraper/test_data/test_vfgh_decision.html")
        return decision_file
        
    
    def __get_json_struct(self) -> dict:
        decision_db = Path("tests/test_scraper/test_data/test_vfgh_db.json")
        json_struct = json.loads(decision_db.read_text(encoding="utf-8"))
        return json_struct[0]
    
    
    def test_decision_to_dict(self):
        decision_file = self.__get_decision()
        expected_data = self.__get_json_struct()
        
        actual_data = decision_db.Decision.to_dict(decision_file)

        for para_actual, para_expected in zip(actual_data["decision_body"], expected_data["decision_body"]):
            assert para_actual == para_expected
