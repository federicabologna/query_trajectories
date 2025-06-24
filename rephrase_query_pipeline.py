#1 Make question worse
import os
import json
import random
from helpers.make_query_worse import remove_fraction_function_words
from helpers.scholar_qa_pipeline import get_scholar_qa_answer
from helpers.make_query_better import *
from model.response.generate_response import *


bad_dir = os.path.join('output', 'rephrase_queries', 'bad_qa')
better_dir_1 = os.path.join('output', 'rephrase_queries', 'better_qa_1')
better_dir_2 = os.path.join('output', 'rephrase_queries', 'better_qa_2')
if not os.path.exists(bad_dir):
    os.makedirs(bad_dir)
if not os.path.exists(better_dir_1):
    os.makedirs(better_dir_1)
if not os.path.exists(better_dir_2):
    os.makedirs(better_dir_2)

with open(os.path.join('data', 'human_answers.json'), 'r') as file:
    data = json.load(file)

# MAKE QUERY WORSE AND GET ANSWER
for d in data: 
    query_id = d['id']
    original_query = d['input']

    if os.path.exists(os.path.join(bad_dir, f'{query_id}.json')):
        with open(os.path.join(bad_dir, f'{query_id}.json'), 'r') as file:
            bad_qa = json.load(file)
            bad_query = bad_qa['input']
            bad_answer = bad_qa['output']
            print(f"Bad Query already exists for {query_id}. Skipping...")
            print(f"Original Query: {original_query}",
                  f"\nWorse Query: {bad_query}")  
    else:
        print(f"Making query worse for {query_id}...")
        bad_query = remove_fraction_function_words(original_query, fraction=0.7)
        print(f"Original Query: {original_query}",
              f"\nWorse Query: {bad_query}")   
        
        # 2 Prompt with question and answer
        # bad_answer = get_scholar_qa_answer(bad_query)
        bad_answer = get_monster_answer(bad_query)
        bad_qa = {'original_query': original_query,
                'input': bad_query,
                'output': bad_answer}
        with open(os.path.join(bad_dir, f'{query_id}.json'), 'w') as file:
            json.dump(bad_qa, file)
            file.write('\n')
    
    


    # FIRST METHOD
    #3 Reformulate question
    if f'{query_id}_betterq_1.json' in os.listdir(better_dir_1):
        print(f"Better Queries Version 1 for {query_id} already exist. Skipping...")
        with open(os.path.join(better_dir_1, f'{query_id}_betterq_1.json'), 'r') as file:
            better_queries_1 = json.load(file)
    else:
        better_queries_1 = reformulate_given_answer(bad_query, bad_answer)
        with open(os.path.join(better_dir_1, f'{query_id}_betterq_1.json'), 'w') as file:
            json.dump(better_queries_1, file)
            file.write('\n')
    
    #4 Answer to reformulated question
    if f'{query_id}_0.json' in os.listdir(better_dir_1):# and f'{query_id}_2.json' in os.listdir(better_dir_1) and f'{query_id}_3.json' in os.listdir(better_dir_1):
        print(f"Better Answers Version 1 for {query_id} already exist. Skipping...")
    else:
        n = 0
        # for key, better_query in better_queries_1.items():
        #     n += 1
        #     print(f"{key}: {better_query}")
        better_query = list(better_queries_1.values())[0]
        better_answer_1 = get_scholar_qa_answer(better_query)
        better_qa_1 = {'better_query': better_query,
                    'better_answer': better_answer_1}

        with open(os.path.join(better_dir_1, f'{query_id}_{n}.json'), 'w') as file:
            json.dump(better_qa_1, file)
            file.write('\n')




    # SECOND METHOD
    if f'{query_id}_betterq_2.json' in os.listdir(better_dir_2):
        print(f"Better Queries Version 2 for {query_id} already exist. Skipping...")
        with open(os.path.join(better_dir_2, f'{query_id}_betterq_2.json'), 'r') as file:
            better_d = json.load(file)
        better_queries_2 = better_d['better_queries_2']
        clarifying_information = better_d['clarifying_information']
            
    else:
        # 5 Get clarifying questions
        clarifying_questions = asking_clarifyingq(bad_query, bad_answer)
        # 6 Get answers to clarifying questions
        clarifying_information = []
        for id, cq in clarifying_questions.items():
            print(f"Clarifying Question: {cq}")
            clarifying_answer = simulated_user(bad_query, bad_answer, cq)
            print(f"Clarifying Answer: {clarifying_answer}")
            
            clarifying_dict = {f'clarifying_question{id[-1]}': cq,
                            f'clarifying_answer{id[-1]}': clarifying_answer}
            clarifying_information.append(clarifying_dict)
        
        # 7 Reformulate question with clarifying information
        better_queries_2 = reformulate_given_clarification(bad_query, bad_answer, clarifying_information)
        with open(os.path.join(better_dir_2, f'{query_id}_betterq_2.json'), 'w') as file:
            json.dump({'clarifying_information': clarifying_information,
                       'better_queries_2': better_queries_2}, file)
            file.write('\n')
    
    
    if f'{query_id}_0.json' in os.listdir(better_dir_2):# and f'{query_id}_2.json' in os.listdir(better_dir_2) and f'{query_id}_3.json' in os.listdir(better_dir_2):
        print(f"Better Answers Version 2 for {query_id} already exist. Skipping...")
    else:
        n = 0
        # for key, better_query in better_queries_2.items():
        #     n += 1
        #     print(f"{key}: {better_query}")
        better_query = list(better_queries_2.values())[0]
        better_answer_2 = get_scholar_qa_answer(better_query)
        better_qa_2 = {'clarifying_information': clarifying_information,
                    'better_query': better_query,
                    'better_answer': better_answer_2} 
        with open(os.path.join(better_dir_2, f'{query_id}_{n}.json'), 'w') as file:
            json.dump(better_qa_2, file)
            file.write('\n')
