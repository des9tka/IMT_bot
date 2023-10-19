import os

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from pydub import AudioSegment
import speech_recognition as sr

from config import bot
from filters import AdminFilter
from state import BotState
from utils import get_answer, text_to_speach


router_voice_handler = Router()


@router_voice_handler.message(AdminFilter(), F.voice)
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
