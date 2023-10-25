import os
import time

import keyboard
import pyautogui
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from pytube import YouTube

import keyboards as kb
from .message_handler import message_query
from config import bot
from filters import AdminFilter
from state import BotState
from utils import master_volume_up, master_volume_down, master_volume_mute_unmute, master_volume_max_min, app_volume_up, app_volume_down, app_volume_max_min, \
    app_volume_mute_unmute, open_app, open_video_via_browser

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
        audio_kb = kb.sessions_audio_kb()
        await callback.message.answer('Choose the volume line:', reply_markup=audio_kb)

    elif get_state.get('session_name') and 'app_session_' in callback.data:

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

        await callback.message.answer(f'Change the {session.split(".")[0]} volume:', reply_markup=kb.volume_app_kb)
        await state.update_data(message_id=callback.message.message_id)

    elif get_state.get('subject') and 'image_worse_quality' in callback.data:
        if get_state.get('subject') == '/resize':
            file = types.FSInputFile('help_image.jpg')
            await callback.message.answer_photo(file, caption='Here is your resized image.')

            os.remove('work_image.jpg')
            os.remove('help_image.jpg')
            await state.update_data(command_name='No_command')
            await state.update_data(subject=None)

        elif get_state.get('subject') == '/blur':
            file = types.FSInputFile('blurred_image.jpg')
            await callback.message.answer_photo(file, caption='Here is your blured image.')

            os.remove('work_image.jpg')
            os.remove('blurred_image.jpg')
            await state.update_data(command_name='No_command')
            await state.update_data(subject=None)

        elif get_state.get('subject') == '/screenshot':
            screenshot = types.FSInputFile('screenshot.png')
            await callback.message.answer_photo(photo=screenshot)
            os.remove('screenshot.png')
            await state.update_data(command_name='No_command')
            await state.update_data(subject=None)

    elif get_state.get('subject') and 'image_better_quality' in callback.data:
        if get_state.get('subject') == '/resize':
            file = types.FSInputFile('help_image.jpg')
            await bot.send_document(chat_id=callback.message.chat.id, document=file)

            os.remove('work_image.jpg')
            os.remove('help_image.jpg')
            await state.update_data(command_name='No_command')
            await state.update_data(subject=None)

        elif get_state.get('subject') == '/blur':
            file = types.FSInputFile('blurred_image.jpg')
            await bot.send_document(chat_id=callback.message.chat.id, document=file)

            os.remove('work_image.jpg')
            os.remove('blurred_image.jpg')
            await state.update_data(command_name='No_command')
            await state.update_data(subject=None)

        elif get_state.get('subject') == '/screenshot':
            screenshot = types.FSInputFile('screenshot.png')
            await callback.message.answer_document(document=screenshot)
            os.remove('screenshot.png')
            await state.update_data(command_name='No_command')
            await state.update_data(subject=None)

    elif callback.data.startswith('browser_choice_'):
        if callback.data == 'browser_choice_chrome':
            open_app('Chrome')
            await open_video_via_browser('Chrome', get_state.get('subject'))

        elif callback.data == 'browser_choice_opera':
            await open_video_via_browser('Opera', get_state.get('subject'))

        elif callback.data == 'browser_choice_edge':
            await open_video_via_browser('Edge', get_state.get('subject'))

        elif callback.data == 'browser_choice_firefox':
            await open_video_via_browser('FireFox', get_state.get('subject'))

        await state.update_data(command_name='No_command')
        await state.update_data(subject=None)

    elif callback.data.startswith('video_platform'):
        name = None
        if callback.data == 'video_platform_youtube':
            await state.update_data(command_name='/download_video/video_platform_youtube')
            name = 'YouTube'
        if callback.data == 'video_platform_tiktok':
            await state.update_data(command_name='/download_video/video_platform_tiktok')
            name = 'TikTok'
        if callback.data == 'video_platform_instagram':
            await state.update_data(command_name='/download_video/video_platform_instagram')
            name = 'Instagram'

        await callback.message.answer(f'Send the {name} url for downloading:')

    elif get_state.get('subject') and 'download_youtube_' in callback.data:
        url = get_state.get('subject')
        YouTube(url).streams.get_by_itag(callback.data.replace('download_youtube_', '').replace(' ', '')).download(output_path=os.getcwd(), filename='youtube_video.mp4')
        file = types.FSInputFile('youtube_video.mp4')
        await callback.message.answer_video(video=file, caption='Here is your video.', reply_markup=kb.exit_keyboard)
        os.remove('youtube_video.mp4')

    else:
        await callback.message.answer('You already used command or use unknown callback for this command. Press command call and try again.')


