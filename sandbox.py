import pytest
from unittest.mock import Mock, patch, MagicMock
import datetime

from zeep import Client

# class Client:
#     def __init__(self, wsdl):
#         self.service = self.Service()

#     def anyfunc(self): 
#         return "anyfunc"

#     class Service:
#         def SearchDocumentsXml(self, test):
#             return "xml"


def get_now():
    return datetime.datetime.now()

def get_any():
    client = Client(wsdl="https://data.bka.gv.at/ris/ogd/v2.6/?WSDL")
    # response = client.service.SearchDocumentsXml("test")
    response = client.anyfunc()

    return response

def get_data():
    client = Client(wsdl="https://data.bka.gv.at/ris/ogd/v2.6/?WSDL")
    response = client.service.SearchDocumentsXml("test")

    return response


@patch("sandbox.datetime.datetime", autospec=True)
def test_get_now(mock_datetime):
    mock_datetime.now.return_value = datetime.datetime(2021, 1, 1)

    assert datetime.datetime.now() == datetime.datetime(2021, 1, 1)
    assert datetime.datetime.now().year == 2021


@patch("sandbox.Client", autospec=True)
def test_get_data(mock_client):
    mock_service = MagicMock()
    mock_service.SearchDocumentsXml.return_value = "test"

    mock_client.return_value.service = mock_service

    assert get_data() == "test"


if __name__ == "__main__":
    # client = Client(wsdl="https://data.bka.gv.at/ris/ogd/v2.6/?WSDL")
    # response = client.service.SearchDocumentsXml("test")
    # print(response[:400])

    client = Client(wsdl="abx")
    response = client.service.SearchDocumentsXml("test")
    print(response[:400])
