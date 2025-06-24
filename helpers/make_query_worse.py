import random
import spacy
import re
from make_query_better import get_response

nlp = spacy.load("en_core_web_sm")

def remove_fraction_function_words(sentence, fraction=0.5):
    doc = nlp(sentence)

    # First: remove punctuation tokens
    tokens_no_punct = [token for token in doc if not token.is_punct]

    # Build list of tokens (just text) and identify content word indices
    words = [token.text for token in tokens_no_punct]
    content_indices = [
        i for i, token in enumerate(tokens_no_punct)
        if token.pos_ in ["PRON", "DET", "ADP", "CCONJ", "SCONJ", "PART", "AUX", "INTJ", "VERB", "ADV", "NUM", "SYM", "X"]
    ]

    # Remove a fraction of the content words
    num_to_remove = int(len(content_indices) * fraction)
    indices_to_remove = set(random.sample(content_indices, num_to_remove)) if num_to_remove > 0 else set()

    # Reconstruct cleaned sentence
    new_sentence = ' '.join([
        word for i, word in enumerate(words) if i not in indices_to_remove
    ])
    
    # remove what, why, how, when, where, who from the beginning of the sentence
    pattern = r'^(who|what|when|where|why|how)\b[\s,;:]*'
    new_sentence = re.sub(pattern, '', new_sentence, flags=re.IGNORECASE).lstrip()

    return new_sentence

def remove_content_words():
    
        print(f"Reformulating Question Version 1")
    
    system_prompt = '''You are a researcher. Create 3 follow-up queries that are more specific than a given user's query but still closely connected it. You will be given:
- An underspecified user query
- ScholarQA's LLM-generated answer, which includes section titles, content, and citations.

Follow these steps:

    1. Read the query.
    2. Read the LLM-generated answer, including the section titles, content, and citations.
    3. Taking inspiration from the answer's section titles, content, and citations write 3 reformulated queries that are more specific than the original query, but still related to it.
    4. Return your output in the following JSON format: {"reformulated1": "first reformulated query", "reformulated2": "second reformulated query", "reformulated3": "third reformulated query"}. Do not provide any additional information or explanation.
'''

    user_prompt = f'''Original Query:\n{original_query}\n\n
LLM-Generated Answer:\n{llm_answer}\n\n

Reformulated Queries in JSON Format: {{"reformulated1": "", "reformulated2": "", "reformulated3": ""}}'''

    messages = [
                    {'role': 'developer', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ]

    response = get_response(messages, _model='gpt-4.1', _max_tokens=300)
    
    return response


# Example usage
if __name__ == "__main__":
    sentence = "The quick brown fox jumps over the lazy dog."
    print(remove_fraction_function_words(sentence, fraction=0.3))