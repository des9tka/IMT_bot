import codecs
import datetime
import subprocess
import time
import pyautogui
import gtts
import psutil
import openai
from bardapi import Bard
from openai.error import InvalidRequestError

from config import BARD_TOKEN


# def format_answer(answer):
#     answer = answer.replace('\n', ' ')
#     answer = answer.replace('*', '')
#     return answer


def close_app(app):
    pid = None
    output = subprocess.check_output(['tasklist'])
    decoded_output = codecs.decode(output, 'latin-1')

    # 1
    for line in decoded_output.splitlines():
        if app in line:
            pid = line.split()[1]
            break
    if pid:
        subprocess.call(['taskkill', '/F', '/PID', pid])
        return f'{app.capitalize()} was successfully closed.'

    # 2
    processes = psutil.process_iter()
    for process in processes:
        if app.lower() in process.name().lower():
            process.terminate()
            return f'{app.capitalize()} was successfully closed.'

    return f'{app.capitalize()} is not open, not global available, or has wrong name input (You can use /task_manager for listing all tasks).'


def open_app(app):
    pyautogui.hotkey("win")
    time.sleep(1)
    pyautogui.write(app)
    time.sleep(1)
    pyautogui.press("enter")
    time.sleep(5)
    processes = psutil.process_iter()
    for process in processes:
        if app.lower() in process.name():
            return f'{app.capitalize()} was successfully open.'
    return f'{app.capitalize()} wasnt find, not global available, or has wrong name input (You can use /task_manager for listing all tasks).'


def got_answer(query):
    return Bard(token=BARD_TOKEN).get_answer(query)['content']


def generate_image(prompt, num_image=1, size='512x512', output_format='url'):
    """
    params:
        prompt (str):
        num_image (int):
        size (str):
        output_format (str):
    """
    try:
        images = []
        response = openai.Image.create(
            prompt=prompt,
            n=num_image,
            size=size,
            response_format=output_format
        )
        if output_format == 'url':
            for image in response['data']:
                images.append(image.url)
        elif output_format == 'b64_json':
            for image in response['data']:
                images.append(image.b64_json)
        return {'created': datetime.datetime.fromtimestamp(response['created']), 'images': images}
    except InvalidRequestError as e:
        print(e)


def text_to_speach(text, language='ru-RU'):
    language = language.split('-')
    tts = gtts.gTTS(text=text, lang=language[0])
    tts.save("Voice assistant reply.")
