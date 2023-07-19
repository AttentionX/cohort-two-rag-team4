"""
A simple baseline for a question answering system.
"""
from pathlib import Path
import json 
import openai
from annoy import AnnoyIndex
import sieun
from rank_bm25 import BM25Okapi

import os
import dotenv

from index import build_index, is_meaningless_query

dotenv.load_dotenv()
openai.api_key = os.getenv('API_KEY')

# --- load pre-processed chunks --- #
with open('embeddings.json', 'r') as f:
    data = json.load(f)

sentences = data['sentences']
embeddings = data['embeddings']

# --- index embeddings for efficient search (using Spotify's annoy)--- #
hidden_size = len(embeddings[0])
index = AnnoyIndex(hidden_size, 'angular')  #  "angular" =  cosine
for i, e in enumerate(embeddings): 
    index.add_item(i , e)
index.build(10)  # build 10 trees for efficient search

# --- BM25 index (todo) 
import nltk
from nltk.stem import PorterStemmer
porter_stemmer = PorterStemmer()
# doc = """In linguistic morphology and information retrieval, stemming is the process of reducing inflected (or sometimes derived) words to their word stem, base or root form—generally a written word form. The stem need not be identical to the morphological root of the word; it is usually sufficient that related words map to the same stem, even if this stem is not in itself a valid root."""

def tokenize_doc(doc):
    tokens = nltk.word_tokenize(doc)
    stemmed_tokens = [porter_stemmer.stem(token) for token in tokens]
    return stemmed_tokens

tokenized_corpus = [tokenize_doc(doc) for doc in sentences]

bm25 = BM25Okapi(tokenized_corpus)


messages = [
    {"role": "system", "content": 'You are a helpful assistant.'}
]

# --- iteratively answer questions (retrieve & generate) --- #
while True:
    sieun.print_color("[Question]: ", sieun.Colors.RED, end="")
    query = input("Your question: ")
    intent = sieun.classify_intent(query)

    if intent == sieun.SearchIntent.SMALLTALK:
        messages += [{"role": "user", "content": query}]

    elif intent == sieun.SearchIntent.COGNITIVE_SEARCH:
        ### filter logic
        embedding = openai.Embedding.create(input=[query], model='text-embedding-ada-002')['data'][0]['embedding']
        if is_meaningless_query(embedding):
            continue
        # get nearest neighbors by vectors
        indices, distances = index.get_nns_by_vector(embedding,
                                                     n=3,  # return top 3
                                                     include_distances=True)
        results = [
            (sentences[i], d)
            for i, d in zip(indices, distances)
        ]
        # with this, generate an answer 
        excerpts = [res[0] for res in results]
        excerpts = '\n'.join([f'[{i}]. {excerpt}' for i, excerpt in enumerate(excerpts, start=1)])
        prompt = f"""
        user query:
        {query}
        
        excerpts: 
        {excerpts}
        ---
        A GPT-4 model was recently released. 
        Given the excerpts from the paper above, answer the user query.
        In your answer, make sure to cite the excerpts by its number wherever appropriate.
        Note, however, that the excerpts may not be relevant to the user query.
        """

        sieun.print_color(f"\n--- EXCERPTS ---\n{excerpts}", sieun.Colors.GREY)
        messages += [{"role": "user", "content": query}]

    elif intent == sieun.SearchIntent.WEB_SEARCH:
        def split_text(raw_text, chunk_size):
            chunks = []
            start = 0
            while start < len(raw_text):
                chunks.append(raw_text[start:start + chunk_size])
                start += chunk_size
            return chunks
        
        google_query = query ######
        data = search_for_text(google_query, k=2)
        sentences = []
        for (link, text) in data:
            sentences += split_text(text, 400)
        index = build_index(sentences)
        
        embedding = openai.Embedding.create(input=[query], model='text-embedding-ada-002')['data'][0]['embedding']
        indices, distances = index.get_nns_by_vector(embedding,
                                                     n=3,  # return top 3
                                                     include_distances=True)
        results = [
            (sentences[i], d)
            for i, d in zip(indices, distances)
        ]
        print(results)
        
        # with this, generate an answer 
        excerpts = [res[0] for res in results]
        excerpts = '\n'.join([f'[{i}]. {excerpt}' for i, excerpt in enumerate(excerpts, start=1)])
        prompt = f"""
        user query:
        {query}
        
        excerpts: 
        {excerpts}
        ---
        given the excerpts from the paper above, answer the user query.
        In your answer, make sure to cite the excerpts by its number wherever appropriate.
        Note, however, that the excerpts may not be relevant to the user query.
        """

        sieun.print_color(f"\n--- EXCERPTS ---\n{excerpts}", sieun.Colors.GREY)
        messages += [{"role": "user", "content": query}]

    elif intent == sieun.SearchIntent.KEYWORD_SEARCH:
        excerpts = bm25.get_top_n(tokenize_doc(query), sentences, n=5)
        excerpts = '\n'.join([f'[{i}]. {excerpt}' for i, excerpt in enumerate(excerpts, start=1)])
        prompt = f"""
        user query:
        {query}
        
        excerpts: 
        {excerpts}
        ---
        A GPT-4 model was recently released. 
        given the excerpts from the paper above, answer the user query.
        In your answer, make sure to cite the excerpts by its number wherever appropriate.
        Note, however, that the excerpts may not be relevant to the user query.
        """

        sieun.print_color(f"\n--- EXCERPTS ---\n{excerpts}", sieun.Colors.GREY)
        messages += [{"role": "user", "content": query}]
        
    chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                   messages=messages)
    answer = chat_completion.choices[0].message.content

    messages += [{"role": "system", "content": answer}]

    sieun.print_color("[Answer]: ", sieun.Colors.GREEN, end="")
    print(answer)
