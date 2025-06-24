import json
import time
import os
from collections import defaultdict
from openai import OpenAI

# EXAMPLE CLUSTER to show the model
example_queries = [
    "is Standard Implants with Sinus Floor Elevation are better than Short Dental Implants",
    "are Short Dental Implants have higher Marginal Bone Loss compared to Standard Implants?",
    "Are there specific considerations for prosthetic selection in short implants?",
    "Risk Assessment for Short Implants",
    "what risk factors impact on the short implants",
    "Dental implant surgery in patients on antithrombotic medications",
    "short implant design",
    "dental implant thread design",
    "complications in the implant surgery",
    "number of dental implants in the treatment"
]

def load_queries_by_user(jsonl_path):
    user_queries = defaultdict(list)
    with open(jsonl_path, "r") as f:
        for line in f:
            row = json.loads(line)
            if "user_id" in row and "query" in row:
                user_queries[row["user_id"]].append(row["query"])
    return user_queries

def make_prompt(user_queries):
    example_list = "\n".join(f"- {q}" for q in example_queries)
    user_query_list = "\n".join(f"- {q}" for q in user_queries)

    _system_prompt = """
You are an assistant that groups user-submitted queries by semantic and topical similarity.

Follow these steps:

1. Group queries that are reformulations of each other, semantically or topically related. Note that some query may not fit into any group.
2. Remove near-duplicates (e.g., minor rewordings or paraphrases).
3. Use the provided example to guide your interpretation of related queries.
4. Return your output in the following JSON format: {"cluster1": ["query1", "query2"], "cluster2": ["query3"]}. Each cluster should contain a list of deduplicated, related queries.

Only return the JSON object. Do not include explanations or comments."""


    _user_prompt = f"""Here is an example list of related queries:
{example_list}

Now, consider the following user-submitted queries:
{user_query_list}
"""
    
    return _system_prompt, _user_prompt

def analyze_user_queries(queries, model="gpt-4.1", max_tokens=1500):
    
    system_prompt, user_prompt = make_prompt(queries)
    
    client = OpenAI(
        api_key = open(os.path.join('../../PhD/apikeys', 'ai2_openai_key')).read().strip()
    )

    attempts = 0
    max_attempts = 3
    response = 'None'

    while attempts < max_attempts:
        try:
            response = client.chat.completions.create(
                model=model,
                temperature=0.3,
                max_completion_tokens=max_tokens,
                messages = [
                    {'role': 'developer', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ]
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

def main(jsonl_file_path, output_file_path):
    user_queries = load_queries_by_user(jsonl_file_path)

    with open(output_file_path, "w") as out_file:
        for user_id, queries in user_queries.items():
            print(f"Processing user {user_id} with {len(queries)} queries...")
            try:
                result = analyze_user_queries(queries)
                result["user_id"] = user_id
                out_file.write(json.dumps(result) + "\n")
            except Exception as e:
                print(f"Error with user {user_id}: {e}")

if __name__ == "__main__":
    dt = "sqa"
    input_p = os.path.join('data', f'{dt}_filtered_returning.jsonl')  # Path to your JSONL file
    output_p = os.path.join('output', f'{dt}_clustered.jsonl')  # Path to save the output JSONL file
    main(input_p, output_p)  # Change to your actual JSONL path

