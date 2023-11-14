# extracts from every html file of a given year the decision body (Begründung) as text. 
# creates one json file for each year if not already existing. otherwise appends to existing file.
# the json file contains a list of dictionaries, each dictionary representing a decision.
# [{"decision_id": str, 
#  "decision_body": [str, str, ...]}
# ...]

from pathlib import Path
from bs4 import BeautifulSoup
import json

def print_stats(): 
    # get the number of all files in the html folder
    path = Path.cwd() / "data" / "judikatur" / branch / f"html_{year}"
    counter_all_files = 0
    for file in path.iterdir(): 
        counter_all_files += 1

    # get the number of all decisions in the database
    database = Path.cwd() / "data" / "judikatur" / branch / f"json_refined" / f"all_{year}.json"
    if database.exists():
        with open(database, "r", encoding="utf-8") as f: 
            database_content = json.load(f)
        counter_all_dec = len(database_content)

    print(f"all files: {counter_all_files}\nall decisions: {counter_all_dec}")


def get_decision_id(file_name) -> str: 
    """returns the decision id from the file name"""
    decision_id = file_name[:-5]
    return decision_id


def is_decision_in_db(new_decision, db_content) -> bool: 
    """checks if the decision is already in the database"""
    for decision in db_content: 
        if decision["decision_id"] == new_decision["decision_id"]: 
            return True
    return False


def add_to_database(new_decision_struct:dict) -> None: 
    database = Path.cwd() / "data" / "judikatur" / branch / f"json_refined" / f"all_{year}.json"
    # if the database does not exist yet, create it
    # otherwise load it, check if the decision is already in it, and append if not

    if not database.exists(): 
        database.touch()
        database.write_text(json.dumps([new_decision_struct], indent=4, ensure_ascii=False), encoding="utf-8")
    else:
        with open(database, "r", encoding="utf-8") as f: 
            database_content = json.load(f)
        if not is_decision_in_db(new_decision_struct, database_content): 
            database_content.append(new_decision_struct)
            with open(database, "w", encoding="utf-8") as f: 
                json.dump(database_content, f, indent=4, ensure_ascii=False)

    
# branch of law
branches = ["vfgh", "vwgh", "justiz"]
branch = branches[2]
year = "2023"


# path to the html files
path = Path.cwd() / "data" / "judikatur" / branch / f"html_{year}"


# main loop 
counter_all_dec = 0

for index, decision_file in enumerate(path.iterdir()):
    counter_all_dec += 1

    decision_id = get_decision_id(decision_file.name)
    soup = BeautifulSoup(decision_file.read_text(encoding="utf-8"), "html.parser")
    
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

    decision_struct = {"decision_id": decision_id, "decision_body": decision_body}
    add_to_database(decision_struct)

print_stats()


