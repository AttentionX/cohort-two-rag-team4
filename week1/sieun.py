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
    COGNITIVE_SEARCH = "document_search"
    KEYWORD_SEARCH = "keyword_search"
    WEB_SEARCH = "web_search"
    # PAPER_SEARCH = "paper_search"


classify_intent_prompt = """Classify the intent of the query into one of the following categories based
on the description. Say the category only. 
categories: 
- SMALLTALK: This query doesn't require searching. 
- COGNITIVE_SEARCH: This query is a complete sentence and this query requires a search over internal documents related to GPT-4.
- KEYWORD_SEARCH: The query is mainly a keyword-based query instead of a complete sentence and his query requires a search over internal documents related to GPT-4.
- WEB_SEARCH: This query can be assisted with information from the internet, including recent information.

examples:
query: Apple mr headset
intent: WEB_SEARCH
query: What data is GPT-4 trained on?
intent: DOCUMENT_SEARCH
query: What is today's weather?
intent: WEB_SEARCH
query: Implement heapsort in Python
intent: SMALLTALK
query: How much does it cost to use GPT models?
intent: COGNITIVE_SEARCH
query: gpt4 api
intent: KEYWORD_SEARCH
query: What is a QR code?
intent: WEB_SEARCH

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
