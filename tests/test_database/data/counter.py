#throw away script to count the number of elements in the xml file

import xml.etree.ElementTree as ET
from pathlib import Path

NAMESPACE = {"ogd": "http://ris.bka.gv.at/ogd/V2_6"}

file = Path(r"tests\test_database\data\test_bundesrecht_collection.xml")
tree = ET.parse(file)
root = tree.getroot()
print(len(root))