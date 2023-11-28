import argparse
import datetime
from typing import NoReturn

import meta_loader


class CLParser(argparse.ArgumentParser):
    def __init__(self):
        super().__init__()
        self.add_arguments()
        self.extract_args()

    def add_arguments(self):
        self.add_argument("--branch", type=str, choices=["vfgh", "vwgh", "justiz"], required=True)
        self.add_argument("--year", type=str, choices=[str(i) for i in range(1946, datetime.datetime.now().year + 1)], required=True)

    def extract_args(self):
        args = self.parse_args()
        self.year = str(args.year)
        self.branch = args.branch
   
    def error(self, message:str) -> NoReturn:
        message = f"Invalid arguments.\nUsage: python scraper.py --branch [vfgh|vwgh|justiz] --year [1946-{datetime.datetime.now().year}]"
        return self.exit(2, message)
    

if __name__ == "__main__":
    parser = CLParser()
    loader = meta_loader.MetaLoader(parser.branch, parser.year)
    meta_data = loader.load_meta_data()
    
