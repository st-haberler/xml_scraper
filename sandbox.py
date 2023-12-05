from pathlib import Path

from zeep import Client






if __name__ == "__main__":
    request_file = Path(r"xml/request_templates/vfgh_query.xml")
    request = request_file.read_text(encoding="utf-8")
    
    client = Client(wsdl="https://data.bka.gv.at/ris/ogd/v2.6/?WSDL")
    response = client.service.SearchDocumentsXml(request)
    print(response[:400])

    test_request = Path(r"tests/test_scraper/test_response_2.xml")
    test_request.write_text(response, encoding="utf-8")

    
    