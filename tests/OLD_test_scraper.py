# Unit tests for scraper.py using pytest

import pytest
import scr.scraper.scraper as scraper

import argparse
from unittest.mock import patch
import datetime
from pathlib import Path


def test_init_script():
    # Test case 1 No command-line arguments
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        with patch('argparse.ArgumentParser.parse_args', 
                   return_value=argparse.Namespace(branch=None, year=None)):
            scraper.init_script()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 2 

    # Test case 2 One command-line argument (invalid)
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        with patch('argparse.ArgumentParser.parse_args', 
                   return_value=argparse.Namespace(branch="INVALID", year=None)):
            scraper.init_script()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 2 
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        with patch('argparse.ArgumentParser.parse_args', 
                   return_value=argparse.Namespace(branch=None, year="INVALID")):
            scraper.init_script()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 2 

    # Test case 3 Two command-line arguments (one invalid)
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        with patch('argparse.ArgumentParser.parse_args', 
                   return_value=argparse.Namespace(branch="INVALID", year="2022")):
            scraper.init_script()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 2 
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        with patch('argparse.ArgumentParser.parse_args', 
                   return_value=argparse.Namespace(branch="vfgh", year="INVALID")):
            scraper.init_script()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 2 

    # Test case 4 Two command-line arguments (both valid, but one invalid value)
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        with patch('argparse.ArgumentParser.parse_args', 
                   return_value=argparse.Namespace(branch="vfgh", year="1815")):
            scraper.init_script()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 2 
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        with patch('argparse.ArgumentParser.parse_args', 
                   return_value=argparse.Namespace(branch="DSK", year="2020")):
            scraper.init_script()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 2 

    # Test case 5 two command-line arguments (both invalid, all combinations)
    current_year = datetime.datetime.now().year
    for branch in scraper.BRANCHES:
        for year in [1946, current_year]: 
            with patch('argparse.ArgumentParser.parse_args', 
                    return_value=argparse.Namespace(branch=branch, year=year)):
                scraper.init_script()
            assert scraper.year == year
            assert scraper.branch == branch
            assert scraper.meta_data_path.exists() and scraper.meta_data_path.is_dir()
            # delete the directory, if empty
            try: 
                scraper.meta_data_path.rmdir()
                assert not scraper.meta_data_path.exists()
            except OSError:
                pass                
            assert scraper.html_target_path.exists() and scraper.html_target_path.is_dir()
            # delete the directory, if empty
            try: 
                scraper.html_target_path.rmdir()
                assert not scraper.html_target_path.exists()
            except OSError:
                pass
            assert scraper.json_target_path.exists() and scraper.json_target_path.is_dir()
            # delete the directory, if empty
            try: 
                scraper.json_target_path.rmdir()
                assert not scraper.json_target_path.exists()
            except OSError:
                pass

    # Test case 5 Three command-line arguments (one invalid)
    with patch('argparse.ArgumentParser.parse_args', 
                return_value=argparse.Namespace(branch="vfgh", year="1950", invalid="invalid")):
            scraper.init_script()
    try: 
        scraper.meta_data_path.rmdir()
        scraper.html_target_path.rmdir()
        scraper.json_target_path.rmdir()
    except OSError:
        pass

    

def test_get_meta_data():#
    # test case 1: current year
        pass