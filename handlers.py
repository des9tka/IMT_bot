import codecs
import datetime
import os
import subprocess
import time
import webbrowser
from functools import partial

import cv2
import keyboard
import numpy as np
import pyautogui
import speech_recognition as sr
from PIL import ImageGrab
from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from pydub import AudioSegment

import keyboards as kb
from config import bot
from filters import AdminFilter
from state import BotState
from utils import get_answer, text_to_speach, open_app, close_app, master_volume_up, master_volume_down, master_volume_mute_unmute, master_volume_max_min, sessions_audio_kb, set_master_volume, is_not_empty, \
    app_volume_up, app_volume_down, app_volume_max_min, app_volume_mute_unmute, get_weather

router_handler = Router()

language = 'ru-RU'
voice_assistant = 'off'


@router_handler.message(AdminFilter(), F.video)
async def cpt_video(message: types.Message):
    await message.answer('Video capturing in development... ')
    # Open the video file in binary mode.
    # with open(message.video, 'rb') as f:
    #     video_bytes = f.read()
    #
    # # Send the video file to Captions.AI.
    # response = requests.post(url='https://app.captions.ai/add-captions',
    #                          files={'video': video_bytes})


@router_handler.message(AdminFilter(), F.audio)
async def get_audio_id(message: types.Message):
    await message.answer(message.audio.file_id)


@router_handler.message(AdminFilter(), F.photo)
async def image_request(message: types.Message):
    file = await bot.get_file(message.photo[-1].file_id)
    await message.bot.download_file(file.file_path, "image.jpg")

    if message.caption.startswith('/ai'):
        # response = get_answer2(query=message.caption, image='image.jpg')
        # print(response)
        await message.answer('Image request to AI in development... ')

    elif message.caption.startswith('/resize'):
        img = cv2.imread('image.jpg')
        sizes = list(filter(is_not_empty, message.caption.replace('/resize ', '').split('x')))

        if len(sizes) > 2:
            await message.answer('Should be provided "width"x"high".')

        else:
            resized_img = cv2.resize(img, (int(sizes[0]), int(sizes[1])))
            cv2.imwrite('resized_image.jpg', resized_img)
            file = types.FSInputFile('resized_image.jpg')
            await message.answer_photo(file)

            os.remove('image.jpg')
            os.remove('resized_image.jpg')


@router_handler.message(AdminFilter(), F.voice)
async def audio_request(message: types.Message):
    try:
        audio_file = await bot.get_file(message.voice.file_id)

        await bot.download_file(audio_file.file_path, 'message_audio.ogg')

        audio = AudioSegment.from_file('message_audio.ogg', format='ogg')
        audio.export('message_audio.ogg', format='wav')
        recognizer = sr.Recognizer()

        with sr.AudioFile('message_audio.ogg') as source:
            audio_data = recognizer.record(source)

        transcription = recognizer.recognize_google(audio_data, language=language)

        os.remove('message_audio.ogg')

        await message.reply(f'You: {transcription}')
        reply = get_answer(transcription)
        await message.answer(f'AI: {reply}')
        if voice_assistant == 'on':
            file = types.FSInputFile('Voice assistant reply.')
            text_to_speach(reply, language)
            await bot.send_audio(chat_id=message.from_user.id, audio=file)
            os.remove('Voice assistant reply.')
    except (Exception,) as e:
        await message.answer(f'Something went wrong, check yor input language or input query and try again.\nMore details: {str(e)}')
        try:
            os.remove('message_audio.ogg')
            os.remove('Voice assistant reply.')
        except (Exception,):
            print(Exception)


@router_handler.message(AdminFilter(), F.sticker)
async def sticker_id(message: types.Message):
    await message.answer(f'Here is your`s sticker id: {message.sticker.file_id}')


@router_handler.message(AdminFilter(), F.text)
async def query(message: types.Message):
    if message.text == '/start':
        await message.answer_sticker(sticker='CAACAgIAAxkBAAOpZRf-yoxEiHWx8_ps5yU_67pi3woAAgEBAAJWnb0KIr6fDrjC5jQwBA')
        time.sleep(1)
        await message.answer('Nice to meet you, can i /help you?')

    elif message.text == '/help':
        await message.answer('Here some commands to use:'
                             '\n\n'
                             '<-----AI----->'
                             '\n- /ai + prompt (Prompt request to AI).'
                             '\n- /img + prompt (Generate image with AI).'
                             '\n- Voice message (Voice request to AI).'
                             '\n- Photo message + command + prompt (Commands:\n• /ai + prompt, \n• /resize + "width"x"high".'
                             '\n- Video (Capturing video by AI).'
                             '\n\n'
                             '<-----Remote Control----->'
                             '\n- /video + name/url (Find video in YouTube).'
                             '\n- /browser + prompt (Search info in browser).'
                             '\n- /screenshot + optional number quality (Qualities:\n• Nothing/1 (Screenshot with compression).\n• 2 (Screenshot in stock quality)).'
                             '\n- /open + app name (Open an app, should be global available).'
                             '\n- /close + app name (Close an app, should be global available).'
                             '\n- /key + hot key/keys (Remote keyboard input).'
                             '\n- /volume + optional value (Change value of volume, 0-100).'
                             '\n\n'
                             '<-----Additional----->'
                             '\n- /tech_support + query (Get in touch with our team).'
                             '\n- /weather + city (Get weather info to your city).'
                             '\n- /help (Watch list of all commands).'
                             '\n- /info (Useful info and F&Q).'
                             '\n\n'
                             '<-----Settings----->'
                             '\n- /sett (All settings).'
                             '\n- /comm_sett (Settings by commands).'
                             '\n- /voice_ass (Switch voice assistant reply mode, default `OFF`).'
                             '\n- /lang (Switch input/output language, default `Ru`).'
                             '\n- /task_manager (Watch list of PC tasks).'
                             '\n- /id (Find out your id).'
                             )

    elif message.text == '/lang':
        await message.answer(f'Your language is {language}. Choose new one:', reply_markup=kb.language_kb)

    elif message.text == '/voice_ass':
        await message.answer(f'Voice assistant --> {voice_assistant.upper()}', reply_markup=kb.voice_assistant_kb)

    elif '/img' in message.text:
        await message.answer('Image generation in developing...')
        # if message.text.replace('/img', '').replace(' ', '') == '':
        #     await message.answer('You should provide a prompt.')
        # else:
        #     image['prompt'] = message.text.replace('/img ', '')
        #     await message.answer('Okay, let`s choose size:', reply_markup=kb.image_size_kb)

    elif message.text == '/id':
        await message.answer(f'Your id: {message.from_user.id}')

    elif '/send' in message.text:
        text = message.text.replace('/send ', '')
        await bot.send_message(chat_id=5714917250, text=text)

    elif '/weather' in message.text:
        if message.text.replace('/weather', '').replace(' ', '') == '':
            await message.answer('You should provide a city.')
        else:
            city = message.text.replace('/weather', '').replace(' ', '')
            response = get_weather(city)

            if response == 'Error':
                await message.answer('Check the name of city and try again.')
            else:
                await message.answer(f'-----{datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}-----'
                                     '\n'
                                     f'\nName - {response["name"]}.'
                                     f'\nCountry - {response["country"]}.'
                                     '\n'
                                     f'\nCurrent temperature - {response["temp"]}°.'
                                     f'\nTemperature feels like - {response["temp_feels"]}°.'
                                     f'\nMin/Max temperature - {response["min_temp"]}° / {response["max_temp"]}°.'
                                     '\n'
                                     f'\nSunrise at - {response["sunrise"]}.'
                                     f'\nSunset at - {response["sunset"]}.'
                                     '\n'
                                     f'\nWind speed - {response["wind_speed"]} per metr.'
                                     f'\nClouds - {response["clouds"]}%.'
                                     f'\nMm of rain - {response["rain_per_hour"]} per hour.'
                                     '\n'
                                     f'\nAdditional info - {(response["description"]).capitalize()}.'
                                     )

    elif '/tech_support' in message.text:
        if message.text.replace('/tech_support', '').replace(' ', '') == '':
            await message.answer('You should provide a appeal text.')
        else:
            text = message.text.replace('/tech_support ', '')
            username = None
            first_name = None
            last_name = None

            if message.from_user.username:
                username = message.from_user.username.replace("'", '').replace(' ', '')
            if message.from_user.first_name:
                first_name = message.from_user.first_name.replace("'", '').replace(' ', '')
            if message.from_user.last_name:
                last_name = message.from_user.last_name.replace("'", '').replace(' ', '')

            await bot.send_message(chat_id=620336352, text=f'Message from {username}.\nFirst name: {first_name}\nLast name: {last_name}\nUser ID: {message.from_user.id}\n\nCall text: {text}')

    elif '/comm_sett' in message.text:
        await message.answer('Settings:\n- /language\n- /voice_assistant')

    elif '/sett' in message.text:
        await message.answer('---SETTINGS---')
        await message.answer(f'Language `{language}`', reply_markup=kb.language_kb)
        await message.answer(f'Assistant `{voice_assistant.upper()}`', reply_markup=kb.voice_assistant_kb)

    elif '/ai' in message.text:
        if message.text.replace('/ai', '').replace(' ', '') == '':
            await message.answer('You should provide a prompt.')
        else:
            reply = get_answer(message.text.replace('/ai ', ''))
            await message.answer(f'AI: {reply}')
            if voice_assistant == 'on':
                file = types.FSInputFile('Voice assistant reply.')
                text_to_speach(reply, language)
                await bot.send_audio(chat_id=message.from_user.id, audio=file)
                os.remove('Voice assistant reply.')

    elif '/open' in message.text:
        if message.text.replace('/open', '').replace(' ', '') == '':
            await message.answer('You should provide an app name to open.')

        else:
            app = message.text.split(' ', 1)[1]
            await message.answer(open_app(app))

    elif '/close' in message.text:
        if message.text.replace('/close', '').replace(' ', '') == '':
            await message.answer('You should provide an app name to close.')

        else:
            app = message.text.split(' ', 1)[1]
            await message.answer(close_app(app))

    elif '/screenshot' in message.text:
        query = message.text.replace('/screenshot', ' ').split(' ')

        # -----v1-----

        ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

        image = ImageGrab.grab()
        np_img = np.array(image)

        img = cv2.cvtColor(np_img, cv2.COLOR_BGR2RGB)
        cv2.imwrite('screenshot.png', img)

        screenshot = types.FSInputFile('screenshot.png')

        if len(list(filter(is_not_empty, query))) == 0 or list(filter(is_not_empty, query))[0] == '1':
            await bot.send_photo(chat_id=message.chat.id, photo=screenshot)
        elif list(filter(is_not_empty, query))[0] == '2':
            await bot.send_document(chat_id=message.chat.id, document=screenshot)
        else:
            await message.answer('Incorrect quality input value.')

        os.remove('screenshot.png')

        # -----v2-----

        # pyautogui.press('win')
        # time.sleep(2)
        # keyboard.write('Snipping Tool')
        # time.sleep(2)
        # keyboard.press('enter')
        # time.sleep(2)
        #
        # try:
        #     locate = pyautogui.locateCenterOnScreen('commands_images/full_mode_image.png')
        #     if not locate:
        #         raise Exception('No full screenshot mode.')
        #
        # except (Exception,):
        #     await message.answer('No full screenshot mode in snipping tool. Active it for proper working.')
        #
        # locate = pyautogui.locateCenterOnScreen('commands_images/add_screenshot.png')
        # pyautogui.moveTo(locate)
        # time.sleep(1)
        # pyautogui.click()
        # time.sleep(2)
        #
        # buffer_img = PIL.ImageGrab.grabclipboard()
        # np_img = np.array(buffer_img)
        #
        # img = cv2.cvtColor(np_img, cv2.COLOR_BGR2RGB)
        # cv2.imwrite('screenshot.png', img)
        #
        # screenshot = types.FSInputFile('screenshot.png')
        #
        # if len(list(filter(is_not_empty, query))) == 0 or list(filter(is_not_empty, query))[0] == '1':
        #     await bot.send_photo(chat_id=message.chat.id, photo=screenshot)
        # elif list(filter(is_not_empty, query))[0] == '2':
        #     await bot.send_document(chat_id=message.chat.id, document=screenshot)
        #
        # os.remove('screenshot.png')
        # await message.answer(f'*Additional: {close_app("Snipping Tool")}')

    elif message.text == '/task_manager':
        output = subprocess.check_output(['tasklist'])
        decoded_output = codecs.decode(output, 'latin-1')

        for line in decoded_output.splitlines():
            if line:
                time.sleep(0.3)
                await message.answer(text=f'{line}')
            else:
                await message.answer('---')

    elif message.text == '/info':
        await message.answer('Assistant AiBot_IMT was created by using Bard AI.')
        await message.answer('Info in developing...')

    elif '/video' in message.text:
        if message.text.replace('/video', '').replace(' ', '') == '':
            await message.answer('You should provide a prompt for browser request.')
        else:
            user_request = message.text.split(' ', 1)[1]

            if user_request.startswith('https:'):
                webbrowser.open(user_request)
            else:
                webbrowser.open(f'https://www.youtube.com/search?q={user_request}')

            time.sleep(3)
            await message.answer(f'{user_request.capitalize()} video was successfully opened.')

    elif '/browser' in message.text:
        if message.text.replace('/browser', '').replace(' ', '') == '':
            await message.answer('You should provide a prompt for browser request.')
        else:
            user_request = message.text.split(' ', 1)[1]
            webbrowser.open(user_request)

            time.sleep(3)
            await message.answer(f'{user_request.capitalize()} request was successfully opened.')

    elif '/volume' in message.text:
        if message.text.replace('/volume', '').replace(' ', '') == '':
            await message.answer('Which volume:', reply_markup=kb.volume_choice_kb)
        else:
            try:
                volume_value = float(message.text.split(' ')[1])

                if 0 <= volume_value <= 100:
                    set_master_volume(value=volume_value / 100)
                elif -65.0 <= volume_value < 0:
                    set_master_volume(cast_value=volume_value)
            except (Exception,):
                await message.answer('Provide a valid value (0-100).')

    elif '/key' in message.text:
        if message.text.replace('/key', '').replace(' ', '') == '':
            await message.answer('You should provide a key.')
        else:
            query_list = message.text.lower().replace('/key ', '').split(' ')
            keys = list(filter(is_not_empty, query_list))

            if len(keys) == 1:
                key = keys[0]
                pyautogui.press(key)
            elif len(keys) == 2:
                key1 = keys[0]
                key2 = keys[1]
                pyautogui.hotkey(key1, key2)
            elif len(keys) > 2 and keys[0] not in ['ctrl', 'space', 'shift', 'alt', 'tab', 'win', 'capslock', 'enter', 'backspace']:
                keyboard.write(message.text.lower().replace('/key ', ''))
            elif len(keys) == 3 and keys[0] in ['ctrl', 'space', 'shift', 'alt', 'tab', 'win', 'capslock', 'enter', 'backspace', 'delete']:
                key1 = keys[0]
                key2 = keys[1]
                key3 = keys[2]
                pyautogui.hotkey(key1, key2, key3)
            else:
                await message.answer('You should provide no more then 2 keys.')

    elif '/sleep' in message.text:
        if message.text.replace('/sleep', '').replace(' ', '') == '':
            await message.answer('You should provide a valid time sleep, in minutes.')
        else:
            sleep_time = list(filter(is_not_empty, message.text.replace('/sleep ', '')))
            if len(sleep_time) > 1:
                await message.answer(f'Expected one value for time sleep, got {len(sleep_time)}')
            else:
                subprocess.run(["powercfg", "/setdcvalue", "SLEEP", "AC", sleep_time[0]])

    else:
        await message.answer('Sorry, didnt understand you, watch /help.')


@router_handler.callback_query(AdminFilter())
async def query(callback: types.CallbackQuery, state: FSMContext):
    global language, image, voice_assistant

    if callback.data == 'Ru_language':
        language = 'ru-RU'
        time.sleep(1)
        await callback.message.answer('Язык был изменен на русский.')

    elif callback.data == 'En_language':
        language = 'en-EN'
        time.sleep(1)
        await callback.message.answer('Language has been switched to english.')

    elif callback.data == 'Ua_language':
        language = 'uk-UA'
        time.sleep(1)
        await callback.message.answer('Мову було змінено на українську.')

    elif callback.data == 'voice_assistant_on':
        voice_assistant = 'on'
        await callback.message.answer('You switch voice assistant to ON.')

    elif callback.data == 'voice_assistant_off':
        voice_assistant = 'off'
        await callback.message.answer('You switch voice assistant to OFF.')

    elif callback.data == 'volume_master_up':
        master_volume_up()

    elif callback.data == 'volume_master_down':
        master_volume_down()

    elif callback.data == 'volume_master_mute_unmute':
        master_volume_mute_unmute()

    elif callback.data == 'volume_master_max_min':
        master_volume_max_min()

    elif callback.data == 'volume_choice_master':
        await callback.message.answer('Change the master volume:', reply_markup=kb.volume_master_kb)

    elif callback.data == 'volume_choice_app':
        audio_kb = sessions_audio_kb()
        await callback.message.answer('Choose the volume line:', reply_markup=audio_kb)

    elif 'app_session_' in callback.data:

        state: BotState = await state.get_data()
        session = state.get('session_name')

        if 'up' in callback.data:
            await app_volume_up(session)

        elif 'down' in callback.data:
            await app_volume_down(session)

        elif 'mute_unmute' in callback.data:
            await app_volume_mute_unmute(session)

        elif 'max_min' in callback.data:
            await app_volume_max_min(session)

    elif 'session_' in callback.data:

        session = callback.data.split('_')[1]

        await state.set_state(BotState)
        await state.update_data(session_name=session)

        # data: BotState = await state.get_data()
        # message_id = data.get('message_id')

        # if message_id and callback.message.message_id == int(message_id):
        #     print(callback.message.message_id)
        #     await bot.edit_message_text(text=f'Change the {session.split(".")[0]} volume:', message_id=2487, chat_id=callback.message.from_user.id)
        # else:
        await callback.message.answer(f'Change the {session.split(".")[0]} volume:', reply_markup=kb.volume_app_kb)
        await state.update_data(message_id=callback.message.message_id)

    elif 'image_size_kb' in callback.data:
        if '1' in callback.data:
            image['size'] = '256x256'
        elif '2' in callback.data:
            image['size'] = '512x512'
        elif '3' in callback.data:
            image['size'] = '1024x1024'
        await callback.message.answer('Let`s choose a number of images:', reply_markup=kb.image_numbers_kb)

    elif 'image_numbers_kb' in callback.data:
        if '1' in callback.data:
            image['number'] = 1
        elif '2' in callback.data:
            image['number'] = 2
        elif '3' in callback.data:
            image['number'] = 3
        elif '4' in callback.data:
            image['number'] = 4
        await callback.message.answer('Do request to AI', reply_markup=kb.image_request_kb)

    elif 'close_sure_yes' in callback.data:
        app = callback.message.text.split(' ')[1]
        await callback.message.answer(close_app(app))

    elif 'close_sure_no' in callback.data:
        await callback.message.answer('Application closure rejected ')

    elif 'image_request_response' in callback.data:
        await callback.message.answer(f'Request: {image["prompt"], image["size"], image["number"]}')
        await callback.message.answer('Request in development...')

        # config = configparser.ConfigParser()
        # config.read('credential.ini')
        #
        # openai.api_key = OPENAI_TOKEN_ALYA
        # response = openai.Image.create(
        #     # image=open("sunlit_lounge.png", "rb"),
        #     # mask=open("mask.png", "rb"),
        #     prompt=image["prompt"],
        #     n=image["number"],
        #     size=image["size"]
        # )
        # print(response)
        #
        # response = generate_image(prompt=image["prompt"], num_image=image["number"], size=image["size"])
        # print(response)
        # prefix = 'demo'
        # for index, image in enumerate(response['images']):
        #     with open(f'{prefix}_{index}.jpg', 'wb') as f:
        #         f.write(b64decode(image))
