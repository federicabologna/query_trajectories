# Imports
import time
import os
import argparse
import json
import numpy as np
import pandas as pd
from openai import OpenAI

def get_response(_system_prompt, _user_prompt, _model='gpt-4.1', _max_tokens=300):

    client = OpenAI(
        api_key = open(os.path.join('../../PhD/apikeys', 's2_openai_key')).read().strip()
    )

    attempts = 0
    max_attempts = 3
    response = 'None'

    while attempts < max_attempts:
        try:
            response = client.chat.completions.create(
                model= _model,
                max_completion_tokens=_max_tokens,
                messages = [
                    {'role': 'developer', 'content': _system_prompt},
                    {'role': 'user', 'content': _user_prompt}
                ]
            )
            
            _answer = response.choices[0].message.content.strip()
            print(_answer)

            if 'Error' not in _answer and len(_answer) > 0:
                break

        except Exception as e:
            print(f'Error {e}. Sleeping 3 seconds ...')
            time.sleep(3)
            if attempts == max_attempts-1:
                _answer = f'Error {e}'

        attempts += 1
        if _model == 'o3':
            time.sleep(2)
        else:
            time.sleep(0.5)

    return _answer


def main():

    # File locations
    dir = os.getcwd()
    data_dir = os.path.join(dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    output_dir = os.path.join(dir, 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    sample = []
    with open(os.path.join('data', 'os_sqa_annotated.jsonl'), 'r') as f:
        for line in f:
            sample.append(json.loads(line.strip()))
            
    # random.seed(42)
    # random.shuffle(sample)

    sys_prompt = f'''You are an expert researcher. You will read a query submitted to a scientific QA system. You will assign one of three labels:
0 if the query is general: it mentions topics and concepts but not how they are related, without details, nor context.
1 if the query is specific: it mentions topics and concepts, how they are related, with some details or contenxt
Here are five examples of queries and their labels to guide your annotation:

Query: {sample[0]['query']} - Label: {sample[0]['label']}
Query: {sample[1]['query']} - Label: {sample[1]['label']}
Query: {sample[2]['query']} - Label: {sample[2]['label']}
Query: {sample[3]['query']} - Label: {sample[3]['label']}
Query: {sample[4]['query']} - Label: {sample[4]['label']}

Follow these steps:

    1. Read the query.
    2. Determine if the query is General, Specific, or Very specific based on the definitions provided.
    3. Assign the appropriate label. Do not use any other labels or categories.
    4. Return your output in the following JSON format: {{"query": "the query text", "label": "the assigned label"}}. Do not provide any additional information or explanation.

Output:'''
    
    print(len(sample))
    print(sys_prompt)

    output_path = os.path.join(output_dir,  f'openscholar_gpt4-1_specificity2.jsonl')
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

            label = get_response(sys_prompt, us_prompt)
            d['label'] = json.loads(label)['label']
            print(d['label'])

            with open(output_path, 'a') as file:
                json.dump(d, file)
                file.write('\n') 

            end = time.time()  
            print(d['query_id'], end-start)


if __name__ == "__main__":
    main()