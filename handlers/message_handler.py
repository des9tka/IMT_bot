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
from state import state_setup
from config import bot
from filters import AdminFilter
from state import BotState
from utils import get_answer, text_to_speach, open_app, close_app, get_weather, cast_to_message_photo, is_not_empty, set_master_volume


router_message_handler = Router()


@router_message_handler.message(AdminFilter(), F.video)
async def cpt_video(message: types.Message):
    await message.answer('Video capturing in development... ')


@router_message_handler.message(AdminFilter(), F.audio)
async def get_audio_id(message: types.Message):
    await message.answer(message.audio.file_id)


@router_message_handler.message(AdminFilter(), F.photo)
async def image_request(message: types.Message, state: FSMContext):

    try:
        file = await bot.get_file(message.photo[-1].file_id)
        await message.bot.download_file(file.file_path, "work_image.jpg")
        await state.update_data(image=message.photo[-1].file_id)

        await state.update_data(command_name='/photo')
        await message.answer('Select command for your image: \n- /image_ai + prompt\n- /image_resize + "width"x"high"\n- /image_id')

    except (Exception,):
        await message.answer('Something gonna wrong, check your input image and try again.')
        try:
            await state.update_data(command_name=None)
            os.remove('work_image.jpg')
        except (Exception,):
            print('Details: All clear.')


@router_message_handler.message(AdminFilter(), F.voice)
async def audio_request(message: types.Message, state: FSMContext):

    get_state: BotState = await state.get_data()
    await state.set_state(BotState)

    try:
        audio_file = await bot.get_file(message.voice.file_id)

        await bot.download_file(audio_file.file_path, 'message_audio.ogg')

        audio = AudioSegment.from_file('message_audio.ogg', format='ogg')
        audio.export('message_audio.ogg', format='wav')
        recognizer = sr.Recognizer()

        with sr.AudioFile('message_audio.ogg') as source:
            audio_data = recognizer.record(source)

        transcription = recognizer.recognize_google(audio_data, language=get_state.get('language'))

        os.remove('message_audio.ogg')

        await message.reply(f'You: {transcription}')
        reply = get_answer(transcription)
        await message.answer(f'AI: {reply}')

        if get_state.get('voice_assistant') == 'on':
            file = types.FSInputFile('Voice assistant reply.')
            text_to_speach(reply, get_state.get('language'))
            await bot.send_audio(chat_id=message.from_user.id, audio=file)
            os.remove('Voice assistant reply.')

    except (Exception,) as e:
        await message.answer(f'Something went wrong, check yor input language or input query and try again.\nMore details: {str(e)}')

        try:
            os.remove('message_audio.ogg')
            os.remove('Voice assistant reply.')
        except (Exception,):
            print('Details: All clear.')


@router_message_handler.message(AdminFilter(), F.sticker)
async def sticker_id(message: types.Message):
    await message.answer(f'Here is your`s sticker id: {message.sticker.file_id}')


@router_message_handler.message(AdminFilter(), F.text)
async def query(message: types.Message, state: FSMContext):

    await state.set_state(BotState)
    get_state: BotState = await state.get_data()

    if not get_state.get('set_up'):
        await state_setup(state)

    if message.text.lower() == 'exit' and get_state.get("command_name") != None:
        await message.answer(f'You exited command {get_state.get("command_name")}.')
        await state.update_data(command_name=None)
        try:
            os.remove('work_image.jpg')
        except (Exception,):
            print('Details: All clear.')

    if message.text == '/start':
        await message.answer_sticker(sticker='CAACAgIAAxkBAAOpZRf-yoxEiHWx8_ps5yU_67pi3woAAgEBAAJWnb0KIr6fDrjC5jQwBA')
        time.sleep(1)
        await message.answer('Nice to meet you, can i /help you?')

    # ------------------------------AI------------------------------

    elif '/ai' in message.text or get_state.get('command_name') == '/ai':
        text = None

        if '/ai' in message.text and message.text.replace('/ai', '').replace(' ', '') == '':
            await state.update_data(command_name='/ai')
            await message.answer('Provide a prompt for AI request:', reply_markup=kb.exit_keyboard)
        elif '/ai' in message.text and message.text.replace('/ai', '').replace(' ', '') != '':
            text = message.text.replace('/ai', '').replace(' ', '')
        elif get_state.get('command_name') == '/ai':
            text = message.text

        if text:
            reply = get_answer(message.text.replace('/ai ', ''))
            await message.answer(f'AI: {reply} \n***To exit AI conversation press or write EXIT***')

            if get_state.get('voice_assistant') == 'on':
                text_to_speach(reply, language=get_state.get('language'))
                file = types.FSInputFile('Voice assistant reply.')
                await bot.send_audio(chat_id=message.from_user.id, audio=file)
                os.remove('Voice assistant reply.')

    elif '/generate_img' in message.text:
        await message.answer('Image generation in developing...')

    elif get_state.get('command_name') == '/voice':
        pass

    elif get_state.get('command_name') and '/photo' in get_state.get('command_name'):

        if message.text.startswith('/image_ai') or '/image_ai' in get_state.get('command_name'):
            text = None

            if '/image_ai' in message.text and message.text.replace('/image_ai', '').replace(' ', '') == '':
                await state.update_data(command_name='/photo/image_ai')
                await message.answer('Provide a prompt for AI:')

            elif '/image_ai' in message.text and message.text.replace('/image_ai', '').replace(' ', '') != '':
                text = message.text.replace('/image_ai', '').replace(' ', '')

            elif get_state.get('command_name') == '/photo/image_ai':
                text = message.text

            if text:
                # -----while developing-----
                await message.answer('Image request to AI in development... ')

                os.remove('work_image.jpg')
                await state.update_data(command_name=None)

        elif message.text.startswith('/image_resize') or '/image_resize' in get_state.get('command_name'):
            size = None

            if '/image_resize' in message.text and message.text.replace('/image_resize', '').replace(' ', '') == '':
                await state.update_data(command_name='/photo/image_resize')
                await message.answer('Provide a size ("width"x"high") for new image:')

            elif '/image_resize' in message.text and message.text.replace('/image_resize', '').replace(' ', '') != '':
                size = message.text.replace('/image_resize', '').replace(' ', '')

            elif get_state.get('command_name') == '/photo/image_resize':
                size = message.text

            if size:
                img = cv2.imread('work_image.jpg')
                sizes = list(filter(is_not_empty, size.split('x')))

                if len(sizes) > 2:
                    await message.answer('Should be provided "width"x"high".')

                else:
                    try:
                        resized_img = cv2.resize(img, (int(sizes[0]), int(sizes[1])))
                        cv2.imwrite('resized_image.jpg', resized_img)
                        file = types.FSInputFile('resized_image.jpg')
                        await message.answer_photo(file, caption='Here is your resized image.')

                        os.remove('work_image.jpg')
                        os.remove('resized_image.jpg')
                        await state.update_data(command_name=None)
                    except (Exception,):
                        await message.answer('Something went wrong. Check your input size and try again..')

        elif message.text.startswith('/image_id'):
            await message.answer(f'Your image id: \n{get_state.get("image")}')
            os.remove('work_image.jpg')
            await state.update_data(command_name=None)
            await state.update_data(image=None)

        else:
            await message.answer(f'Unknown command for image.')

    elif get_state.get('command_message') == '/video_capture':
        # -----In development-----
        pass

    # ------------------------------Remote Control------------------------------

    elif '/open_video' in message.text:
        if message.text.replace('/open_video', '').replace(' ', '') == '':
            await message.answer('You should provide a prompt for browser request.')
        else:
            user_request = message.text.split(' ', 1)[1]

            if user_request.startswith('https:'):
                webbrowser.open(user_request)
            else:
                webbrowser.open(f'https://www.youtube.com/search?q={user_request}')

            time.sleep(3)
            await message.answer(f'{user_request.capitalize()} video was successfully opened.')

    elif '/open_in_browser' in message.text:
        if message.text.replace('/open_in_browser', '').replace(' ', '') == '':
            await message.answer('You should provide a prompt for browser request.')
        else:
            user_request = message.text.split(' ', 1)[1]
            webbrowser.open(user_request)

            time.sleep(3)
            await message.answer(f'{user_request.capitalize()} request was successfully opened.')

    elif '/screenshot' in message.text:
        query = message.text.replace('/screenshot', ' ').split(' ')

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

    # ------------------------------Additional------------------------------

    elif '/tech_support' in message.text or get_state.get('command_name') == '/tech_support':
        text = None

        if message.text.replace('/tech_support', '').replace(' ', '') == '':
            await state.update_data(command_name='/tech_support')
            await message.answer('Detect any problems? Input yor appeal text:', reply_markup=kb.exit_keyboard)
        elif '/tech_support' in message.text and message.text.replace('/tech_support', '').replace(' ', '') != '':
            text = message.text.replace('/tech_support ', '')
        elif get_state.get('command_name') == '/tech_support':
            text = message.text

        if text:

            username = None
            first_name = None
            last_name = None

            if message.from_user.username:
                username = message.from_user.username.replace("'", '').replace(' ', '')
            if message.from_user.first_name:
                first_name = message.from_user.first_name.replace("'", '').replace(' ', '')
            if message.from_user.last_name:
                last_name = message.from_user.last_name.replace("'", '').replace(' ', '')
            await bot.send_message(chat_id=620336352, text=f'Message from @{username}.\nFirst name: {first_name}\nLast name: {last_name}\nUser ID: {message.from_user.id}\n\nCall text: {text}')
            await message.answer_photo(photo=cast_to_message_photo('commands_images/tech_support_image.jpg'), caption='Thank you, for your invocation!')
            await state.update_data(command_name=None)

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
                                     f'\nCity - {response["name"]}.'
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

    elif message.text == '/help':
        await message.answer('Here some commands to use:'
                             '\n\n'
                             '<-----AI----->'
                             '\n- /ai + prompt (Prompt request to AI).'
                             '\n- /img + prompt (Generate image with AI).'
                             '\n- Voice message (Voice request to AI).'
                             '\n- Photo message + command + optional prompt (Commands:\n• /image_ai + prompt;\n• /image_resize + "width"x"high";\n• /image_id.'
                             '\n- Video (Capturing video by AI).'
                             '\n\n'
                             '<-----Remote Control----->'
                             '\n- /open_video + name/url (Find video in YouTube).'
                             '\n- /open_in_browser + prompt (Search info in browser).'
                             '\n- /screenshot + optional number quality (Qualities:\n• Nothing/1 (Screenshot with compression).\n• 2 (Screenshot in stock quality)).'
                             '\n- /open + app name (Open an app, should be global available).'
                             '\n- /close + app name (Close an app, should be global available).'
                             '\n- /key + hot key/keys (Remote keyboard input).'
                             '\n- /volume + optional value (Change value of volume, 0-100).'
                             '\n\n'
                             '<-----Additional----->'
                             '\n- /start (Start bot).'
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

    elif message.text == '/info':
        await message.answer('Assistant AiBot_IMT was created by using Bard AI.')
        await message.answer('Info in developing...')

    elif '/sleep' in message.text:
        if message.text.replace('/sleep', '').replace(' ', '') == '':
            await message.answer('You should provide a valid time sleep, in minutes.')
        else:
            sleep_time = list(filter(is_not_empty, message.text.replace('/sleep ', '')))
            if len(sleep_time) > 1:
                await message.answer(f'Expected one value for time sleep, got {len(sleep_time)}')
            else:
                subprocess.run(["powercfg", "/setdcvalue", "SLEEP", "AC", sleep_time[0]])

    # ------------------------------Settings------------------------------

    elif '/sett' in message.text:
        await message.answer('---SETTINGS---')
        await message.answer(f'Language --> `{get_state.get("language")}`', reply_markup=kb.language_kb)
        await message.answer(f'Voice assistant --> `{get_state.get("voice_assistant")}`', reply_markup=kb.voice_assistant_kb)

    elif '/comm_sett' in message.text:
        await message.answer('Settings:\n- /language\n- /voice_assistant')

    elif message.text == '/voice_ass':
        await message.answer(f'Voice assistant --> {get_state.get("voice_assistant")}', reply_markup=kb.voice_assistant_kb)

    elif message.text == '/lang':
        lang = get_state.get("language")
        await message.answer(f'Your language is {lang}. Choose new one:', reply_markup=kb.language_kb)

    elif message.text == '/task_manager':
        output = subprocess.check_output(['tasklist'])
        decoded_output = codecs.decode(output, 'latin-1')

        for line in decoded_output.splitlines():
            if line:
                time.sleep(0.3)
                await message.answer(text=f'{line}')
            else:
                await message.answer('---')

    elif message.text == '/id':
        await message.answer(f'Your id: {message.from_user.id}')

    else:
        await message.answer('Sorry, didnt understand you, watch /help.')
