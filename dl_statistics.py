from pathlib import Path
import argparse
import re 

parser = argparse.ArgumentParser(description="Extract links to decisions from downloaded metadata collection.")
parser.add_argument("-branch", type=str, help="The branch of the links to extract.")
parser.add_argument("-year", type=str, help="The year of the links to extract.")
args = parser.parse_args()

html_path = Path(Path.cwd() / "data" / "judikatur" / args.branch / f"html_{args.year}")
html_files = [f.name for f in html_path.iterdir() if f.is_file()]

link_list = Path(Path.cwd() / "data" / "judikatur" / args.branch / f"{args.branch}_all_decision_links_{args.year}.links").read_text().split("\n")

downloaded_links = 0
for counter, link in enumerate(link_list):
    for file in html_files: 
        if file in link:
            downloaded_links += 1
            

print(f"Links: {counter} | Downloaded links: {downloaded_links}")
