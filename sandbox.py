from pathlib import Path

for file in (Path.cwd() / "data").rglob("*.json"):
    print(file.name)
    
    # replace in file all occurences of "decision" with "doc"
    text = file.read_text(encoding="utf-8")
    text = text.replace("decision", "doc")
    file.write_text(text, encoding="utf-8")
