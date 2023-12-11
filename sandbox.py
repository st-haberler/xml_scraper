import spacy

nlp = spacy.load("de_core_news_sm")

doc = nlp("Ich habe ein Auto gekauft.")

print(nlp.pipeline)