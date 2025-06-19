# Imports
import time
import os
import random
import argparse
import json
import requests
import numpy as np
import pandas as pd
from   sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, accuracy_score, classification_report
from transformers import AutoTokenizer, AutoModelForCausalLM


def get_response(_system_prompt, _user_prompt, _model='llama3:latest', _max_tokens=300):

    data = {
        "model": _model,
        "messages": [
            {"role": "system","content": _system_prompt},
            {"role": "user","content": _user_prompt}
            ],
        "stream": False
    }
    
    headers = {
        'Content-Type': 'application/json'
    }

    attempts = 0
    max_attempts = 3
    response = 'None'

    while attempts < max_attempts:
        try:
            response = requests.post('http://localhost:11434/api/chat', headers=headers, json=data)
          
            _answer = response.json()['message']['content']

            if 'Error' not in _answer and len(_answer) > 250:
                break

        except Exception as e:
            print(f'Error {e}. Sleeping 3 seconds ...')
            time.sleep(3)
            if attempts == max_attempts-1:
                _answer = f'Error {e}'

        attempts += 1
        if _model == 'gpt-4-better':
            time.sleep(2)
        else:
            time.sleep(0.5)

    return _answer
 

def main():

    # parser = argparse.ArgumentParser()
    # parser.add_argument('--n_shots', required=True, type=str)
    # args = parser.parse_args()
    # number_shots = args.n_shots

    # File locations
    dir = os.getcwd()
    data_dir = os.path.join(dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    output_dir = os.path.join(dir, 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    sample = []
    with open(os.path.join('data', 'OS_queries_0225_annotated.jsonl'), 'r') as f:
        for line in f:
            sample.append(json.loads(line.strip()))
            
    # random.seed(42)
    # random.shuffle(sample)

    sys_prompt = f'''You are an expert researcher. You will read a query submitted to a scientific QA system. You will assign one of three labels:
                    1 = General if the query mentions broad topics or concepts.
                    2 = Specific if the query mentions specific topics or concepts.
                    
                    Here are five examples of queries and their labels to guide your annotation:
                    
                    Query: {sample[0]['query']} - Label: {sample[0]['label']}
                    Query: {sample[1]['query']} - Label: {sample[1]['label']}
                    Query: {sample[2]['query']} - Label: {sample[2]['label']}
                    Query: {sample[3]['query']} - Label: {sample[3]['label']}
                    Query: {sample[4]['query']} - Label: {sample[4]['label']}
                    
                    Follow these steps:
                    
                        1. Read the query.
                        2. Determine if the query is General, Specific, or Very specific.
                        3. Assign the appropriate label based on the definitions provided.
                        
                    Do not provide any additional information or explanation.'''
    
    print(len(sample))
    print(sys_prompt)

    output_path = os.path.join(output_dir,  f'openscholar_ollama_specificity.jsonl')
    collected_ids = set()
    if os.path.exists(output_path):
        with open(output_path, 'r') as f:
            for line in f:
                dct = json.loads(line.strip())
                collected_ids.add(dct['query_id'])

    print(len(collected_ids))

    for d in sample[5:]:  # Skip the first 5 examples used for the system prompt

        if d['query_id'] not in collected_ids:

            start = time.time()

            us_prompt = f"Query:\n{d['query']}\n\nLabel:"

            d['label'] = get_response(sys_prompt, us_prompt)

            with open(output_path, 'a') as file:
                json.dump(d, file)
                file.write('\n') 

            end = time.time()  
            print(d['query_id'], end-start)


if __name__ == "__main__":
    main()