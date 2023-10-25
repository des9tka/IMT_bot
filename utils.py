import codecs
import datetime
import subprocess
import time
from ctypes import cast, POINTER
import gtts
import psutil
import pyautogui
import requests
from aiogram import types
from aiogram.fsm.context import FSMContext
from bardapi import Bard
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, ISimpleAudioVolume
from bs4 import BeautifulSoup
from urllib.request import urlopen
import instascrape

from config import BARD_TOKEN, OPEN_WEATHER_TOKEN

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))


def cast_to_message_photo(image_path):
    image = types.FSInputFile(image_path)
    return image


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
    opened = False

    windows = pyautogui.getWindowsWithTitle(app)

    for window in windows:
        if app.lower() in window.title.lower():
            window.activate()
            window.maximize()
            opened = True

    if not opened:
        pyautogui.hotkey("win")
        time.sleep(1)
        pyautogui.write(app)
        time.sleep(1)
        pyautogui.press("enter")
        time.sleep(3)


def get_answer(query):
    return Bard(token=BARD_TOKEN).get_answer(query)['content']


def get_image_answer(query, image=None):
    """Returns the answer from Bard."""

    response = requests.post(
        "https://api.bard.ai/v2/answer",
        headers={"Authorization": f"Bearer {BARD_TOKEN}"},
        files={"image": open(image, "rb")},
        data={"query": query},
        verify=False,
    )

    return response.json()["content"]


def get_weather(city):
    response = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={OPEN_WEATHER_TOKEN}')
    try:
        weather = response.json()[0]
    except (Exception,):
        return 'Error'
    lon = weather['lon']
    lat = weather['lat']

    response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?&lat={lat}&lon={lon}&appid={OPEN_WEATHER_TOKEN}&units=metric')
    weather = response.json()

    res_weather = {
        'name': weather['name'],
        'country': weather['sys']['country'],
        'temp': weather['main']['temp'],
        'temp_feels': weather['main']['feels_like'],
        'max_temp': weather['main']['temp_max'],
        'min_temp': weather['main']['temp_min'],
        'wind_speed': weather['wind']['speed'],
        'sunrise': datetime.datetime.fromtimestamp(weather['sys']['sunrise']).strftime('%H:%M'),
        'sunset': datetime.datetime.fromtimestamp(weather['sys']['sunset']).strftime('%H:%M'),
        'time_now': datetime.datetime.fromtimestamp(weather['dt']).strftime('%H:%M'),
        'clouds': weather['clouds']['all'],
        'description': weather['weather'][0]['description'],
        'main_weather': weather['weather'][0]['main']
    }

    try:
        rain_per_hour = weather['rain']['1h']
        res_weather['rain_per_hour'] = rain_per_hour
    except (Exception,):
        res_weather['rain_per_hour'] = 0

    return res_weather


def text_to_speach(text, language='ru-RU'):
    language = language.split('-')
    tts = gtts.gTTS(text=text, lang=language[0])
    tts.save("Voice assistant reply.")


def convert_video_to_mp3(input_video, output_audio):
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", input_video,
        "-vn",
        "-acodec", "libmp3lame",
        "-ab", "320k",
        "-ar", "44100",
        "-y",
        output_audio
    ]
    try:
        subprocess.run(ffmpeg_cmd, check=True)
    except subprocess.CalledProcessError as e:
        raise Exception('Converting failed.')


async def open_video_via_browser(browser, query):
    open_app(browser)
    pyautogui.hotkey('ctrl', 't')
    time.sleep(1)

    if query.startswith('https:'):
        pyautogui.write(query)
    else:
        pyautogui.write(f'https://www.youtube.com/search?q={query}')

    time.sleep(1)
    pyautogui.press('enter')

    time.sleep(2)
    return f'"{query}" video was successfully opened through {browser} opened.'


async def search_via_browser(browser, query):
    pyautogui.hotkey('ctrl', 't')
    time.sleep(1)
    pyautogui.write(query)
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(2)
    return f'"{query}" was successfully opened {browser} opened.'


async def keyboard_write(message):
    query_list = message.text.lower().replace('/key ', '').split(' ')
    keys = list(filter(is_not_empty, query_list))
    print(keys)
    print(len(keys))
    print(len(keys[0]))

    if keys[0].lower() == 'exit':
        pass

    elif len(keys) == 1 and keys[0] in ['ctrl', 'space', 'shift', 'alt', 'tab', 'win', 'capslock', 'enter', 'backspace']:
        print(1)
        key = keys[0]
        pyautogui.press(key)

    elif len(keys) == 1 and keys[0] not in ['ctrl', 'space', 'shift', 'alt', 'tab', 'win', 'capslock', 'enter', 'backspace']:
        print(2)
        pyautogui.write(keys[0])

    elif len(keys) == 2 and keys[0] in ['ctrl', 'space', 'shift', 'alt', 'tab', 'win', 'capslock', 'enter', 'backspace']:
        print(3)
        key1 = keys[0]
        key2 = keys[1]
        pyautogui.hotkey(key1, key2)

    elif len(keys) == 2 and keys[0] in ['ctrl', 'space', 'shift', 'alt', 'tab', 'win', 'capslock', 'enter', 'backspace']:
        print(4)
        key1 = keys[0]
        key2 = keys[1]
        pyautogui.hotkey(key1, key2)

    elif len(keys) >= 2 and keys[0] not in ['ctrl', 'space', 'shift', 'alt', 'tab', 'win', 'capslock', 'enter', 'backspace']:
        print(5)
        pyautogui.write(message.text.lower().replace('/key ', ''))

    elif len(keys) == 3 and keys[0] in ['ctrl', 'space', 'shift', 'alt', 'tab', 'win', 'capslock', 'enter', 'backspace', 'delete']:
        print(6)
        key1 = keys[0]
        key2 = keys[1]
        key3 = keys[2]
        pyautogui.hotkey(key1, key2, key3)

    else:
        await message.answer('Something went wrong, input keys and try again.')


def download_video_from_tiktok(link):
    cookies = {
        '_gid': 'GA1.2.1221201842.1698218485',
        '_gat_UA-3524196-6': '1',
        '_ga': 'GA1.2.1056017198.1696323883',
        '_ga_ZSF3D6YSLC': 'GS1.1.1698218484.2.1.1698218534.0.0.0',
    }

    headers = {
        'authority': 'ssstik.io',
        'accept': '*/*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        # 'cookie': '_gid=GA1.2.1221201842.1698218485; _gat_UA-3524196-6=1; _ga=GA1.2.1056017198.1696323883; _ga_ZSF3D6YSLC=GS1.1.1698218484.2.1.1698218534.0.0.0',
        'hx-current-url': 'https://ssstik.io/en',
        'hx-request': 'true',
        'hx-target': 'target',
        'hx-trigger': '_gcaptcha_pt',
        'origin': 'https://ssstik.io',
        'referer': 'https://ssstik.io/en',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Opera GX";v="102"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 OPR/102.0.0.0',
    }

    params = {
        'url': 'dl',
    }

    data = {
        'id': link,
        'locale': 'en',
        'tt': 'WHB4dFhl',
    }

    response = requests.post('https://ssstik.io/abc', params=params, cookies=cookies, headers=headers, data=data)
    download_soup = BeautifulSoup(response.text, 'html.parser')
    download_link = download_soup.a['href']

    mp4_file = urlopen(download_link)

    with open('tiktok_video.mp4', 'wb') as file:
        while True:
            data = mp4_file.read(4096)
            if data:
                file.write(data)
            else:
                break
    return download_link


def download_from_inst(link):
    cookies = {
        'random_n': 'eyJpdiI6InV1MzgvRUhpeUNxUkwzOXhnKzZxVlE9PSIsInZhbHVlIjoiKzBUMy9VZCtjdUozV2Q1bUNPY0ZPbHk4MnhYOWJXaUFoZkQ1dGhVQ0lJaEZDNVhvSkY1RENxMjNyRDBjRmk5YiIsIm1hYyI6IjUxZTU4ZTFhZjI3OGZkMzE0MTRkOWUzZTM4MzIxNGYxZDc0NmY2NWRjNzNmNGEzZjM1YTgyN2I4YTRiNWM3NzMiLCJ0YWciOiIifQ%3D%3D',
        'SLG_G_WPT_TO': 'ru',
        'SLG_GWPT_Show_Hide_tmp': '1',
        'SLG_wptGlobTipTmp': '1',
        'XSRF-TOKEN': 'eyJpdiI6IjFxREZjOVpoNFZ3aXdkS29seWw3SEE9PSIsInZhbHVlIjoiQ0ZVdUMwV1RXeVkxWDFCYjJ0bjlpUUU3U2xRaUNXS1RjeUtJbEtBdXhiKy93T1llMkhnemxUU3R3RFIrM09jNkR3WDFOTHdjQnZFTjJpTUNGQzJtMkkvRW4zMlo5bUdvcklFQ2Z6ZmhpUnFFUUxJekg1RWtzVTNZOUIwdXpOZzEiLCJtYWMiOiIxZGI2YzY5MTE4ZTJkMmRhMzc5MzU3OWJhZWVlOTc1MDkxZWE1ZTYyNTcxMDI0NjU5MDU2NjY4NWQxZTkzNTk5IiwidGFnIjoiIn0%3D',
        'sssinstagram_session': 'eyJpdiI6Ikp6aVE4T0hLaXF0anNpMzdtQk12L0E9PSIsInZhbHVlIjoicFNIMmoreDA0TDl1WWYzQlFyNVM5WGViK0dUQnJaZUg5NklFeTZhQWhGb3RNbjZWSER1ZFcrcHBvYWJVMFJnZk95aDFlWm56bFJsbzN0RGhkWUpSVURGVkUrOTVOelpJODBIWHg3QlFjdHo0dW90VTdyMW1oV3RTWjUzdmN3c1QiLCJtYWMiOiI0NWJjYTJiYzgyODQ2OWUxNjA5ODBmNTg0NWMxY2IyNGQzODk2ZTIzNmM0NDY3ODFhMTE2ZTRjYjkwNmM1NThlIiwidGFnIjoiIn0%3D',
    }

    headers = {
        'authority': 'sssinstagram.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/json;charset=UTF-8',
        # 'cookie': 'random_n=eyJpdiI6InV1MzgvRUhpeUNxUkwzOXhnKzZxVlE9PSIsInZhbHVlIjoiKzBUMy9VZCtjdUozV2Q1bUNPY0ZPbHk4MnhYOWJXaUFoZkQ1dGhVQ0lJaEZDNVhvSkY1RENxMjNyRDBjRmk5YiIsIm1hYyI6IjUxZTU4ZTFhZjI3OGZkMzE0MTRkOWUzZTM4MzIxNGYxZDc0NmY2NWRjNzNmNGEzZjM1YTgyN2I4YTRiNWM3NzMiLCJ0YWciOiIifQ%3D%3D; SLG_G_WPT_TO=ru; SLG_GWPT_Show_Hide_tmp=1; SLG_wptGlobTipTmp=1; XSRF-TOKEN=eyJpdiI6IjFxREZjOVpoNFZ3aXdkS29seWw3SEE9PSIsInZhbHVlIjoiQ0ZVdUMwV1RXeVkxWDFCYjJ0bjlpUUU3U2xRaUNXS1RjeUtJbEtBdXhiKy93T1llMkhnemxUU3R3RFIrM09jNkR3WDFOTHdjQnZFTjJpTUNGQzJtMkkvRW4zMlo5bUdvcklFQ2Z6ZmhpUnFFUUxJekg1RWtzVTNZOUIwdXpOZzEiLCJtYWMiOiIxZGI2YzY5MTE4ZTJkMmRhMzc5MzU3OWJhZWVlOTc1MDkxZWE1ZTYyNTcxMDI0NjU5MDU2NjY4NWQxZTkzNTk5IiwidGFnIjoiIn0%3D; sssinstagram_session=eyJpdiI6Ikp6aVE4T0hLaXF0anNpMzdtQk12L0E9PSIsInZhbHVlIjoicFNIMmoreDA0TDl1WWYzQlFyNVM5WGViK0dUQnJaZUg5NklFeTZhQWhGb3RNbjZWSER1ZFcrcHBvYWJVMFJnZk95aDFlWm56bFJsbzN0RGhkWUpSVURGVkUrOTVOelpJODBIWHg3QlFjdHo0dW90VTdyMW1oV3RTWjUzdmN3c1QiLCJtYWMiOiI0NWJjYTJiYzgyODQ2OWUxNjA5ODBmNTg0NWMxY2IyNGQzODk2ZTIzNmM0NDY3ODFhMTE2ZTRjYjkwNmM1NThlIiwidGFnIjoiIn0%3D',
        'origin': 'https://sssinstagram.com',
        'sec-ch-ua': '"Opera";v="103", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 OPR/103.0.0.0',
        'x-requested-with': 'XMLHttpRequest',
        'x-xsrf-token': 'eyJpdiI6IjFxREZjOVpoNFZ3aXdkS29seWw3SEE9PSIsInZhbHVlIjoiQ0ZVdUMwV1RXeVkxWDFCYjJ0bjlpUUU3U2xRaUNXS1RjeUtJbEtBdXhiKy93T1llMkhnemxUU3R3RFIrM09jNkR3WDFOTHdjQnZFTjJpTUNGQzJtMkkvRW4zMlo5bUdvcklFQ2Z6ZmhpUnFFUUxJekg1RWtzVTNZOUIwdXpOZzEiLCJtYWMiOiIxZGI2YzY5MTE4ZTJkMmRhMzc5MzU3OWJhZWVlOTc1MDkxZWE1ZTYyNTcxMDI0NjU5MDU2NjY4NWQxZTkzNTk5IiwidGFnIjoiIn0=',
    }

    json_data = {
        'link': link,
        'token': '',
    }

    response = requests.post('https://sssinstagram.com/ru/r', cookies=cookies, headers=headers, json=json_data)
    result = response.json()
    link = None

    if 'urlDownloadable' in response.text:
        link = result['data']['items'][0]['urls'][0]['urlDownloadable']

        response = requests.get(link)
        if response.status_code == 200:
            with open("inst_video.mp4", "wb") as file:
                file.write(response.content)

        else:
            raise Exception(f"Failed to download video: {response.status_code}")

    elif 'pictureUrl' in response.text:
        link = result['data']['items'][0]['pictureUrl']

        response = requests.get(link)
        if response.status_code == 200:
            with open("inst_image.jpg", "wb") as file:
                file.write(response.content)
        else:
            raise Exception(f"Failed to download video: {response.status_code}")

    else:
        print('Downloading only for pictures and videos.')

    return link
