from pathlib import Path
from unittest.mock import patch, MagicMock

import decision_loader


class TestDecisionLoader:
    
    def __get_linklist(self): 
        link_file = Path.cwd() / "tests/test_scraper/test_data/test_links_vfgh_2022.links"
        link_list = link_file.read_text().split("\n")
        
        return link_list
    

    @patch("decision_loader.requests.get")
    @patch("decision_loader.DecisionLoader._get_link_collection")
    @patch("decision_loader.DecisionLoader._save_decision")
    @patch("decision_loader.DecisionLoader._log_missed_downloads")
    def test_load(self, mock_log, mock_save, mock_link_collection, mock_get):
        # arrange
        branch = "vfgh"
        year = "2021"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "test"
        mock_get.return_value = mock_response
        mock_link_collection.return_value = self.__get_linklist()
    
        sut = decision_loader.DecisionLoader()
        
        # act 
        sut.load_all(branch, year)
        
        # assert
        assert mock_save.call_count == len(self.__get_linklist())
