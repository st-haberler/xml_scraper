from pathlib import Path
import xml.etree.ElementTree as ET
import argparse
import datetime

# global constants 
BRANCHES = ["vwgh", "vfgh", "justiz"]
BRANCH = None
YEAR = None
ns = {'ogd': 'http://ris.bka.gv.at/ogd/V2_6'}
content_reference_element = "ogd:OgdDocumentReference/ogd:Data/ogd:Dokumentliste/ogd:ContentReference"
# ---------------------------------


def init_by_args() -> None: 
    """
    Initialize the script by command line arguments.
    """
    global BRANCH, YEAR

    parser = argparse.ArgumentParser(description="Extract links to decisions from downloaded metadata collection.")
    parser.add_argument("-branch", choices=BRANCHES, help="The branch of the links to extract.")
    parser.add_argument("-year", type=int, help="The year of the links to extract.")
    args = parser.parse_args()

    # general introduction message
    print("This module extracts links to decisions from downloaded metadata collection. ")

    # check if arguments are valid, if not: display message and exit
    if args.branch not in BRANCHES:
        print(f"Invalid argument: Branch must be one of {BRANCHES}.")
        exit()
    else: 
        BRANCH = args.branch
    if args.year < 1946 or args.year > datetime.datetime.now().year:
        print(f"Invalid argument: Year must be between 1946 and {datetime.datetime.now().year}.")
        exit()
    else:
        YEAR = args.year


def extract_xml_from_collection() -> None:
    global meta_collection_file, meta_collection_xml, meta_collection_root

    meta_collection_file = Path(Path.cwd() / "data" / "judikatur" / BRANCH / f"{BRANCH}_meta_collection_all_{YEAR}.xml")
    meta_collection_xml = ET.parse(meta_collection_file)
    meta_collection_root = meta_collection_xml.getroot()


def extract_links_from_xml() -> None:
    global links
    
    content_reference_list = meta_collection_root.findall(f".//{content_reference_element}", namespaces=ns)

    # filtered list excludes documents that are not decisions (embedded attachments, etc.)
    filtered_content_reference_list = []
    for content_reference in content_reference_list:
        if content_reference.find("ogd:ContentType", namespaces=ns).text == "MainDocument" and content_reference.find("ogd:Name", namespaces=ns).text == "Hauptdokument":
            filtered_content_reference_list.append(content_reference)

    links = []
    for content_reference in filtered_content_reference_list:
        try: 
            urls_element = content_reference.find("ogd:Urls", namespaces=ns)
            for content_url in urls_element:
                if content_url.find("ogd:DataType", namespaces=ns).text == "Html":
                    link = content_url.find("ogd:Url", namespaces=ns).text
                    links.append(link)
        except AttributeError as e:
            print(e)
            continue


def save_links_to_file() -> None:
    links_file = Path(Path.cwd() / "data" / "judikatur" / BRANCH / f"{BRANCH}_all_decision_links_{YEAR}.links")

    with open(links_file, "w") as f:
        for link in links:
            f.write(f"{link}\n")


def extract_to_file(branch:str, year:str, file_name:str) -> None:
    global BRANCH, YEAR
    BRANCH = branch
    YEAR = year
    extract_xml_from_collection()
    extract_links_from_xml()

    file = Path(Path.cwd() / "data" / "judikatur" / BRANCH / file_name)
    with open(file, "w") as f:
        for link in links:
            f.write(f"{link}\n")


if __name__ == "__main__": 
    init_by_args()
    extract_xml_from_collection()
    extract_links_from_xml()
    save_links_to_file()