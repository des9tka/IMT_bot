import os
import time
from aiogram import Router
from pydub import AudioSegment
import speech_recognition as sr
from aiogram import types, F

import keyboards as kb
from utils import got_answer
from config import bot

router_handler = Router()

language = 'ru-RU'


@router_handler.message(F.voice)
async def audio_request(message: types.Message):
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
    await message.answer(f'AI: {str(got_answer(transcription))}')


@router_handler.message(F.sticker)
async def sticker_id(message: types.Message):
    await message.answer(message.sticker.file_id)


@router_handler.message(F.text)
async def query(message: types.Message):
    if message.text == '/start':
        time.sleep(1)
        await message.answer_sticker(sticker='CAACAgIAAxkBAAOpZRf-yoxEiHWx8_ps5yU_67pi3woAAgEBAAJWnb0KIr6fDrjC5jQwBA')
        time.sleep(1)
        await message.answer('Nice to meet you, can i help you?')
    elif message.text == '/help':
        time.sleep(1)
        await message.answer('Here some commands to use: \n- /language (Switch input language, default Ru).\n- No commands (Text request to AI).\n- Voice message (Voice request to AI).')
    elif message.text == '/language':
        await message.answer(f'Your language is {language}. Choose new one:', reply_markup=kb.language_kb)
    else:
        await message.answer(got_answer(message.text))


@router_handler.callback_query()
async def query(callback: types.CallbackQuery):
    global language
    if callback.data == 'Ru_language':
        language = 'ru-RU'
        time.sleep(1)
        await callback.message.answer('Язык был изменен на русский.')
    elif callback.data == 'En_language':
        language = 'en-EN'
        time.sleep(1)
        await callback.message.answer('Language has been switched to english.')
