import openai
from annoy import AnnoyIndex


def build_index(source: list[str]) -> AnnoyIndex:
    # --- embed chunks --- #
    embeddings = [
        r['embedding']
        for r in openai.Embedding.create(input=source, model='text-embedding-ada-002')['data']
    ]

    # --- index embeddings for efficient search (using Spotify's annoy)--- #
    hidden_size = len(embeddings[0])
    index = AnnoyIndex(hidden_size, 'angular')  # "angular" =  cosine
    for i, e in enumerate(embeddings):
        index.add_item(i, e)
    index.build(10)  # build 10 trees for efficient search
    return index


# pre-defined meaningless questions #
meaningless_questions = [
    "How are you?",
    "What is your name?",
    "What is your favorite color?",
    "What is your favorite food?",
    "How is the weather?",
    "What's the secret to happiness?",
    "Why do we drive on a parkway and park on a driveway?",
    "How many licks does it take to get to the center of a Tootsie Pop?",
    "What color is the number seven?",
    "What's the meaning of life without a question mark?",
    "Who made GPT4?"
]

meaningless_questions_index = build_index(meaningless_questions)


def is_meaningless_query(embedding) -> bool:
    idx, dist = meaningless_questions_index.get_nns_by_vector(embedding, n=1, include_distances=True)
    should_filter = dist[0] < 0.5
    if should_filter:
        print(f"Skip Meaningless Question: similar with: {meaningless_questions[idx[0]]}, similarity: {dist[0]}")
    else:
        print(f"Question Accepted...")
    return should_filter
