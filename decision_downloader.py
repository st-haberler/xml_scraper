import requests
from pathlib import Path
import re
import argparse

def init_by_args() -> None:
    """
    Initializes the downloader by command line arguments.
    """
    global branch, year

    parser = argparse.ArgumentParser(description="Download decisions via the RIS API.")
    parser.add_argument("-branch", type=str, help="The branch of law to download decisions from.")
    parser.add_argument("-year", type=str, help="The year to download decisions from.")
    args = parser.parse_args()

    branch = args.branch
    year = args.year


def get_filename(link:str) -> str:
    """
    Extracts the filename from a link.
    """
    filename = re.search(r"\/([^\/]+)$", link).group(1)
    return filename

def download_decisions() -> None:
    link_file = Path(Path.cwd() / "data" / "judikatur" / branch / f"{branch}_all_decision_links_{year}.links")
    link_list = link_file.read_text().split("\n")

    for index, link in enumerate(link_list): 
        file_name = get_filename(link)
        if file_name in [f.name for f in Path(Path.cwd() / "data" / "judikatur" / branch / f"html_{year}").iterdir()]: 
            print(f"Skipping {file_name}...")
            continue
        try: 
            response = requests.get(link, timeout=10)
        except Exception as e:
            print(e)
            continue
        Path(Path.cwd() / "data" / "judikatur" / branch / f"html_{year}" / file_name).write_text(response.text, encoding="utf-8")


if __name__ == "__main__": 
    init_by_args()
    download_decisions()