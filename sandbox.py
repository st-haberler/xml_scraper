import spacy

nlp = spacy.load("de_core_news_sm")
doc = nlp("Ich bin ein Satz.")

for token in doc:
    print(token.text_with_ws, "-")

