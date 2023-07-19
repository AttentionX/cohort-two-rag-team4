"""
A simple baseline for a question answering system.
"""
from pathlib import Path
import yaml
import openai
from annoy import AnnoyIndex
import sieun

import os
import dotenv

from index import build_index, is_meaningless_query

dotenv.load_dotenv()
openai.api_key = os.getenv('API_KEY')

# --- load pre-processed chunks --- #
with open(Path(__file__).resolve().parent / "openai27052023.yaml", 'r') as f:
    paper = yaml.safe_load(f)
sentences = paper['sentences'][:10]

# --- embed chunks and make it as index --- #
index = build_index(sentences)

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

    elif intent == sieun.SearchIntent.DOC_SEARCH:
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
        
        title of the paper:
        {paper['title']}
        
        excerpts: 
        {excerpts}
        ---
        given the excerpts from the paper above, answer the user query.
        In your answer, make sure to cite the excerpts by its number wherever appropriate.
        Note, however, that the excerpts may not be relevant to the user query.
        """

        sieun.print_color(f"\n--- EXCERPTS ---\n{excerpts}", sieun.Colors.GREY)
        messages += [{"role": "user", "content": query}]

    elif intent == sieun.SearchIntent.WEB_SEARCH:
        pass
    elif intent == sieun.SearchIntent.PAPER_SEARCH:
        pass
    #
    chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                   messages=messages)
    answer = chat_completion.choices[0].message.content

    messages += [{"role": "system", "content": answer}]

    sieun.print_color("[Answer]: ", sieun.Colors.GREEN, end="")
    print(answer)
