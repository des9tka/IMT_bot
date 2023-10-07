import codecs
import os
import subprocess
import tempfile
import time

import PIL
import mss
import numpy as numpy
import speech_recognition as sr
from PIL import ImageGrab
from aiogram import Router
from aiogram import types, F
from pydub import AudioSegment

import keyboards as kb
from config import bot
from filters import AdminFilter
from utils import got_answer, text_to_speach, open_app, close_app

router_handler = Router()

language = 'ru-RU'
voice_assistant = 'off'
image = dict()
bots = {}


@router_handler.message(AdminFilter(), F.video)
async def cpt_video(message: types.Message):
    # Open the video file in binary mode.
    # with open(message.video, 'rb') as f:
    #     video_bytes = f.read()
    #
    # # Send the video file to Captions.AI.
    # response = requests.post(url='https://app.captions.ai/add-captions',
    #                          files={'video': video_bytes})

    print('video')


@router_handler.message(AdminFilter(), F.audio)
async def get_audio_id(message: types.Message):
    await message.answer(message.audio.file_id)


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
        reply = got_answer(transcription)
        await message.answer(f'AI: {reply}')
        if voice_assistant == 'on':
            file = types.FSInputFile('Voice assistant reply.')
            text_to_speach(reply, language)
            await bot.send_audio(chat_id=message.from_user.id, audio=file)
            os.remove('Voice assistant reply.')
    except (Exception,) as e:
        await message.answer(f'Something went wrong, check yor input language and try again.\nMore details: {e}')


@router_handler.message(AdminFilter(), F.sticker)
async def sticker_id(message: types.Message):
    await message.answer(message.sticker.file_id)


@router_handler.message(AdminFilter(), F.text)
async def query(message: types.Message):
    if message.text == '/start' and message.chat.id == message.from_user.id:
        time.sleep(1)
        await message.answer_sticker(sticker='CAACAgIAAxkBAAOpZRf-yoxEiHWx8_ps5yU_67pi3woAAgEBAAJWnb0KIr6fDrjC5jQwBA')
        time.sleep(1)
        await message.answer('Nice to meet you, can i /help you?')

    if message.text == '/info':
        await message.answer(text=f'{message.from_user}')

    elif message.text == '/help':
        time.sleep(1)
        await message.answer('Here some commands to use: \n- /ai + prompt (Prompt request to AI).\n- Voice message (Voice request to AI).\n- /lang (Switch input/output language, default `Ru`).\n- /id (Find out your id).'
                             '\n- /img + prompt (Generate image with AI).\n- /tech_supp + query (Get in touch with our team).\n- /voice_ass (Switch voice assistant reply mode, default `OFF`).\n- /screenshot + monitor '
                             'number ('
                             'Make screenshot).\n- /open + app name (Open an app, should be global available).\n- /close + app name (Close an app, should be global available).\n- /task_manager (List of pc tasks).\n- '
                             '/sett (All bot '
                             'settings).\n- '
                             '/comm_sett (Settings by commands).\n- /help (Watch list of all commands).\n- /info (Useful info and F&Q).')

    elif message.text == '/lang':
        await message.answer(f'Your language is {language}. Choose new one:', reply_markup=kb.language_kb)

    elif message.text == '/voice_ass':
        await message.answer(f'Voice assistant --> {voice_assistant.upper()}', reply_markup=kb.voice_assistant_kb)

    elif '/img' in message.text:
        if message.text.replace('/img', '').replace(' ', '') == '':
            await message.answer('You should provide a prompt.')
        else:
            image['prompt'] = message.text.replace('/img ', '')
            await message.answer('Okay, let`s choose size:', reply_markup=kb.image_size_kb)

    elif message.text == '/id':
        await message.answer(f'Your id: {message.from_user.id}')

    elif '/send' in message.text:
        text = message.text.replace('/send ', '')
        await bot.send_message(chat_id=5714917250, text=text)

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

            await bot.send_message(chat_id=620336352, text=f'Message from {username}.\nFirst name: {first_name}\nLast name: {last_name}\n\nCall text: {text}')

    elif '/comm_sett' in message.text:
        await message.answer('Settings:\n- /language\n- /voice_assistant')

    elif '/sett' in message.text:
        await message.answer('---SETTINGS---')
        await message.answer('Language', reply_markup=kb.language_kb)
        await message.answer(f'Assistant', reply_markup=kb.voice_assistant_kb)

    elif '/ai' in message.text:
        if message.text.replace('/ai', '').replace(' ', '') == '':
            await message.answer('You should provide a prompt.')
        else:
            reply = got_answer(message.text.replace('/ai ', ''))
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
        try:
            monitor_number = int(message.text.split(' ')[1])
        except (Exception,):
            monitor_number = 1

        with mss.mss() as sct:
            mon = sct.monitors[monitor_number]
            monitor = {
                'top': mon['top'],
                'left': mon['left'],
                'width': mon['width'],
                'height': mon['height'],
                'mon': monitor_number
            }
            sct_image = sct.grab(monitor)
            path = tempfile.gettempdir() + '/screenshot2.png'
            pil_image = PIL.ImageGrab.Image.frombytes("RGB", sct_image.size, sct_image.bgra, "raw", "BGRX")
            pil_image.save(path)
            photo = types.FSInputFile(path)
            await message.answer_photo(photo)

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
        await message.answer('Info in developing...')

    else:
        await message.answer('Sorry, didnt understand you, watch /help.')


@router_handler.callback_query(AdminFilter())
async def query(callback: types.CallbackQuery):
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

    elif 'image_size_kb' in callback.data:
        if '1' in callback.data:
            image['size'] = '256x256'
        if '2' in callback.data:
            image['size'] = '512x512'
        if '3' in callback.data:
            image['size'] = '1024x1024'
        await callback.message.answer('Let`s choose a number of images:', reply_markup=kb.image_numbers_kb)

    elif 'image_numbers_kb' in callback.data:
        if '1' in callback.data:
            image['number'] = 1
        if '2' in callback.data:
            image['number'] = 2
        if '3' in callback.data:
            image['number'] = 3
        if '4' in callback.data:
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
