from typing import Literal
import pytest
from unittest.mock import patch, call, PropertyMock
import argparse
import scraper 
import datetime
from pathlib import Path
# test for init_script using pytest, fixtures, mock, patch, parametrize and mark as needed
# ("vfgh", "1945"), ("justiz", str(datetime.datetime.now().year)),



@pytest.mark.parametrize("branch, year", [("vfgh", str(datetime.datetime.now().year + 1)),
                                          ("DSK", str(datetime.datetime.now().year)), 
                                          ("vwgh", None), 
                                          (None, "2022"),
                                          (None, None),
                                          ("INVALID", "2022"),
                                          ("vfgh", "INVALID"),
                                          ("INVALID", "INVALID")])
def test_init_script_invalid_args(branch: Literal['vfgh', 'DSK', 'vwgh', 'INVALID'] | None, year: str | None):
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        with patch("argparse.ArgumentParser.parse_args", 
                   return_value=argparse.Namespace(branch=branch, year=year)):
            scraper.init_script()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 2

### UNDER CONSTRUCTION ###
@pytest.mark.parametrize("branch, year", [("vfgh", "1951")])
@patch("pathlib.Path.mkdir")
def test_init_script_valid_args(mock_mkdir, branch:str, year:str):
    with patch("scraper.argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(branch=branch, year=year)):
        scraper.init_script()
        assert mock_mkdir.call_count == 3
        mock_mkdir.assert_called_with(exist_ok=True, parents=True)
        assert scraper.meta_data_path.name == scraper.Path.cwd() / "data" / branch / year


# @pytest.mark.parametrize("branch, year", [("vfgh", str(datetime.datetime.now().year))])
# @patch("pathlib.Path.exists")
# @patch("pathlib.Path.mkdir")
# def test_init_script_valid_args_create_dir(branch:str, year: str, mock_exists, mock_mkdir):
#     with patch("scraper.argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(branch=branch, year=year)):
#         mock_exists.return_value = False
#         scraper.init_script()
#         mock_mkdir.assert_called_with(exist_ok=True, parents=True)

    



    # with patch("scraper.meta_data_path") as mock_meta_data_path: 
    #     scraper.init_script()
    #     assert mock_meta_data_path.
    
    # with patch("scraper.Path.exists", return_value=True), patch("scraper.Path.mkdir") as mock_mkdir, patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(branch=branch, year=year)):
    #     scraper.init_script()
    #     mock_mkdir.assert_not_called()
        
# @pytest.mark.parametrize("branch, year", [("vfgh", "1951")])
# def test_init_script_valid_args_new_dir(branch:str, year: str):
#     with patch("scraper.meta_data_path.exists", new_callable=PropertyMock) as mock_property, patch("scraper.meta_data_path.mkdir") as mock_mkdir, patch("scraper.argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(branch=branch, year=year)):
#         mock_property.return_value = "False"
#         scraper.init_script()
#         assert mock_mkdir.call_count == 3



# @pytest.mark.parametrize("branch, year", [("vfgh", "1952")])     
# def test_init_script_valid_args_ndir(branch:str, year:str): 
    
    
#     with patch("scraper.meta_data_path.exists", return_value=True):
#         scraper.init_script()
#         assert True
 


    