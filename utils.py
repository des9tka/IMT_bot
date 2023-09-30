from bardapi import Bard

from config import BARD_TOKEN


def format_answer(answer):
    answer = answer.replace('\n', ' ')
    answer = answer.replace('*', '')
    return answer


def got_answer(query_):
    print(query_)
    if 'shortly' in query_ or 'briefly' in query_:
        answer = Bard(token=BARD_TOKEN).get_answer(str(query_ + ', answer shortly.'))['content']
    else:
        answer = Bard(token=BARD_TOKEN).get_answer(str(query_))['content']

    return format_answer(answer)
