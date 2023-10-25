import codecs
import datetime
import os
import subprocess
import time
from functools import partial

import cv2
import keyboard
import numpy as np
import pyautogui
from PIL import Image, ImageFilter
from PIL import ImageGrab
from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from pytube import YouTube

import keyboards as kb
from config import bot, help_message
from filters import AdminFilter
from state import BotState
from state import state_setup
from utils import get_answer, text_to_speach, open_app, close_app, get_weather, cast_to_message_photo, is_not_empty, set_master_volume, convert_video_to_mp3, keyboard_write, download_video_from_tiktok, download_from_inst

router_message_handler = Router()


@router_message_handler.message(AdminFilter(), F.text)
async def message_query(message: types.Message, state: FSMContext):
    # ------------------------------Tech------------------------------

    await state.set_state(BotState)
    get_state: BotState = await state.get_data()

    if not get_state.get('set_up'):
        await state_setup(state)

    if message.text.lower() == 'exit' and get_state.get("command_name") != 'No_command':
        await message.answer(f'You exited command {get_state.get("command_name")}.')
        try:
            if '/photo' in get_state.get('command_name'):
                os.remove('work_image.jpg')
            elif '/video_ai' in get_state.get('command_name'):
                os.remove('work_video.mp4')
                os.remove('resized_video.mp4')
        except (Exception,):
            print('Details: All clear.')
        await state.update_data(command_name='No_command')

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
        transcription = get_state.get('subject')

        if transcription and message.text == '/voice_transcription':
            await message.answer(f'Transcription: {transcription}')
            await state.update_data(command_name='No_command')
            await state.update_data(subject=None)

            try:
                os.remove('message_audio.ogg')
                os.remove('Voice assistant reply.')
            except (Exception,):
                print('Details: All clear.')

        if transcription and message.text == '/voice_ai':
            try:
                await message.reply(f'You: {transcription}')
                reply = get_answer(transcription)
                await message.answer(f'AI: {reply}')

                if get_state.get('voice_assistant') == 'ON':
                    file = types.FSInputFile('Voice assistant reply.')
                    text_to_speach(reply, get_state.get('language'))
                    await bot.send_audio(chat_id=message.from_user.id, audio=file)

                    os.remove('Voice assistant reply.')

                await state.update_data(command_name='No_command')
                await state.update_data(subject=None)

            except (Exception,) as e:
                await message.answer(f'Something went wrong, check yor input language or input query and try again.')

                try:
                    os.remove('message_audio.ogg')
                    os.remove('Voice assistant reply.')
                except (Exception,):
                    print('Details: All clear.')

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
                await state.update_data(command_name='No_command')

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
                        cv2.imwrite('help_image.jpg', resized_img)
                        await state.update_data(subject='/resize')
                        await message.answer('Choose the quality of image:', reply_markup=kb.image_quality_kb)

                    except (Exception,):
                        await message.answer('Something went wrong. Check your input size and try again.')

        elif message.text.startswith('/image_blur') or '/image_blur' in get_state.get('command_name'):
            blur = None
            if '/image_blur' in message.text and message.text.replace('/image_blur', '').replace(' ', '') == '':
                await state.update_data(command_name='/photo/image_blur')
                await message.answer('Provide a blur value (1-100) for new image:', reply_markup=kb.exit_keyboard)

            elif '/image_blur' in message.text and message.text.replace('/image_blur', '').replace(' ', '') != '':
                try:
                    blur = int(message.text.replace('/image_blur', '').replace(' ', ''))
                except (Exception,):
                    await message.answer('Something went wrong. Check your input blur value and try again.')

            elif get_state.get('command_name') == '/photo/image_blur':
                try:
                    blur = int(message.text)

                    if not 1 <= blur <= 100:
                        await message.answer('Invalid blur value input.')
                        blur = None
                except (Exception,):
                    await message.answer(f'Something went wrong. Check your input blur value and try again.')

            if blur:
                work_image = Image.open('work_image.jpg')

                blured_image = work_image.filter(ImageFilter.GaussianBlur(blur))
                blured_image.save('blurred_image.jpg')

                await state.update_data(subject='/blur')
                await message.answer('Choose the quality of image:', reply_markup=kb.image_quality_kb)

        elif message.text.startswith('/image_id'):
            await message.answer(f'Your image id: \n{get_state.get("image")}')
            os.remove('work_image.jpg')
            await state.update_data(command_name='No_command')
            await state.update_data(subject=None)

        elif not message.text.lower().startswith('exit'):
            await message.answer(f'Unknown command for image.')

    elif get_state.get('command_name') and '/video_ai' in get_state.get('command_name'):

        if '/video_caption' in message.text or '/video_caption' in get_state.get('command_name'):
            await message.answer('Captioning video in developing...')

        elif '/video_mp3' in message.text or message.text.replace('/video_ai', '').replace(' ', '') == '':
            try:
                convert_video_to_mp3('work_video.mp4', 'extract_audio.mp3')
                file = types.FSInputFile('extract_audio.mp3')

                await message.answer_audio(file, caption='Here is your mp3 from video.')
            except (Exception,):
                await message.answer('Exacting mp3 was failed. Check the input video and try again...')

            os.remove('work_video.mp4')
            os.remove('extract_audio.mp3')

        elif '/video_id' in message.text or message.text.replace('/video_id', '').replace(' ', '') == '':
            await message.answer(f'Your video id: \n{get_state.get("subject")}')
            os.remove('work_video.mp4')
            await state.update_data(command_name='No_command')
            await state.update_data(subject=None)

        elif '/video_resize' in message.text or '/video_resize' in get_state.get('command_name'):
            sizes = None

            if '/video_resize' in message.text and message.text.replace('/video_resize', '').replace(' ', '') == '':
                await state.update_data(command_name='/video_ai/video_resize')
                await message.answer('Provide a size ("width"x"high") for new video:', reply_markup=kb.exit_keyboard)

            elif '/video_resize' in message.text and message.text.replace('/video_resize', '').replace(' ', '') != '':
                sizes = message.text.replace('/video_resize', '').replace(' ', '')

            elif get_state.get('command_name') == '/video_ai/video_resize' and not message.text.lower().startswith('exit'):
                sizes = message.text

            elif not message.text.lower().startswith('exit'):
                await message.answer(f'Unknown command for image.')

            if sizes:
                try:
                    sizes = list(filter(is_not_empty, sizes.split('x')))

                    if len(sizes) == 1:
                        sizes = list(filter(is_not_empty, sizes.split('х')))

                    cap = cv2.VideoCapture('work_video.mp4')
                    codec = cv2.VideoWriter_fourcc(*"mp4v")

                    writer = cv2.VideoWriter('resized_video.mp4', codec, 25, (int(sizes[0]), int(sizes[1])))

                    while True:

                        ret, frame = cap.read()
                        if not ret:
                            break
                        resized_frame = cv2.resize(frame, (int(sizes[0]), int(sizes[1])))
                        writer.write(resized_frame)

                    writer.release()
                    cv2.destroyAllWindows()
                    file = types.FSInputFile('resized_video.mp4')
                    await message.answer_video(file, caption='Here is your resized video.')
                    await state.update_data(command_name='No_command')

                except (Exception,):
                    await message.answer('Something went wrong. Check your input size and try again.')

                os.remove('resized_video.mp4')
                os.remove('work_video.mp4')

    # ------------------------------Remote Control------------------------------

    elif '/open_video' in message.text or get_state.get('command_name') == '/open_video':

        if '/open_video' in message.text and message.text.replace('/open_video', '').replace(' ', '') == '':
            await state.update_data(command_name='/open_video')
            await message.answer('Provide a link or name of search video:', reply_markup=kb.exit_keyboard)

        elif '/open_video' in message.text and message.text.replace('/open_in_browser', '').replace(' ', '') != '':
            try:
                user_request = message.text.replace('/open_video', '').replace(' ', '', 1)

                await state.update_data(subject=user_request)
                await message.answer(f'Open {user_request} through browser (use existed pc browser):', reply_markup=kb.browser_choice_kb)

            except (Exception,):
                await state.update_data(subject=None)
                await message.answer('Something went wrong. Check yor input video name/url.')

        elif get_state.get('command_name') == '/open_video' and not message.text.lower().startswith('exit'):
            await state.update_data(subject=message.text)
            await message.answer(f'Open "{message.text}" through browser (use existed pc browser):', reply_markup=kb.browser_choice_kb)

    elif '/open_in_browser' in message.text or get_state.get('command_name') == '/open_in_browser':
        user_request = None

        if '/open_in_browser' in message.text and message.text.replace('/open_in_browser', '').replace(' ', '') == '':
            await state.update_data(command_name='/open_in_browser')
            await message.answer('Provide a request for browser searching:', reply_markup=kb.exit_keyboard)

        elif '/open_in_browser' in message.text and message.text.replace('/open_in_browser', '').replace(' ', '') != '':
            try:
                user_request = message.text.replace('/open_in_browser', '').split(' ', 1)

                if len(user_request) > 2:
                    raise Exception('Invalid arguments.')

                else:
                    user_request = user_request[1]
            except (Exception,):
                user_request = None
                await message.answer('Something went wrong. Check yor input request.')

        elif get_state.get('command_name') == '/open_in_browser' and not message.text.lower().startswith('exit'):
            user_request = message.text

        if user_request:
            open_app('chrome')
            pyautogui.hotkey('ctrl', 't')
            keyboard.write(user_request)
            keyboard.press('enter')
            await message.answer(f'{user_request.capitalize()} request was successfully opened.')

    elif '/screenshot' in message.text:
        try:
            ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

            image = ImageGrab.grab()
            np_img = np.array(image)

            img = cv2.cvtColor(np_img, cv2.COLOR_BGR2RGB)
            cv2.imwrite('screenshot.png', img)

            await state.update_data(subject='/screenshot')

            await message.answer('Choose quality of screenshot:', reply_markup=kb.image_quality_kb)

        except (Exception,):
            await message.answer('Something went wrong, try again.')

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

    elif '/key' in message.text or get_state.get('command_name') == '/key':
        if message.text.replace('/key', '').replace(' ', '') == '':
            await message.answer('Provide a values for keyboard writing (for exit type "Exit" or choose the command under):', reply_markup=kb.exit_keyboard)
            await state.update_data(command_name='/key')
        elif message.text.replace('/key', '').replace(' ', '') != '':
            await keyboard_write(message)
        elif get_state.get('command_name') == '/key':
            while message.text != 'exit':
                await keyboard_write(message)

    elif '/volume' in message.text:
        if message.text.replace('/volume', '').replace(' ', '') == '':
            file = types.FSInputFile('commands_images/volume_image.jpg')
            await message.answer_photo(photo=file)
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
            await state.update_data(command_name='No_command')

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

    elif message.text == '/download_video' or get_state.get('command_name') and '/download_video' in get_state.get('command_name'):
        if not get_state.get('command_name') or '/download_video' not in get_state.get('command_name'):
            await state.update_data(command_name='/download_video')
            await message.answer('Which video platform should we use:', reply_markup=kb.video_platform_kb)

        elif get_state.get('command_name') == '/download_video/video_platform_youtube' and message.text.lower() != 'exit':
            try:
                video_info = YouTube(message.text)
                await state.update_data(subject=message.text)
                await message.answer('All video quality and types. Choose one :', reply_markup=kb.youtube_video_kb(video_info))
            except (Exception,):
                await message.answer(f'Something went wrong, check yor input YouTube video url and try again.')

        elif get_state.get('command_name') == '/download_video/video_platform_tiktok' and message.text.lower() != 'exit':
            try:
                link = download_video_from_tiktok(message.text)

                if link and os.path.isfile('tiktok_video.mp4'):
                    file = types.FSInputFile('tiktok_video.mp4')
                    await message.answer_video(file, caption=f'Here is your video and extra link for downloading: {link}')
                    os.remove('tiktok_video.mp4')
                    await state.update_data(command_name='No_command')
                    await state.update_data(subject=None)

                elif link:
                    await message.answer(f'Downloading failed, here is your link for downloading: {link}')

                else:
                    raise Exception('Details: downloading failed')

            except (Exception,):
                await message.answer('Something went wrong, check yor input TikTok video url and try again.')

        elif get_state.get('command_name') == '/download_video/video_platform_instagram':
            try:
                link = download_from_inst(message.text)

                if link and os.path.isfile('inst_image.jpg') or os.path.isfile('insta_video.mp4'):
                    if os.path.isfile('inst_image.jpg'):
                        file = types.FSInputFile('inst_image.jpg')
                        await message.answer_photo(file, f'Here is photo video and extra link for downloading: {link}')
                        os.remove('inst_image.jpg')

                    elif os.path.isfile('inst_video.mp4'):
                        file = types.FSInputFile('inst_video.mp4')
                        await message.answer_video(file, f'Here is your video and extra link for downloading: {link}')
                        os.remove('inst_video.mp4')

                    elif link:
                        await message.answer(f'Downloading failed, here is your link for downloading: {link}')

                    else:
                        raise Exception('Details: downloading failed')

            except (Exception,):
                await message.answer('Something went wrong, check yor input Instagram url and try again.')
            await state.update_data(command_name='No_name')

        elif not message.text.lower() == 'exit':
            await message.answer('Unknown command for video downloading.')

    elif message.text == '/help':
        file = types.FSInputFile('commands_images/help_image.jpg')
        await message.answer_photo(photo=file)
        await message.answer(help_message)

    elif message.text == '/info':
        file = types.FSInputFile('commands_images/info_image.jpg')
        await message.answer_photo(photo=file)
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

    elif '/settings' in message.text:
        file = types.FSInputFile('commands_images/settings_image.jpg')
        await message.answer_photo(photo=file)
        await message.answer('---SETTINGS---')
        await message.answer(f'Language --> `{get_state.get("language")}`', reply_markup=kb.language_kb)
        await message.answer(f'Voice assistant --> `{get_state.get("voice_assistant")}`', reply_markup=kb.voice_assistant_kb)

    elif '/command_settings' in message.text:
        file = types.FSInputFile('commands_images/settings_image.jpg')
        await message.answer_photo(photo=file)
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

    elif '/test' in message.text:
        if message.text.replace('/test', '').replace(' ', '') == '':
            await message.answer('Provide a value.')
        else:
            open_app(message.text.replace('/test', '').replace(' ', ''))

    else:
        await message.answer('Sorry, didnt understand you, watch /help.')
