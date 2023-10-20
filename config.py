import os

import dotenv
from aiogram import Bot, Dispatcher

dotenv.load_dotenv()

TG_TOKEN = os.environ.get('TG_TOKEN')
BARD_TOKEN = os.environ.get('BARD_TOKEN')
OPENAI_TOKEN = os.environ.get('OPENAI_TOKEN')
OPENAI_TOKEN_ALYA = os.environ.get('OPENAI_TOKEN_ALYA')
telethon_api_id = os.environ.get('api_id')
telethon_api_hash = os.environ.get('api_hash')
ADMIN_ID = os.environ.get('ADMIN_ID')
TEST_ID = os.environ.get('TEST_ID')
OPEN_WEATHER_TOKEN = os.environ.get('OPEN_WEATHER_TOKEN')

phone_owner = os.environ.get('phone_owner')

bot = Bot(token=TG_TOKEN)
dp = Dispatcher(Bot=bot)

help_message = '''Here some commands to use:


<----------AI---------->
- /ai + prompt (Prompt request to AI).
- /img + prompt (Generate image with AI).

- Voice message (Commands:\n• /voice_ai (Voice request to AI);\n• /voice_transcription;).

- Photo message + command + optional prompt (Commands:\n• /image_ai + prompt;\n• /image_resize + "width"x"high";\n• /image_id.

- Video message (Commands:\n• /video_caption;\n• /video_resize + "width"x"high";\n• /video_id;\n• /video_mp3).


<----------Remote Control---------->
- /open_video + name/url (Find video in YouTube).
- /open_in_browser + prompt (Search info in browser).

- /screenshot + optional number quality (Qualities:\n• Nothing/1 (Screenshot with compression);\n• 2 (Screenshot in stock quality)).

- /open + app name (Open an app, should be global available).
- /close + app name (Close an app, should be global available).
- /key + hot key/keys (Remote keyboard input).
- /volume + optional value (Change value of volume, 0-100).


<----------Additional---------->
- /start (Start bot).
- /tech_support + query (Get in touch with our team).
- /weather + city (Get weather info to your city).
- /help (Watch list of all commands).
- /info (Useful info and F&Q).


<----------Settings---------->
- /settings (All settings).
- /command_settings (Settings by commands).
- /voice_ass (Switch voice assistant reply mode, default `OFF`).
- /lang (Switch input/output language, default `Ru`).
- /task_manager (Watch list of PC tasks).
- /id (Find out your id).'''


# client = telethon.TelegramClient('Owner_session', telethon_api_id, telethon_api_hash).start(bot_token=TG_TOKEN)
