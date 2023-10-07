import os

import dotenv
# import telethon
from aiogram import Bot, Dispatcher

dotenv.load_dotenv()

TG_TOKEN = os.environ.get('TG_TOKEN')
BARD_TOKEN = os.environ.get('BARD_TOKEN')
OPENAI_TOKEN = os.environ.get('OPENAI_TOKEN')
OPENAI_TOKEN_ALYA = os.environ.get('OPENAI_TOKEN_ALYA')
telethon_api_id = os.environ.get('api_id')
telethon_api_hash = os.environ.get('api_hash')
ADMIN_ID = os.environ.get('ADMIN_ID')

phone_owner = os.environ.get('phone_owner')

bot = Bot(token=TG_TOKEN)
dp = Dispatcher(Bot=bot)

# client = telethon.TelegramClient('Owner_session', telethon_api_id, telethon_api_hash).start(bot_token=TG_TOKEN)
