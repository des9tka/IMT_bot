import codecs
import datetime
import subprocess
import time
from ctypes import cast, POINTER

import gtts
import pip
import psutil
import pyautogui
import requests
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from bardapi import Bard
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, ISimpleAudioVolume

from config import BARD_TOKEN

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))


def sessions_audio_kb():
    keyboard = []
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process:
            name = session.Process.name().split('.')[0]
            keyboard.append([InlineKeyboardButton(text=f'{name}', callback_data=f'session_{session.Process.name()}')])

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)


def master_volume_up():
    current_volume = volume.GetMasterVolumeLevel()
    if current_volume < -3.0:
        volume.SetMasterVolumeLevel(current_volume + 3.0, None)


def master_volume_down():
    current_volume = volume.GetMasterVolumeLevel()
    if current_volume > -65.0:
        volume.SetMasterVolumeLevel(current_volume - 3.0, None)


def master_volume_mute_unmute():
    if volume.GetMute() == 0:
        volume.SetMute(1, None)
    else:
        volume.SetMute(0, None)


def master_volume_max_min():
    current_volume = volume.GetMasterVolumeLevel()
    if current_volume >= -50.0:
        volume.SetMasterVolumeLevel(-65.0, None)
    elif current_volume <= 50.0:
        volume.SetMasterVolumeLevel(0.0, None)


def set_master_volume(value=None, cast_value=None):
    if not cast_value:
        volume.SetMasterVolumeLevelScalar(value, None)
    else:
        volume.SetMasterVolumeLevel(cast_value, None)


def is_not_empty(string):
    return string != ''


async def app_volume_up(state: FSMContext):
    sessions = AudioUtilities.GetAllSessions()

    for session in sessions:
        session_volume = session._ctl.QueryInterface(ISimpleAudioVolume)
        current_volume = session.SimpleAudioVolume.GetMasterVolume()

        if session.Process and session.Process.name() == state and current_volume < 1.0:
            session_volume.SetMasterVolume(current_volume + 0.05, None)


async def app_volume_down(state: FSMContext):
    sessions = AudioUtilities.GetAllSessions()

    for session in sessions:
        session_volume = session._ctl.QueryInterface(ISimpleAudioVolume)
        current_volume = session.SimpleAudioVolume.GetMasterVolume()

        if session.Process and session.Process.name() == state and current_volume > 0.0:
            session_volume.SetMasterVolume(current_volume - 0.05, None)


async def app_volume_mute_unmute(state: FSMContext):
    sessions = AudioUtilities.GetAllSessions()

    for session in sessions:
        session_volume = session._ctl.QueryInterface(ISimpleAudioVolume)

        if session.Process and session.Process.name() == state and session_volume.GetMute() == 1:
            session_volume.SetMute(0, None)
        elif session.Process and session.Process.name() == state and session_volume.GetMute() == 0:
            session_volume.SetMute(1, None)


async def app_volume_max_min(state: FSMContext):
    sessions = AudioUtilities.GetAllSessions()

    for session in sessions:
        session_volume = session._ctl.QueryInterface(ISimpleAudioVolume)
        current_volume = session.SimpleAudioVolume.GetMasterVolume()

        if session.Process and session.Process.name() == state and current_volume >= 0.5:
            session_volume.SetMasterVolume(0.0, None)
        elif session.Process and session.Process.name() == state and current_volume < 0.5:
            session_volume.SetMasterVolume(1.0, None)


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


def get_answer(query):
    return Bard(token=BARD_TOKEN).get_answer(query)['content']


def get_answer2(query, image=None):
    """Returns the answer from Bard."""

    response = requests.post(
        "https://api.bard.ai/v2/answer",
        headers={"Authorization": f"Bearer {BARD_TOKEN}"},
        files={"image": open(image, "rb")},
        data={"query": query},
        verify=False,
    )

    return response.json()["content"]


# def generate_image(prompt, num_image=1, size='512x512', output_format='url'):
#     """
#     params:
#         prompt (str):
#         num_image (int):
#         size (str):
#         output_format (str):
#     """
#     try:
#         images = []
#         response = openai.Image.create(
#             prompt=prompt,
#             n=num_image,
#             size=size,
#             response_format=output_format
#         )
#         if output_format == 'url':
#             for image in response['data']:
#                 images.append(image.url)
#         elif output_format == 'b64_json':
#             for image in response['data']:
#                 images.append(image.b64_json)
#         return {'created': datetime.datetime.fromtimestamp(response['created']), 'images': images}
#     except InvalidRequestError as e:
#         print(e)


def text_to_speach(text, language='ru-RU'):
    language = language.split('-')
    tts = gtts.gTTS(text=text, lang=language[0])
    tts.save("Voice assistant reply.")

# def format_answer(answer):
#     answer = answer.replace('\n', ' ')
#     answer = answer.replace('*', '')
#     return answer
