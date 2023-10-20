import os
import time

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from pydub import AudioSegment
import speech_recognition as sr

from config import bot
from filters import AdminFilter
from state import BotState, state_setup


router_voice_handler = Router()


@router_voice_handler.message(AdminFilter(), F.voice)
async def audio_request(message: types.Message, state: FSMContext):

    get_state: BotState = await state.get_data()
    await state.set_state(BotState)

    if not get_state.get('set_up'):
        await state_setup(state)

    try:
        audio_file = await bot.get_file(message.voice.file_id)

        await bot.download_file(audio_file.file_path, 'message_audio.ogg')

        audio = AudioSegment.from_file('message_audio.ogg', format='ogg')
        audio.export('message_audio.ogg', format='wav')
        recognizer = sr.Recognizer()

        with sr.AudioFile('message_audio.ogg') as source:
            audio_data = recognizer.record(source)

        transcription = recognizer.recognize_google(audio_data, language=get_state.get('language'))

        await message.answer('Choose the command for voice message:\n- /voice_ai\n - /voice_transcription')
        await state.update_data(command_name='/voice')
        await state.update_data(subject=transcription)

        os.remove('message_audio.ogg')
    except (Exception,):
        await message.answer('Something went wrong. Check you voice input and try again...')
