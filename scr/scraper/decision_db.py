from bs4 import BeautifulSoup as bs
import json
from pathlib import Path


class Decision:
    
    @classmethod
    def to_dict(cls, decision_file:Path) -> dict:
        decision_id = decision_file.stem
        soup = bs(decision_file.read_text(encoding="utf-8"), "html.parser")
        
        # find the decision body: <body><div><div><h1>Begründung</h1><p>...</p><p>...</p>...
        decision_body = []
        for div in soup.body.div.find_all("div"): 
            # check if h1 tag exists and if it contains "Begründung"
            if div.h1 and (("Begründung" in div.h1.text)
                        or ("Text" in div.h1.text)
                        or ("Rechtliche Beurteilung" in div.h1.text)): 
                for para in div.find_all("p"):  
                    # remove tags that are not meant for written text 
                    for sr in para.find_all("span", class_="sr-only"): 
                        sr.decompose()
                    decision_body.append(para.text)

        decision_struct = {"decision_id": decision_id, 
                           "decision_body": decision_body
                           }     
        return decision_struct


class DecisionDB: 
    
    def __init__(self, db_path:Path=None) -> None:
        if db_path is None:
            self.db_path = Path.cwd() / "data" / "judikatur" 
        else:
            self.db_path = db_path

    
    def is_decision_in_db(self, decision_id:str, db_list:dict) -> bool:
        for decision in db_list:
            if decision["decision_id"] == decision_id:
                return True
        return False
    
    
    def add_year_to_db(self, year:str, branch:str) -> None:
        html_path = Path.cwd() / "data" / "judikatur" / branch / f"html_{year}" 
        html_path.mkdir(parents=True, exist_ok=True)
        
        db_file = self.db_path / branch / "json_database" / f"all_{year}.json"
        if not db_file.exists():
            raise FileNotFoundError(f"Database file {db_file} does not exist. Wrong year or branch?")

        db_list = []
        for decision_file in html_path.glob("*.html"):
            new_decision_dict = Decision.to_dict(decision_file)
            if not self.is_decision_in_db(new_decision_dict["decision_id"], db_list):
                db_list.append(new_decision_dict)
        
        db_file.write_text(json.dumps(db_list, indent=4), encoding="utf-8")

