"""
A simple baseline for a question answering system.
"""
from pathlib import Path
import yaml
import openai
from annoy import AnnoyIndex

import os
import dotenv

dotenv.load_dotenv()
openai.api_key = os.getenv('API_KEY')

# --- load pre-processed chunks --- #
with open(Path(__file__).resolve().parent / "openai27052023.yaml", 'r') as f:
    paper = yaml.safe_load(f)
sentences = paper['sentences']


# --- embed chunks --- #
embeddings = [
    r['embedding']
    for r in openai.Embedding.create(input=sentences, model='text-embedding-ada-002')['data']
] 

# --- index embeddings for efficient search (using Spotify's annoy)--- #
hidden_size = len(embeddings[0])
index = AnnoyIndex(hidden_size, 'angular')  #  "angular" =  cosine
for i, e in enumerate(embeddings): 
    index.add_item(i , e)
index.build(10)  # build 10 trees for efficient search

messages = [
        {"role": "system", "content": 'You are a helpful assistant.'}
    ]

# --- iteratively answer questions (retrieve & generate) --- #
while True:
    query = input("Your question: ")
    embedding =  openai.Embedding.create(input = [query], model='text-embedding-ada-002')['data'][0]['embedding']
    # get nearest neighbors by vectors
    indices, distances = index.get_nns_by_vector(embedding,
                                                  n=3,  # return top 3
                                                  include_distances=True)
    results =  [ 
        (sentences[i], d)
        for i, d in zip(indices, distances)
    ]
    # with this, generate an answer 
    excerpts = [res[0] for res in results]
    excerpts = '\n'.join([f'[{i}]. {excerpt}' for i, excerpt in enumerate(excerpts, start=1)])
    prompt = f"""
    user query:
    {query}
    
    title of the paper:
    {paper['title']}
    
    excerpts: 
    {excerpts}
    ---
    given the excerpts from the paper above, answer the user query.
    In your answer, make sure to cite the excerpts by its number wherever appropriate.
    Note, however, that the excerpts may not be relevant to the user query.
    """
    
    messages += [{"role":"user", "content": query}]
    chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                    messages=messages)
    answer = chat_completion.choices[0].message.content
    
    messages += [{"role":"system", "content":answer}]
    answer += f"\n--- EXCERPTS ---\n{excerpts}"
    print(answer)



