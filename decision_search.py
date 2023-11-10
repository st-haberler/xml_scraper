# this script searches the RIS for all decisions of one branch
# result is one xml file with the complete metadata of all decisions of one year

import argparse



BRANCHES = ["vwgh", "vfgh", "justiz"]
YEAR = 2023
RIS_API_WSDL = "https://data.bka.gv.at/ris/ogd/v2.6/?WSDL"



if __name__ == "__main__": 
    parser = argparse.ArgumentParser(description="Search the RIS for decisions of a specific branch.")
    parser.add_argument("-branch", choices=BRANCHES, help="The branch of the RIS to search in.")
    parser.add_argument("-year", type=int, help="The year to search in.")
    args = parser.parse_args()

    print(f"{args.branch} is selected.")
    print(f"{args.year} is selected.")