from model.response.scholarqa.rag.reranker.modal_engine import ModalReranker
# from scholarqa.rag.reranker.reranker_base import CrossEncoderScores
from scholarqa.rag.retrieval import PaperFinderWithReranker
from scholarqa.rag.retriever_base import FullTextRetriever
from scholarqa.llms.constants import CLAUDE_37_SONNET, GPT_4o, GPT_4o_MINI
from scholarqa import ScholarQA

# from data import QueryPlans, Plan, PlanRequirement
# from enums import PersonalizationStrategy, PersonalizationFramework

import os
import time
import subprocess
import sys

from dotenv import load_dotenv
load_dotenv(dotenv_path='/.env')

def ensure_env_tokens():
    required_env_vars = ["S2_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "MODAL_TOKEN", "MODAL_TOKEN_SECRET"]
    missing = [var for var in required_env_vars if not os.getenv(var)]

    if missing:
        print("⚠️  Missing environment variables:", ", ".join(missing))
        print("🔧 Attempting to generate export script...")

        subprocess.run([sys.executable, "model/response/setup.py"])
        sys.exit(1)
    else:
        print(f"✅ All env variables set")

def get_monster_answer(query):
    # check all tokens are set
    ensure_env_tokens()

    retriever = FullTextRetriever(n_retrieval=256, n_keyword_srch=20)
    # reranker = CrossEncoderScores(model_name_or_path="mixedbread-ai/mxbai-rerank-large-v1") #sentence transformer
    reranker = ModalReranker(app_name='ai2-scholar-qa', api_name='inference_api', batch_size=256, gen_options=dict())
    
    paper_finder = PaperFinderWithReranker(retriever, reranker, n_rerank=50, context_threshold=0.5)
    scholar_qa = ScholarQA(paper_finder=paper_finder, llm_model=CLAUDE_37_SONNET, run_table_generation=False)


    attempts = 0
    max_attempts = 3

    while attempts < max_attempts:
        try:
            answer = scholar_qa.answer_query(query=query)
            if type(answer) is dict:
                break
        
        except Exception as e:
            print(f'Error {e}. Sleeping 1 second ...')
            time.sleep(1)
            if attempts == max_attempts-1:
                answer = f'Error {e}'
        
        attempts += 1
        time.sleep(0.5)
        
    return answer

if __name__ == "__main__":
    get_monster_answer("What are the key mechanisms for lipid nanoparticles (LNPs) to form biomolecular corona with various serum proteins and blood componen")