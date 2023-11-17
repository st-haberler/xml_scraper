# Unit tests for scraper.py using pytest

import pytest
import scraper

import argparse
from unittest.mock import patch


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
    for branch in scraper.BRANCHES:

    # Test case 5 Three command-line arguments (one invalid)

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        scraper.init_script('-branch branch1 -year 2022 -extra_arg')
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 2