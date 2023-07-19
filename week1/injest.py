from glob import glob
from pathlib import Path
from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import Title, NarrativeText
import spacy
import yaml
import os


def injest_pdf(title: str):
    # --- split the PDF into chunks & save it (using unstructured) --- #
    elements = partition_pdf(filename=Path(title), strategy="auto")

    # build dtm, upsert vectors, etc.
    paragraphs = ""
    for el in elements:
        if isinstance(el, Title):
            paragraphs += "<TITLE>"
        if isinstance(el, NarrativeText):
            el_as_str = str(el).strip()
            if " " in el_as_str and not el_as_str.startswith("["):
                paragraphs += el_as_str
    paragraphs = [p for p in paragraphs.split("<TITLE>") if p]
    nlp = spacy.load("en_core_web_sm")  #  use this as a sentencizer
    sentences_by_paragraph: list[list[str]] = [
        [sent.text for sent in nlp(p).sents]
        for p in paragraphs
    ]
    filename = os.path.basename(title)
    bigrams_by_paragraph: list[list[str]] = [
        [f"title:{filename}, {sentences[i]} {sentences[i+1]}" for i in range(len(sentences)-1)]
        for sentences in sentences_by_paragraph
    ]

    # just flatten it out
    return [
        sent
        for sentences in bigrams_by_paragraph
        for sent in sentences
    ]

sentences = []

for fp in glob("./raw_data/*.pdf"):
    print(f"[*] injesting {fp}")
    sentences += injest_pdf(fp)
    

print(sentences[:10])
print(len(sentences))

# --- load pre-processed chunks --- #

import openai
openai.api_key = os.getenv('API_KEY')


# --- embed chunks --- #
_sentences = []
embeddings = []

from tqdm import tqdm
for s in tqdm(range(0, len(sentences), 100)):
    try:
        s = sentences[s: min(len(sentences), s + 100)]
        e = [
            it["embedding"] for it in openai.Embedding.create(input=s, model='text-embedding-ada-002')['data']
        ]
        
        _sentences += s
        embeddings += e
    except:
        print("modeated:", s)

import json
with open('embeddings.json', 'w') as f:
    json.dump({"embeddings": embeddings, "sentences": sentences}, f)

