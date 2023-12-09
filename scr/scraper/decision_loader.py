import logging
from pathlib import Path
import re
import requests


DATA_PATH = Path.cwd() / "data" / "judikatur" 
META_PATH = "meta_data"


logging.basicConfig(level=logging.INFO)


class DecisionLoader:

    def __init__(self) -> None:
        pass


    def _is_link(self, link:str) -> bool:
        return link.startswith("https://www.ris.bka.gv.at/Dokumente/") and link.endswith(".html")
    
    def _get_filename(self, link:str) -> str:
        """
        Extracts the filename from a link ie the substring after the last slash.
        """
        try: 
            filename = re.search(r"\/([^\/]+)$", link).group(1)
            return filename
        except AttributeError as e:
            logging.error(f"Could not extract filename from:\n{link}.", exc_info=True)
            return None
        

    def _log_missed_downloads(self, missed_downloads:list[str], branch:str, year:str) -> None:
        missed_file = DATA_PATH / branch / f"html_{year}" / f"{branch}_{year}_missed_links.links"
        missed_file.write_text("\n".join(missed_downloads))

    
    def _save_decision(self, response:requests.Response, target_path:Path, filename:Path) -> None:
        decision_file = target_path / filename
        decision_file.write_text(response.text)


    def _get_link_collection(self, branch:str, year:str) -> list[str]:
        link_file = DATA_PATH / branch / META_PATH / f"{branch}_all_links_{year}.links"
        return link_file.read_text().split("\n")


    def load_all(self, branch, year) -> None:
        link_collection = self._get_link_collection(branch, year)

        target_path = DATA_PATH / branch / f"html_{year}" 
        target_path.mkdir(parents=True, exist_ok=True)

        invalid_links = []
        invalid_filenames = []
        missed_downloads = []

        for link in link_collection:
            if not self._is_link(link): 
                invalid_links.append(link)
                continue
            
            filename = self._get_filename(link)
            
            if filename is None:
                invalid_filenames.append(link)
                continue
            if filename in target_path.iterdir():
                logging.info(f"File {filename} already exists.")
                continue

            try:                
                response = requests.get(link, timeout=10)
            except requests.RequestException: 
                missed_downloads.append(link)
                continue
            if response.status_code != 200:
                missed_downloads.append(link)
                continue
            
            self._save_decision(response, target_path, filename)
            

        self._log_missed_downloads(missed_downloads, branch, year)

        logging.info(f"Invalid links: {invalid_links}")
        logging.info(f"Invalid filenames: {invalid_filenames}")
        logging.info(f"Missed downloads: {missed_downloads}")
        logging.info(f"Downloaded {len(link_collection) - len(missed_downloads)} files.")



                
                
