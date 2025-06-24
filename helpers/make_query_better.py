# Imports
import time
import os
import argparse
import json
import numpy as np
import pandas as pd
from openai import OpenAI

def get_response(_messages, _model='gpt-4.1', _max_tokens=300):

    client = OpenAI(
        api_key = open(os.path.join('../../PhD/apikeys', 'ai2_openai_key')).read().strip()
    )

    attempts = 0
    max_attempts = 3
    response = 'None'

    while attempts < max_attempts:
        try:
            response = client.chat.completions.create(
                model= _model,
                max_completion_tokens=_max_tokens,
                messages = _messages
            )
            
            _answer = response.choices[0].message.content.strip()
            answer_dict = json.loads(_answer)
            break

        except Exception as e:
            print(f'Error {e}. Sleeping 3 seconds ...')
            time.sleep(3)
            if attempts == max_attempts-1:
                answer_dict = f'Error {e}'

        attempts += 1
        time.sleep(0.5)

    return answer_dict


def reformulate_given_answer(original_query, llm_answer):
    
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


def asking_clarifyingq(original_query, llm_answer):
    
    print(f"Asking Clarifying Questions")
    
    system_prompt = '''You are a researcher. A colleague submitted a query to ScholarQA and received an answer. Write 3 clarifying questions to your colleague to better understand what they were specifically looking for. You will be given:
- An underspecified user query
- ScholarQA's LLM-generated answer, which includes section titles, content, and citations.

Follow these steps:

    1. Read the query.
    2. Read the LLM-generated answer, including the section titles, content, and citations.
    3. Taking inspiration from the answer's section titles, content, and citations write 3 reformulated queries that are more specific than the original query, but still related to it.
    4. Return your output in the following JSON format: {"clarifying1": "first clarifying question", "clarifying2": "second clarifying question", "clarifying3": "third clarifying question"}. Do not provide any additional information or explanation.
'''

    user_prompt = f'''Original Query:\n{original_query}\n\n
LLM-Generated Answer:\n{llm_answer}\n\n"

Clarifying Questions in JSON Format: {{'clarifying1': '', 'clarifying2': '', 'clarifying3': ''}}'''

    messages = [
                    {'role': 'developer', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ]

    response = get_response(messages, _model='gpt-4.1', _max_tokens=300)
    
    return response


def simulated_user(original_query, llm_answer, clarifying_question):
    
    print(f"Answering Clarifying Questions")
    
    system_prompt = '''You are a researcher. You submitted a question to ScholarQA, and received an LLM-generated answer as well as a clarifying question asked to you by ScholarQA to better understand your query. Answer the clarifying question being given:
    - your original query
    - ScholarQA's LLM-generated answer, which includes section titles, content, and citations
    - a clarifying question asked to you by ScholarQA to better understand your query.

Follow these steps:

    1. Read the query.
    2. Read the LLM-generated answer, including the section titles, content, and citations.
    3. Read the clarifying question.
    4. Use the above information to answer the clarifying question.
    5. Return your output in the following JSON format: {"clarifying_answer": "your answer to the clarifying question"}. Do not provide any additional information or explanation.
'''
# in the future you should add user history

    user_prompt = f'''Original Query:\n{original_query}\n\n
LLM-Generated Answer:\n{llm_answer}\n\n
Clarifying Question:\n{clarifying_question}\n\n

Clarifying Answers in JSON Format: {{'clarifying1': '', 'clarifying2': '', 'clarifying3': ''}}'''

    messages = [
                    {'role': 'developer', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ]

    response = get_response(messages, _model='gpt-4.1', _max_tokens=300)
    
    return response


def reformulate_given_clarification(original_query, llm_answer, clarifying):
    
    print(f"Reformulating Question Version 2")

    system_prompt = f'''You are a researcher. A colleague submitted a query to ScholarQA and received an answer. You asked your colleague three clarifying questions to better understand what they were specifically looking for and received answers to them. Write a reformulated query that is more specific than the original query but still closely connected to it. You will be given:
- An underspecified user query
- ScholarQA's LLM-generated answer, which includes section titles, content, and citations
- A conversation history with clarifying questions and answers.

Follow these steps:

    1. Read the query.
    2. Read the LLM-generated answer, including the section titles, content, and citations.
    3. Read the conversation history with clarifying questions and answers.
    4. Taking inspiration from the answer's section titles, content, and citations write 3 reformulated queries that are more specific than the original query, but still related to it.
    5. Return your output in the following JSON format: {{"reformulated1": "reformulated query", "reformulated2": "second reformulated query", 'reformulated3': "third reformulated query"}}. Do not provide any additional information or explanation.
'''

    user_prompt = f'''LLM-Generated Answer:\n{llm_answer}\n\n
Original Query:\n{original_query}\n\n
Conversation History:\n{json.dumps(clarifying, indent=2)}\n\n
    
Reformulated queries in JSON Output: {{"reformulated1": "", "reformulated2": "", "reformulated3": ""}}
'''

    # insert system prompt at the beginning of list
    messages =  [
                    {'role': 'developer', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ]

    response = get_response(messages, _model='gpt-4.1', _max_tokens=300)
    
    return response

# Example usage:
# original_query = "What are the benefits of using transformers in NLP?"
# llm_answer = "<LLM-generated answer with sections, content, citations>"
# print(prompt_gpt41_for_specific_queries(original_query, llm_answer))