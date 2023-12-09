from pathlib import Path

import scr.scraper.meta_loader as ml
import scr.scraper.link_extractor as le


def download_decisions(branch:str="vfgh", year:str="2021") -> None:
    loader = ml.MetaLoader(branch, year)
    new_meta_data = loader.load_meta_data()
    
    ml.MetaSaver.save_meta_data(new_meta_data, branch, year)
    
    extractor = le.LinkExtractor()
    extractor.get_links(year, branch, todisk=True)



if __name__ == "__main__":
    download_decisions() 
    
    