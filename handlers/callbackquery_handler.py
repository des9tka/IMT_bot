import os
import time

from aiogram import Router, types
from aiogram.fsm.context import FSMContext

import keyboards as kb
from config import bot
from filters import AdminFilter
from state import BotState
from utils import master_volume_up, master_volume_down, master_volume_mute_unmute, master_volume_max_min, sessions_audio_kb, app_volume_up, app_volume_down, app_volume_max_min, \
    app_volume_mute_unmute

router_callback_query_handler = Router()


@router_callback_query_handler.callback_query(AdminFilter())
async def query(callback: types.CallbackQuery, state: FSMContext):

    get_state: BotState = await state.get_data()
    await state.set_state(BotState)

    if callback.data == 'Ru_language':

        await state.update_data(language='ru-RU')
        time.sleep(1)
        await callback.message.answer('Язык был изменен на русский.')

    elif callback.data == 'En_language':
        await state.update_data(language='en-EN')
        time.sleep(1)
        await callback.message.answer('Language has been switched to english.')

    elif callback.data == 'Ua_language':
        await state.update_data(language='uk-UA')
        time.sleep(1)
        await callback.message.answer('Мову було змінено на українську.')

    elif callback.data == 'voice_assistant_on':
        await state.update_data(voice_assistant='ON')
        await callback.message.answer('You switch voice assistant to ON.')

    elif callback.data == 'voice_assistant_off':
        await state.update_data(voice_assistant='OFF')
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

        session = get_state.get('session_name')

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

        await callback.message.answer(f'Change the {session.split(".")[0]} volume:', reply_markup=kb.volume_app_kb)
        await state.update_data(message_id=callback.message.message_id)

    elif 'image_worse_quality' in callback.data:
        file = types.FSInputFile('resized_image.jpg')
        await callback.message.answer_photo(file, caption='Here is your resized image.')

        os.remove('work_image.jpg')
        os.remove('resized_image.jpg')
        await state.update_data(command_name='No_command')
        await state.update_data(subject=None)

    elif 'image_better_quality' in callback.data:
        file = types.FSInputFile('resized_image.jpg')
        await bot.send_document(chat_id=callback.message.chat.id, document=file)

        os.remove('work_image.jpg')
        os.remove('resized_image.jpg')
        await state.update_data(command_name='No_command')
        await state.update_data(subject=None)

    # elif 'image_size_kb' in callback.data:
    #     if '1' in callback.data:
    #         image['size'] = '256x256'
    #     elif '2' in callback.data:
    #         image['size'] = '512x512'
    #     elif '3' in callback.data:
    #         image['size'] = '1024x1024'
    #     await callback.message.answer('Let`s choose a number of images:', reply_markup=kb.image_numbers_kb)
    #
    # elif 'image_numbers_kb' in callback.data:
    #     if '1' in callback.data:
    #         image['number'] = 1
    #     elif '2' in callback.data:
    #         image['number'] = 2
    #     elif '3' in callback.data:
    #         image['number'] = 3
    #     elif '4' in callback.data:
    #         image['number'] = 4
    #     await callback.message.answer('Do request to AI', reply_markup=kb.image_request_kb)
    #
    # elif 'image_request_response' in callback.data:
    #     await callback.message.answer(f'Request: {image["prompt"], image["size"], image["number"]}')
    #     await callback.message.answer('Request in development...')
