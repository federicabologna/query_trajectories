from scholarqa.rag.reranker.modal_engine import ModalReranker
from scholarqa.rag.retrieval import PaperFinderWithReranker
from scholarqa.rag.retriever_base import FullTextRetriever
from scholarqa import ScholarQA
from scholarqa.llms.constants import CLAUDE_37_SONNET
import time


def get_scholar_qa_answer(query):

    #Retrieval class/steps
    retriever = FullTextRetriever(n_retrieval=256, n_keyword_srch=20) #full text and keyword search

    #Reranker if deployed on Modal, modal_app_name and modal_api_name are modal specific arguments.
    #Please refer https://github.com/allenai/ai2-scholarqa-lib/blob/aps/readme_fixes/docs/MODAL.md for more info 
    reranker = ModalReranker(app_name='ai2-scholar-qa', api_name='inference_api', batch_size=256, gen_options=dict())

    #wraps around the retriever with `retrieve_passages()` and `retrieve_additional_papers()`, and reranker with rerank()
    #any modifications to the retrieval output can be made here
    paper_finder =  PaperFinderWithReranker(retriever, reranker, n_rerank=50, context_threshold=0.5)

    #For wrapper class with MultiStepQAPipeline integrated
    scholar_qa = ScholarQA(paper_finder=paper_finder, llm_model=CLAUDE_37_SONNET, run_table_generation=False) #llm_model can be any litellm model
    # GPT_4o
    # GPT_4o_MINI
    
    attempts = 0
    max_attempts = 3

    while attempts < max_attempts:
        try:
            answer = scholar_qa.answer_query(query)
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