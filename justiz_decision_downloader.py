import requests
from pathlib import Path
import re


def get_filename(link:str) -> str:
    """
    Extracts the filename from a link.
    """
    filename = re.search(r"\/([^\/]+)$", link).group(1)
    return filename



link_file = Path(Path.cwd() / "data" / "judikatur" / "justiz" / "justiz_all_decision_links_2023.links")
link_list = link_file.read_text().split("\n")


for index, link in enumerate(link_list): 
    file_name = get_filename(link)
    if file_name in [f.name for f in Path(Path.cwd() / "data" / "judikatur" / "justiz" / "html_2023").iterdir()]: 
        print(f"Skipping {file_name}...")
        continue

    response = requests.get(link)
    Path(Path.cwd() / "data" / "judikatur" / "justiz" / "html_2023" / file_name).write_text(response.text, encoding="utf-8") 

