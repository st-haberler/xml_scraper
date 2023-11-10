from pathlib import Path
import xml.etree.ElementTree as ET

# extract xml data from collection 
meta_collection_file = Path(Path.cwd() / "data" / "judikatur" / "vfgh" / "vfgh_meta_collection_all_2023.xml")
meta_collection_xml = ET.parse(meta_collection_file)
meta_collection_root = meta_collection_xml.getroot()
# ---------------------------------


# extract links from xml data
ns = {'ogd': 'http://ris.bka.gv.at/ogd/V2_6'}

content_reference_element = "ogd:OgdDocumentReference/ogd:Data/ogd:Dokumentliste/ogd:ContentReference"
content_reference_list = meta_collection_root.findall(f".//{content_reference_element}", namespaces=ns)

# filtered list excludes documents that are not decisions (embedded attachments, etc.)
filtered_content_reference_list = []
for content_reference in content_reference_list:
    if content_reference.find("ogd:ContentType", namespaces=ns).text == "MainDocument" and content_reference.find("ogd:Name", namespaces=ns).text == "Hauptdokument":
        filtered_content_reference_list.append(content_reference)  
print(f"{len(filtered_content_reference_list) = }")

links = []
for content_reference in filtered_content_reference_list:
    try: 
        urls_element = content_reference.find("ogd:Urls", namespaces=ns)
        for content_url in urls_element:
            if content_url.find("ogd:DataType", namespaces=ns).text == "Html":
                link = content_url.find("ogd:Url", namespaces=ns).text
                links.append(link)
    except AttributeError as e:
        print(e)
        continue
# ---------------------------------


# save links to file
year = "2023"
links_file = Path(Path.cwd() / "data" / "judikatur" / "vfgh" / f"vfgh_all_decision_links_{year}.links")

with open(links_file, "w") as f:
    for link in links:
        f.write(f"{link}\n")
# ---------------------------------


