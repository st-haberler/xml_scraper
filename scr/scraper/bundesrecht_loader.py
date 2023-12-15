import logging
from pathlib import Path
import re
import requests


DATA_PATH = Path.cwd() / "data" / "bundesrecht" 
META_PATH = "meta_data"

logging.basicConfig(level=logging.INFO)

class BundesrechtLoader:

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
        

    def _log_missed_downloads(self, missed_downloads:list[str], source_type:str) -> None:
        missed_file = DATA_PATH / source_type / f"{source_type}_missed_links.links"
        missed_file.write_text("\n".join(missed_downloads))


    def _save_bundesrecht(self, response:requests.Response, target_path:Path, filename:Path) -> None:
        decision_file = target_path / filename
        decision_file.write_text(response.text)

    
    def _get_link_collection(self, source_type:str) -> list[str]:
        link_file = DATA_PATH / source_type / META_PATH / f"{source_type}.links"
        return link_file.read_text().split("\n")
    

    def load_all(self, source_type:str) -> None:
        link_collection = self._get_link_collection(source_type)

        target_path = DATA_PATH / source_type / "html"
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

            try: 
                response = requests.get(link)
            except requests.RequestException:
                missed_downloads.append(link)
                continue
            if response.status_code != 200:
                missed_downloads.append(link)
                continue

            self._save_bundesrecht(response, target_path, filename)
           

        self._log_missed_downloads(missed_downloads, source_type)
        logging.info(f"Invalid links: {len(invalid_links)}")
        logging.info(f"Invalid filenames: {len(invalid_filenames)}")
        logging.info(f"Missed downloads: {len(missed_downloads)}")
        logging.info(f"Downloaded: {len(link_collection) - len(invalid_links) - len(invalid_filenames) - len(missed_downloads)}")


if __name__ == "__main__":
    loader = BundesrechtLoader()
    loader.load_all("PHG")