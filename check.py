import json
import time

def trying(_answer):  

    attempts = 0
    max_attempts = 3
    response = 'None'

    while attempts < max_attempts:
        
        try:
            answer_dict = json.loads(_answer)
            break

        except Exception as e:
            print(f'Error {e}. Sleeping 3 seconds ...')
            time.sleep(3)
            if attempts == max_attempts-1:
                _answer = f'Error {e}'

        attempts += 1
        time.sleep(0.5)
    
    return answer_dict


if __name__ == "__main__":
    answer = '''{"response": "This is a test answer."}'''
    print(type(trying(answer)))
    
    