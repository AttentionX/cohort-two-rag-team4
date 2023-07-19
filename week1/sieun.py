import openai
from enum import Enum


class Colors(Enum):
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    GREY = "\033[90m"
    RESET = "\033[0m"


# Function to print text with color
def print_color(text, color, *args, **kwargs):
    print(f"{color.value}{text}{Colors.RESET.value}", *args, **kwargs)

class SearchIntent(Enum):
    SMALLTALK = "smalltalk"
    DOC_SEARCH = "document_search"
    WEB_SEARCH = "web_search"
    PAPER_SEARCH = "paper_search"


classify_intent_prompt = """Classify the intent of the query into one of the following categories based
on the description. Say the category only. 
categories: 
- SMALLTALK: This query doesn't require searching. 
- DOCUMENT_SEARCH: This query requires a search on internal documents related to GPT-4.
- WEB_SEARCH: This query can be assisted with information from the internet.
- PAPER_SEARCH: This query is looking for papers.

examples:
query: What is GPT-4?


query: '''{query}'''
"""

def classify_intent(query: str) -> SearchIntent:
    messages = [{"role":"user", "content": classify_intent_prompt.format(query=query)}]
    print_color("Classifying user intent...", Colors.GREY)
    chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                    messages=messages).choices[0].message.content.lower()

    for intent in SearchIntent:
        if intent.value in chat_completion:
            print_color(f"Response: {chat_completion}, classified as `{intent.name}`", Colors.GREY)
            return intent

    print_color(f"Response: {chat_completion}, could not parse output, using default.", Colors.GREY)
    return SearchIntent.SMALLTALK
